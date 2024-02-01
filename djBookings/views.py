# djBookings/views.py
from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt  
from djApi.flags import FIREBASE_DB, COLLECTIONS, nSuccessCodes
#from sendEmailServices.email_main import send_emails
from google.cloud.firestore_v1.base_query import FieldFilter, Or
import json
import logging
import firebase_admin.firestore
import threading
import time
from django.urls import reverse

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

@csrf_exempt
def freeTrial2(request):
    logging.info("Free Trial")
    name_studio = name_class = name_learner = studio_address = booked = email_studio = email_learner = ""

    if request.method == 'POST':
        logging.info("Free trial request received.")
        logging.info(request.body)

        try:
            request_data = json.loads(request.body.decode('utf-8'))
            user_id = request_data.get('userId')
            studio_id = request_data.get('studioId')
            classIndex = request_data.get('classIndex')

            if user_id and studio_id and classIndex:
                # if Trial/studio_id/user_id/classIndex trialDone:
                #   return JsonResponse({'type':'TrialDone',message:'You have already availed trial for this'})
                user_thread = threading.Thread(target=_get_user_info, args=(user_id,))
                studio_thread = threading.Thread(target=_get_studio_info, args=(studio_id, classIndex))
                user_thread.start()
                studio_thread.start()
                user_thread.join()
                studio_thread.join()

        except json.JSONDecodeError as e:
            logging.error(f"Error decoding JSON: {e}")

        return JsonResponse({'message': 'This is the free trial bookings endpoint.'})
    else:
        logging.info(request.method)
        return JsonResponse("This is the free trial endpoint. Send a POST request to start the free trial.", safe=False)


@csrf_exempt
def freeTrial3(request):
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
            classIndex = request_data.get('classIndex')
            logging.info(user_id+" "+studio_id)
            if user_id != "" and studio_id != "":
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
                    name_class = studio_map['tableData'][str(classIndex)]['className']
                    send_emails(name_studio,name_learner,name_class,email_learner,email_studio)
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


def availFreeTrial(request,booking_id):
    logging.info(f"Free Trial {booking_id}")
    db = FIREBASE_DB
    doc_ref = db.collection(COLLECTIONS.FREE_TRIAL_BOOKINGS).document(str(booking_id))

    doc = doc_ref.get()
    if doc.exists:
        booking_data = doc.to_dict()
        logging.info(f"Booking exists data: {doc.to_dict()}")
        # Check if validated already
        if 'used' in booking_data and booking_data['used']:
            return JsonResponse({'Booking Id': booking_id, 'Status': 'Already Validated'})

        # Check if expired (assuming you have a 'expiry_date' field in your data)
        if 'timestamp' in booking_data:
            expiration_time = (float(booking_data['timestamp'])*1000 + 12*60)/1000
            logging.info(expiration_time)
            logging.info(time.time())
            if expiration_time < time.time():
                return JsonResponse({'Booking Id': booking_id, 'Status': 'Expired'})
            doc_ref.set({"used": True,"used_at":time.time()}, merge=True)
            return JsonResponse({'Booking Id': booking_id, 'Status': 'Valid Booking, Enjoy your free class.'})

    else:
        logging.info("No such bookings")
        return JsonResponse({'Booking Id': booking_id,'Status':'Invalid Booking Id'})


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
                        return JsonResponse({'Error': 'bookedAt not found in document'}, status=400)

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

