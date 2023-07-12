from flask import Flask, request
import functions_framework
from google.cloud import pubsub_v1
import logging
logging.basicConfig(level=logging.INFO)
import json
import os
import datetime

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

#@APP.route('/create', methods=['POST', ])
#def create_entity():
#    logging.info("Received request to create entity: {}".format(request))
#    request_json = json.loads(request.data)
#    author = request_json['author']
#    publish_message(author=author, entityId=entity_id, operation="create",
#                    payload=json.dumps({"mandatory_keys": "mandatory_values",
#                                        **{key: request_json[key] for key in request_json.keys() if key not in ARGS_DEFINITION["create-user"]["args"].keys()}}))
#    response = APP.response_class(
#        response=json.dumps({"payload":{}, "responseMessage":"Created entity {id}".format(id=entity_id)}),
#        status=200,
#        mimetype='application/json') 
#    return response
    
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