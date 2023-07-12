from flask import Flask, request
import functions_framework
from google.cloud import pubsub_v1
import logging
logging.basicConfig(level=logging.INFO)
import json
import os
import datetime
import requests

PROJECT_ID = os.environ.get('PROJECT_ID')

APP = Flask("internal")
EVENT_BUS = os.environ["EVENT_BUS"]
ENTITY = ""
#with open("command.json") as fs:
#    ARGS_DEFINITION = json.load("commands.json")
ARGS_DEFINITION = {}

def publish_message(author:str, operation:str, entityId:str, payload:str):
    """
    This function publishes the message.
    Parameters:
        conversation_id: The ID of the conversation
        author: Who is publishing the message (user_id)
        message: The message to publish
    """
    message = {
        "author": author,
        "entity": ENTITY,
        "entityId": entityId,
        "operation": operation,
        "timestamp": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "payload": payload
    }
    message_json = json.dumps(message).encode("utf-8")
    print("Publishing ", message_json)
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(PROJECT_ID, EVENT_BUS)
    publish_future = publisher.publish(topic_path,
                                        data=message_json)
    publish_future.result()

@APP.route('/', methods=['GET', 'POST'])
def unknown_operation():
    response = APP.response_class(
        response="Incomplete path, please select an operation",
        status=400,
        mimetype='text/plain')
    return response


@APP.route('/send_email', methods=['POST', ])
def send_email_zap():
    logging.info("Received request to trigger an email zap: {}".format(request))
    request_json = json.loads(request.data)
    # Ensure zap_url for the email zap is either passed in or set as an environment variable
    zap_url = request_json.get('zap_url', os.environ.get('EMAIL_ZAP_URL'))
    # Prepare the payload. This will depend on how you've set up your zap.
    # You'll want to extract the necessary information from the request data.
    payload = {
        "email": request_json['email'],
        "subject": request_json['subject'],
        "body": request_json['body'],
    }
    response = requests.post(zap_url, data=json.dumps(payload), headers={'Content-Type': 'application/json'})

    if response.status_code == 200:
        status_message = 'Email Zap action triggered successfully'
    else:
        status_message = 'Failed to trigger Email Zap action'

    response = APP.response_class(
        response=json.dumps({"payload": payload, "responseMessage": status_message}),
        status=response.status_code,
        mimetype='application/json') 
    return response

    
@functions_framework.http
def entity_commands(request):
    internal_ctx = APP.test_request_context(path=request.full_path,
                                            method=request.method)
    internal_ctx.request.data = request.data
    internal_ctx.request.headers = request.headers
    internal_ctx.request.args = request.args
    
    APP.config['PRESERVE_CONTEXT_ON_EXCEPTION']=False
    
    return_value = APP.response_class(
        response="Invalid Request", 
        status=400,
        mimetype='text/plain')
    
    try:
        internal_ctx.push()
        return_value = APP.full_dispatch_request()
        logging.info("Request processed: {}".format(return_value))
        internal_ctx.pop()
    except Exception as e:
        logging.error(e)
    return return_value