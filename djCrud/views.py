from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt  
from utils.flags import FIREBASE_DB, CELERY_APP
from utils.env_loader import base_web_url
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

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s - Line: %(lineno)d',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def testEndpoint(request):
    logging.info("Hello from djCrud")
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
    logger.info(f'send_notification_emails task {task}')
    CELERY_APP.send_task('tasks.process_email_task', args=[task])


@csrf_exempt
def updateEntity(request, entity_id):
    if request.method == 'PUT':
        try:
            body = json.loads(request.body)
            data = body.get('data')
            collection_name = body.get('collection_name')
            #emails = body.get('notify', '')
            #metadata = body.get('metadata', '')
            logger.info(f'entity_id {entity_id}')
            logger.info(f'body {body}')
            # Validate entity type
            if not is_valid_entity_type(collection_name):
                return JsonResponse({'Error': 'Entity Type not found.'}, status=nSuccessCodes.NOT_FOUND)

            # Process user creation for other entity types
            user_id = extract_user_id(request)
            if user_id:
                user_ref, user_data = get_user_data(user_id)
                if user_data is None:
                    return JsonResponse({'status': 'error', 'message': "User not found."}, status=nSuccessCodes.NOT_FOUND)
                if not user_data.get('CreatorMode', False):
                    return JsonResponse({'status': 'error', 'message': "User not a creator."}, status=nSuccessCodes.FORBIDDEN)

                collection_ref = FIREBASE_DB.collection(collection_name).document(entity_id)
                collection_ref.set(data, merge=True)

            else:
                return JsonResponse({'status': 'error', 'message': "Please log in again."}, status=nSuccessCodes.UNAUTHORIZED)

            return JsonResponse({'status': 'success', 'message': 'Entity added successfully', 'id': collection_ref.id}, status=nSuccessCodes.CREATED)

        except Exception as e:
            logger.error(f"Error occurred: {str(e)}")  
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

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
                return create_user_entity(collection_name, operation_type, data, emails, metadata)

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

                # Prepare data for email notification over redis-celery
                base_url = base_web_url()
                user_name = user_data.get('Name', None)
                metadata['user_name'] = user_name if user_name else metadata.get('user_name')
                studio_id = None
                entity_url = None
                studio_name = None
                studio_street_name = None
                studio_city_name = None

                if collection_name == COLLECTIONS.STUDIO:
                    # Studio Details
                    studio_street_name = data.get('street',None)
                    studio_city_name = data.get('city',None)
                    studio_name = data.get('studioName',None)
                    studio_id = collection_ref.id
                    entity_url = f"{base_url}/#/studio/{studio_id}"

                    metadata.update({
                        'studio_street_name': studio_street_name,
                        'studio_city_name': studio_city_name,
                        'studio_name': studio_name,
                        'studio_id': studio_id,
                        'entity_url': entity_url,
                    })
                
                elif collection_name in [COLLECTIONS.WORKSHOPS, COLLECTIONS.OPENCLASSES, COLLECTIONS.COURSES]:
                    entity_id = collection_ref.id
                    studio_id = data.get('StudioId',None)

                    studio_ref, studio_data = get_entity_data(studio_id)
                    if studio_data:
                        studio_street_name = studio_data.get('street',None)
                        studio_city_name = studio_data.get('city',None)
                        studio_name = studio_data.get('studioName',None)

                    if collection_name == COLLECTIONS.WORKSHOPS: 
                        entity_name = data.get('workshopName',None)
                        entity_url = f"{base_url}/#/workshop/{entity_id}"
                    elif collection_name == COLLECTIONS.OPENCLASSES:
                        entity_name = data.get('openClassName',None)
                        entity_url = f"{base_url}/#/openClass/{entity_id}"
                    elif collection_name == COLLECTIONS.COURSES:
                        entity_name = data.get('courseName',None)
                        entity_url = f"{base_url}/#/course/{entity_id}"
                    
                    metadata.update({
                        'studio_street_name': studio_street_name,
                        'studio_city_name': studio_city_name,
                        'studio_name': studio_name,
                        'studio_id': studio_id,
                        'entity_url': entity_url,
                        'entity_id': entity_id,
                        'entity_name': entity_name
                    })

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
        operation_type = NOTIFICATION.OP_CREATE
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
    elif collection_name == COLLECTIONS.USER:
        operation_type = NOTIFICATION.OP_SIGN_UP

    return operation_type, entity_created_key, collection_ref

def create_user_entity(collection_name, operation_type, data, emails, metadata):
    """Creates a new user entity and returns the response."""
    user_id = metadata.get('user_id',None)
    user_name = data.get('Name', None)
    if user_name:
        metadata['user_name'] = user_name
    collection_ref = FIREBASE_DB.collection(collection_name).document(user_id)
    if emails and is_valid_entity_type(collection_name) and collection_ref and user_id:
        collection_ref.set(data)
        logger.info(f'create_user_entity collection_name {collection_name}, emails {emails},operation_type {operation_type} ,User Id {user_id},metadata {metadata}')
        send_notification_emails(collection_name, emails, operation_type , collection_ref.id, metadata)
        return JsonResponse({'status': 'success', 'message': 'Entity added successfully', 'id': collection_ref.id}, status=nSuccessCodes.CREATED)
    else:
        return JsonResponse({'status': 'success', 'message': 'Failure no proper gmail.'}, status=nSuccessCodes.FAILURE)

def get_user_data(user_id):
    """Retrieves user data from Firebase."""
    user_ref = FIREBASE_DB.collection(COLLECTIONS.USER).document(user_id)
    user_snap = user_ref.get()
    if user_snap.exists:
        return user_ref, user_snap.to_dict()
    return user_ref, None

def get_entity_data(entity_id, collection_name = COLLECTIONS.STUDIO):
    """Retrieves entity data from Firebase."""
    entity_ref = FIREBASE_DB.collection(collection_name).document(entity_id)
    entity_snap = entity_ref.get()
    if entity_snap.exists:
        return entity_ref, entity.to_dict()
    return entity_ref, None

def update_user_entity_created(user_ref, entity_created_key, collection_id, user_data):
    """Updates the user's entity created list."""
    if entity_created_key:
        entity_created = user_data.get(entity_created_key, [])
        entity_created.append(collection_id)
        user_ref.set({entity_created_key: entity_created}, merge=True)
