# djBookings/views.py
from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt  
from djApi.flags import FIREBASE_DB
from utils.common_utils import is_valid_entity_type, COLLECTIONS, nSuccessCodes
from utils.redis_client import RedisClient
from google.cloud.firestore_v1.base_query import FieldFilter, Or
from .flags import FLAGS
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
from django.shortcuts import render, redirect
from rest_framework.decorators import api_view
import random
import string

def generate_ticket_id(length=7):
    characters = string.ascii_uppercase + string.digits  # A-Z and 0-9
    return ''.join(random.choices(characters, k=length))

def bookingsTest(request):
    logging.info("Hello")
    return JsonResponse({'message': 'This is the bookings endpoint.'})


def _get_user_info(user_id):
    logging.info(f'Getting User info for {user_id}')
    user_ref = FIREBASE_DB.collection(COLLECTIONS.USER).document(user_id)
    user_doc = user_ref.get()
    logging.info('Got user doc')
    if user_doc.exists:
        user_map = user_doc.to_dict()
        name_learner = user_map.get('Name', '')
        email_learner = user_map.get('Email', '')
        logging.info(f"User Document data: {name_learner} {email_learner}")
    else:
        logging.info("No such document of User!")

def _get_studio_info(studio_id, classIndex):
    logging.info(f'Getting Studio info for {studio_id}')
    studio_ref = FIREBASE_DB.collection(COLLECTIONS.STUDIO).document(studio_id)
    studio_doc = studio_ref.get()
    logging.info('Got studio doc')
    if studio_doc.exists:
        studio_map = studio_doc.to_dict()
        name_studio = studio_map.get('studioName', '')
        email_studio = studio_map.get('mailAddress', '')
        name_class = studio_map.get('tableData').get(str(classIndex)).get('className')
        logging.info(f"Studio Document data: {name_studio} {email_studio} {name_class}")
    else:
        logging.info("No such document of studio!")

@api_view(['GET'])
def availFreeTrial(request,booking_id):
    logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logo.png')
    with open(logo_path, 'rb') as image_file:
        encoded_string_logo = base64.b64encode(image_file.read()).decode('utf-8')

    return render(request, 'input_form_free_trial.html', {'booking_id': booking_id,'encoded_string_logo':encoded_string_logo})

@api_view(['POST'])
def availFreeTrialResults(request):
    booking_id = request.POST.get('booking_id')
    passcode_value = request.POST.get('input_field')
    passcode_value = passcode_value.strip()
    logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logo.png')
    with open(logo_path, 'rb') as image_file:
        encoded_string_logo = base64.b64encode(image_file.read()).decode('utf-8')

    if(not passcode_value.isdigit() or int(passcode_value)<999 or int(passcode_value) != 8311):
        if int(passcode_value) == -1:
            return render(request,'passcode_wrong.html', {'message': 'Timed out','encoded_string_logo':encoded_string_logo })
        return render(request,'passcode_wrong.html', {'message': f'Passcode incorrect {passcode_value}','encoded_string_logo':encoded_string_logo })

    logging.info(f"Free Trial {booking_id}")
    db = FIREBASE_DB
    doc_ref = db.collection(COLLECTIONS.FREE_TRIAL_BOOKINGS).document(str(booking_id))
   

    doc = doc_ref.get()
    if doc.exists:
        booking_data = doc.to_dict()
        logging.info(f"Booking exists data: {doc.to_dict()}")
        logging.info(booking_data['studio_id'])
        # Check if validated already
        if 'used' in booking_data and booking_data['used']:
            return render(request, 'case4a.html', {'booking_id': booking_id,'encoded_string_logo':encoded_string_logo ,'status': 'Valid Booking but Already used'})
            #return JsonResponse({'Booking Id': booking_id, 'Status': 'Valid Booking but Already used'})

        # Check if expired (assuming you have a 'expiry_date' field in your data)
        if 'timestamp' in booking_data:
            expiration_time = (float(booking_data['timestamp']) + FLAGS.EXPIRES_WITHIN_DAYS*FLAGS.DAYS_TO_SEC)
            logging.info(expiration_time)
            logging.info(time.time())
            if expiration_time < time.time():
                return render(request, 'case3a.html', {'booking_id': booking_id,'encoded_string_logo':encoded_string_logo ,'status': 'Valid booking but Expired'})
                #return JsonResponse({'Booking Id': booking_id, 'Status': 'Valid booking but Expired'})
            doc_ref.set({"used": True,"used_at":time.time()}, merge=True)
            return render(request, 'case1a.html', {'booking_id': booking_id,'encoded_string_logo':encoded_string_logo ,'status': 'Valid Booking Id'})
            #return JsonResponse({'Booking Id': booking_id, 'Status': 'Valid Booking, Enjoy your free class now.'})

    else:
        logging.info("No such bookings")
        return render(request, 'case2a.html', {'booking_id': booking_id,'encoded_string_logo':encoded_string_logo ,'status': 'Invalid Booking Id'})
        #return render(request, 'case2a.html', {'booking_id': booking_id, 'status': 'Invalid Booking Id'})  /home/ayush/Downloads/FreeTrialCases
        #return JsonResponse({'Booking Id': booking_id,'Status':'Invalid Booking Id'}) #invalid

@api_view(['POST'])
@csrf_exempt
def freeTrial(request):
    logging.info("Free Trial")
    db = FIREBASE_DB
    name_studio = name_class = name_learner = studio_address = booked = email_studio = email_learner = ""
    if request.method == 'POST':
        # Handle the POST request for the free trial
        logging.info("Free trial request received.")
        logging.info(request.body)
        try:
            request_data = json.loads(request.body.decode('utf-8'))
            user_id, studio_id = "",""
            user_id = request_data.get('userId')
            studio_id = request_data.get('studioId')
            class_index = request_data.get('classIndex')

            logging.info(user_id+" "+studio_id)
            if user_id != "" and studio_id != "":

                free_trial_bookings_ref = db.collection(COLLECTIONS.FREE_TRIAL_BOOKINGS)
                validation_query_results =   free_trial_bookings_ref.where(
                    filter=FieldFilter("user_id", "==", user_id)
                    ).where(filter=FieldFilter("studio_id", "==", studio_id)
                    ).where(filter=FieldFilter("class_index", "==", class_index)).stream()
                
                logging.info(validation_query_results)
        
                # Check if the result set is non-empty
                first_document = None
                for doc in validation_query_results:
                    first_document = doc.to_dict()
                    logging.info(doc.exists)
                    logging.info(doc.id)
                    first_document["id"] = doc.id
                    break
                if first_document:
                    booked_at = first_document.get('timestamp', None)  
                    if booked_at is not None:
                        return JsonResponse({
                            'Booking Id': first_document['id'],
                            'nSuccessCode': nSuccessCodes.ALREADY_BOOKED,
                            'bookedAt': booked_at
                        })
                    else:
                        return JsonResponse({'Error': 'bookedAt not found in document'}, status=nSuccessCodes.NOT_FOUND)

                #logging.info("Both IDs are there")
                user_ref = db.collection(COLLECTIONS.USER).document(user_id)
                #logging.info("Got User_ref")
                studio_ref = db.collection(COLLECTIONS.STUDIO).document(studio_id)
                #logging.info("Got studio_ref")
                user_doc = user_ref.get()
                #logging.info("Got user_doc")
                #logging.info(user_id+" "+studio_id)
                if user_doc.exists:
                    user_map = user_doc.to_dict()
                    name_learner = user_map['Name']
                    email_learner = user_map['Email']
                    
                else:
                    logging.info("No such document of User!")
                
                studio_doc = studio_ref.get()
                if studio_doc.exists:
                    studio_map = studio_doc.to_dict()
                    name_studio = studio_map['studioName']
                    email_studio = studio_map['mailAddress']
                    studio_address = studio_map['street'] +", " +studio_map['city']
                    name_class = studio_map['tableData'][str(class_index)]['className']
                    data = {"name_studio": name_studio, "name_class": name_class, "name_learner": name_learner,
                            "studio_address":studio_address,"email_studio":email_studio,"email_learner":email_learner,
                            'user_id':user_id,'studio_id':studio_id,'class_index':class_index,'timestamp':time.time()}
                    booking_time,booking_ref = free_trial_bookings_ref.add(data)
                    return JsonResponse({'Booking Id': booking_ref.id,'nSuccessCode':nSuccessCodes.CREATED,'Booked At':data['timestamp']})

                else:
                    logging.info("No such document of studio!")
                
                logging.info(
                    f"{user_id} {email_learner} {name_learner} {name_studio} {email_studio} {str(name_class)}"
                )
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding JSON: {e}")
        return JsonResponse({'message': 'This is the free trial bookings endpoint.'})
    else:
        logging.info(request.method)
        return JsonResponse("This is the free trial endpoint. Send a POST request to start the free trial.",safe=False)

@api_view(['POST'])
@csrf_exempt
def bookEntity(request):
    logging.info("Book entity")
    db = FIREBASE_DB
    entity_type = entity_id= associated_studio_id=  email_learner=persons_allowed= price_per_person= timestamp= user_id = ""
    logging.info(json.loads(request.body.decode('utf-8')))
    if request.method == 'POST':
        try:
            request_data = json.loads(request.body.decode('utf-8'))
            user_id = request_data.get('userId')
            entity_type = request_data.get('entityType')
            entity_id = request_data.get('entityId')
            associated_studio_id = request_data.get('associatedStudioId')
            email_learner = request_data.get('emailLearner')
            persons_allowed = request_data.get('personsAllowed')
            price_per_person = request_data.get('pricePerPerson')

            if not is_valid_entity_type(entity_type):
                JsonResponse({'Error': 'Entity Type not found.'}, status=nSuccessCodes.NOT_FOUND)

            bookings_ref = db.collection(COLLECTIONS.BOOKINGS)
            validation_query_results =   bookings_ref.where(
                    filter=FieldFilter("user_id", "==", user_id)
                    ).where(filter=FieldFilter("entity_id", "==", entity_id)
                    ).stream()

            first_document = None
            for doc in validation_query_results:
                first_document = doc.to_dict()
                first_document["id"] = doc.id
                break
            if first_document:
                booked_at = first_document.get('timestamp', None)  
                if booked_at is not None:
                    return JsonResponse({
                        'Booking Id': first_document['id'],
                        'nSuccessCode': nSuccessCodes.ALREADY_BOOKED,
                        'bookedAt': booked_at
                    })
                else:
                    return JsonResponse({'Error': 'bookedAt not found in document'}, status=nSuccessCodes.NOT_FOUND)
     
            timestamp = time.time()
            new_booking = {
                'user_id': user_id,
                'entity_type': entity_type,
                'entity_id': entity_id,
                'associated_studio_id': associated_studio_id,
                'email_learner': email_learner,
                'persons_allowed': persons_allowed,
                'price_per_person': price_per_person,
                'timestamp': timestamp
            }
            ticket_id = RedisClient.get_next_ticket_id()
            bookings_ref.document(ticket_id).set(new_booking)
            max_retries = 7  # Maximum number of retries
            for attempt in range(max_retries):
                ticket_id = generate_ticket_id()
                doc_ref = FIREBASE_DB.collection(BOOKINGS).document(ticket_id)
                doc = doc_ref.get()

                if not doc.exists::  
                    bookings_ref.document(ticket_id).set(new_booking)
                    return ticket_id  
            raise Exception("Failed to generate a unique ticket ID after 7 attempts.")

            return JsonResponse({
                'nSuccessCode': nSuccessCodes.BOOKING_SUCCESS,
                'message': 'Booking added successfully'
            })

        except Exception as e:
            logging.error(f"Error booking entity: {str(e)}")
            return JsonResponse({'Error': str(e)}, status= nSuccessCodes.INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@csrf_exempt
def getUserBookings(request, user_id):
    logging.info("Get entity bookings")

    if request.method == 'GET':
        try:
            db = FIREBASE_DB
            months = 1

            time_filter = time.time() - months * 30 * 24 * 60 * 60  # Past 30 days (optional)

            def get_name(collection_name, doc_id):
                doc_ref = FIREBASE_DB.collection(collection_name).document(doc_id)
                doc = doc_ref.get()
                if doc.exists:
                    mp = doc.to_dict()
                    return (mp.get("workshopName") or mp.get("studioName") or mp.get("openClassName") or mp.get("studioName"))

            # Define sync fetch function
            def fetch_bookings(collection):
                docs = collection.where(filter=FieldFilter("user_id", "==", user_id)).where(filter=FieldFilter("timestamp", ">", time_filter)).stream()
                result = {}
                
                for doc in docs:
                    try:
                        uuid = doc.id
                        if uuid:
                            result[uuid] = doc.to_dict()
                            logging.info(uuid)
                    except AttributeError as e:
                        logging.info("Error accessing doc.id: %s", str(e))

                return result
                
            logging.info("Get entity bookings")

            bookings_ref = FIREBASE_DB.collection(COLLECTIONS.BOOKINGS)
            free_trial_bookings_ref = FIREBASE_DB.collection(COLLECTIONS.FREE_TRIAL_BOOKINGS)

            bookings_results = fetch_bookings(bookings_ref)
            free_trial_results = fetch_bookings(free_trial_bookings_ref)

            categorized_bookings = {
                COLLECTIONS.FREE_TRIAL_BOOKINGS: free_trial_results,  # Free trial bookings
                COLLECTIONS.WORKSHOPS: {},
                COLLECTIONS.OPENCLASSES: {},
                COLLECTIONS.COURSES: {},
            }
            logging.info(bookings_results)
            for booking_id, booking_data in bookings_results.items():
                entity_type = booking_data['entity_type']
                entity_id = booking_data['entity_id']
                associated_studio_id = booking_data['associated_studio_id']
                # Categorize based on entity_type
                if entity_type == 'Workshops':
                    booking_data["entity_name"] = get_name(COLLECTIONS.WORKSHOPS,entity_id)
                    booking_data["studio_name"] = get_name(COLLECTIONS.STUDIO,associated_studio_id)
                    categorized_bookings[COLLECTIONS.WORKSHOPS][booking_id] = booking_data
                elif entity_type == 'OpenClasses':
                    booking_data["entity_name"] = get_name(COLLECTIONS.OPENCLASSES,entity_id)
                    booking_data["studio_name"] = get_name(COLLECTIONS.STUDIO,associated_studio_id)
                    categorized_bookings[COLLECTIONS.OPENCLASSES][booking_id] = booking_data
                elif entity_type == 'Courses':
                    booking_data["entity_name"] = get_name(COLLECTIONS.COURSES,entity_id)
                    booking_data["studio_name"] = get_name(COLLECTIONS.STUDIO,associated_studio_id)
                    categorized_bookings[COLLECTIONS.COURSES][booking_id] = booking_data

                    # Optionally handle unexpected entity types if necessary
                    logging.warning(f"Unexpected entity_type: {entity_type}")
            return JsonResponse({
                'nSuccessCode': nSuccessCodes.SUCCESS,
                'message': 'Bookings retrieved successfully',
                'data': categorized_bookings
            })

        except Exception as e:
            logging.error(f"Error getting bookings: {str(e)}")
            return JsonResponse({'Error': str(e)}, status=nSuccessCodes.INTERNAL_SERVER_ERROR)
