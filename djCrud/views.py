from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt  
from djApi.flags import FIREBASE_DB, CELERY_APP
from utils.common_utils import is_valid_entity_type, extract_user_id, COLLECTIONS, NOTIFICATION, nSuccessCodes
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

def send_notification_emails(collection_name, emails, operation_type, entity_id, metadata):
    task = {
        "type" : NOTIFICATION.TYPE_CRUD ,
        "collection_name" : collection_name,
        "emails" : emails,
        "operation_type" : operation_type,
        "entity_id" : entity_id,
        "metadata" : metadata
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
            metadata = body.get('metadata', '')
            
            # Validate entity type
            if not is_valid_entity_type(collection_name):
                return JsonResponse({'Error': 'Entity Type not found.'}, status=nSuccessCodes.NOT_FOUND)

            # Handle entity creation
            operation_type, entity_created_key, collection_ref = handle_entity_creation(collection_name, data)

            if collection_name == COLLECTIONS.USER:
                return create_user_entity(collection_name, data)

            # Process user creation for other entity types
            user_id = extract_user_id(request)
            if user_id:
                user_ref, user_data = get_user_data(user_id)
                if user_data is None:
                    return JsonResponse({'status': 'error', 'message': "User not found."}, status=nSuccessCodes.NOT_FOUND)
                logging.info(user_data)
                if not user_data.get('CreatorMode', False):
                    return JsonResponse({'status': 'error', 'message': "User not a creator."}, status=nSuccessCodes.FORBIDDEN)

                collection_ref = FIREBASE_DB.collection(collection_name)
                update_time, collection_ref = collection_ref.add(data)
                update_user_entity_created(user_ref, entity_created_key, collection_ref.id, user_data)

            else:
                return JsonResponse({'status': 'error', 'message': "Please log in again."}, status=nSuccessCodes.UNAUTHORIZED)

            # Send notifications if required
            if emails and operation_type and collection_ref.id:
                send_notification_emails(collection_name, emails, operation_type, collection_ref.id, metadata)
                logger.info(collection_ref.id)

            return JsonResponse({'status': 'success', 'message': 'Entity added successfully', 'id': collection_ref.id}, status=nSuccessCodes.CREATED)

        except Exception as e:
            logger.error(f"Error occurred: {str(e)}")  
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

def handle_entity_creation(collection_name, data):
    """Handles the logic for determining operation type and entity creation key."""
    operation_type = None
    entity_created_key = None
    collection_ref = None

    if collection_name == COLLECTIONS.STUDIO:
        operation_type = NOTIFICATION.OP_CREATE_STUDIO
        entity_created_key = "StudioCreated"
    elif collection_name == COLLECTIONS.COURSES:
        operation_type = NOTIFICATION.OP_CREATE
        entity_created_key = "CourseCreated"
    elif collection_name == COLLECTIONS.OPENCLASSES:
        operation_type = NOTIFICATION.OP_CREATE
        entity_created_key = "OpenClassCreated"
    elif collection_name == COLLECTIONS.WORKSHOPS:
        operation_type = NOTIFICATION.OP_CREATE
        entity_created_key = "WorkshopCreated"
    elif collection_name == COLLECTIONS.INSTRUCTORS:
        operation_type = NOTIFICATION.OP_CREATE

    return operation_type, entity_created_key, collection_ref

def create_user_entity(collection_name, data):
    """Creates a new user entity and returns the response."""
    collection_ref = FIREBASE_DB.collection(collection_name)
    update_time, collection_ref = collection_ref.add(data)
    return JsonResponse({'status': 'success', 'message': 'Entity added successfully', 'id': collection_ref.id}, status=nSuccessCodes.CREATED)

def get_user_data(user_id):
    """Retrieves user data from Firebase."""
    user_ref = FIREBASE_DB.collection(COLLECTIONS.USER).document(user_id)
    user_snap = user_ref.get()
    if user_snap.exists:
        return user_ref, user_snap.to_dict()
    return user_ref, None

def update_user_entity_created(user_ref, entity_created_key, collection_id, user_data):
    """Updates the user's entity created list."""
    if entity_created_key:
        entity_created = user_data.get(entity_created_key, [])
        entity_created.append(collection_id)
        user_ref.set({entity_created_key: entity_created}, merge=True)











def newEntity2(request):
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            data = body.get('data')
            collection_name = body.get('collection_name')
            emails = body.get('notify', '')
            metadata = body.get('metadata', '')
            operation_type = None
            entity_created_key = None
            collection_ref = None

            if not is_valid_entity_type(collection_name):
                JsonResponse({'Error': 'Entity Type not found.'}, status=nSuccessCodes.NOT_FOUND)

            if collection_name == COLLECTIONS.STUDIO:
                operation_type = NOTIFICATION.OP_CREATE_STUDIO
                entity_created_key = "StudioCreated"

            elif collection_name == COLLECTIONS.COURSES:
                operation_type = NOTIFICATION.OP_CREATE
                entity_created_key = "CourseCreated"

            elif collection_name == COLLECTIONS.OPENCLASSES:
                operation_type = NOTIFICATION.OP_CREATE
                entity_created_key = "OpenClassCreated"

            elif collection_name == COLLECTIONS.WORKSHOPS:
                operation_type = NOTIFICATION.OP_CREATE
                entity_created_key = "WorkshopCreated"

            elif collection_name == COLLECTIONS.INSTRUCTORS:
                operation_type = NOTIFICATION.OP_CREATE

            elif collection_name == COLLECTIONS.USER :
                operation_type = NOTIFICATION.OP_SIGN_UP
                collection_ref = FIREBASE_DB.collection(collection_name)
                update_time, collection_ref = collection_ref.add(data)
                return JsonResponse({'status': 'success', 'message': 'Entity added successfully', 'id': collection_ref.id}, status=nSuccessCodes.CREATED)

            # User trying to create some entity
            if collection_name in [COLLECTIONS.STUDIO, COLLECTIONS.COURSES, COLLECTIONS.OPENCLASSES, COLLECTIONS.WORKSHOPS, COLLECTIONS.INSTRUCTORS]:
                user_id = extract_user_id(request)
                # User exists
                if(user_id):
                    user_ref = FIREBASE_DB.collection(COLLECTIONS.USER).document(user_id)
                    user_snap = user_ref.get()
                    if user_snap.exists:
                        user_data = user_snap.to_dict() or {}
                        isCreator = user_data.get(CreatorMode,False)
                        # User is not a creator
                        if not isCreator:
                            return JsonResponse({'status': 'error', 'message': "User not a creator."}, status=nSuccessCodes.FORBIDDEN)
                        # User is a creator
                        collection_ref = FIREBASE_DB.collection(collection_name)
                        update_time, collection_ref = collection_ref.add(data)
                        # Non instructor entity created
                        if entity_created_key:
                            entity_created = user_data.get(entity_created_key, [])
                            entity_created.append(collection_ref.id)
                            user_ref.set({entity_created_key: entity_created}, merge=True)
                    else:
                        return JsonResponse({'status': 'error', 'message': "User not found."}, status=nSuccessCodes.NOT_FOUND)
                # User does not exists
                else:
                    return JsonResponse({'status': 'error', 'message': "Please log in again."}, status=nSuccessCodes.UNAUTHORIZED)

            
            if emails and operation_type and collection_name and collection_ref.id:
                send_notification_emails(collection_name, emails, operation_type, collection_ref.id, metadata)
                logger.info(collection_ref.id)

            return JsonResponse({'status': 'success', 'message': 'Entity added successfully', 'id': collection_ref.id}, status=nSuccessCodes.CREATED)

        except Exception as e:
            logger.error(f"Error occurred: {str(e)}")  
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)