import os
import logging
logging.basicConfig(level=logging.INFO)
import json
import firebase_admin
from firebase_admin import firestore
import functions_framework
from typing import Dict
import base64

PROJECT_ID = os.environ.get('PROJECT_ID')
EVENT_BUS = os.environ.get('EVENT_BUS')
ENTITY = ""
APP = firebase_admin.initialize_app()

def _create_entity(entity_id:str, payload:Dict):
    logging.info("Created")

def _delete_entity(entity_id:str):
    logging.info("Deleted")

# Triggered from a message on a Cloud Pub/Sub topic.
@functions_framework.cloud_event
def user_manager(cloud_event):
    event = json.loads(base64.b64decode(cloud_event.data["message"]["data"]).decode())
    if event['entity']==ENTITY:
        payload = json.loads(event['payload'])
        if event['operation']=="delete":
            _delete_entity(user_id=event['entityId'])
        elif event['operation']=="create":
            _create_entity(user_id=event['entityId'], payload=json.loads(event["payload"]))