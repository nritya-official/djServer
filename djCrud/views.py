from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt  
from djApi.flags import FIREBASE_DB, COLLECTIONS, nSuccessCodes, CELERY_APP, NOTIFICATION
from google.cloud.firestore_v1.base_query import FieldFilter, Or
import json
import logging
import firebase_admin.firestore
import threading
import time
from django.urls import reverse
from django.http import HttpResponse
from django.template import loader
import base64
import os
import logging

logger = logging.getLogger(__name__)

def crudTest(request):
    logging.info("Hello")
    return JsonResponse({'message': 'This is the crud endpoint.'})

def send_notification_emails(collection_name, emails, operation_type, entity_id):
    task = {
        "type" : NOTIFICATION.TYPE_CRUD ,
        "collection_name" : collection_name,
        "emails" : emails,
        "operation_type" : operation_type,
        "entity_id" : entity_id
    }
    CELERY_APP.send_task('tasks.process_email_task', args=[task])

@csrf_exempt
def newEntity(request):
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            data = body.get('data')
            collection_name = body.get('collection_name')
            emails = body.get('notify', '')

            # Add the document to Firestore
            collection_ref = FIREBASE_DB.collection(collection_name)
            update_time, collection_ref = collection_ref.add(data)

            if emails:
                send_notification_emails(collection_name, emails, NOTIFICATION.OP_CREATE, collection_ref.id)
                logger.info(collection_ref.id)
            return JsonResponse({'status': 'success', 'message': 'Entity added successfully', 'id': collection_ref.id}, status=201)

        except Exception as e:
            logger.error(f"Error occurred: {str(e)}")  
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


