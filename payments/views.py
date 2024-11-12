import json
import os
import razorpay
from utils.flags import FIREBASE_DB
from payments.constants import PAYMENT_STATUS
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from datetime import datetime
import logging
from utils.common_utils import *
from utils.time_utils import TimeNow, TimezoneConstants
import hashlib
import random
import string

# Get Razorpay Key id and secret for authorizing Razorpay client.
RAZOR_KEY = "rzp_test_KGN4elrXhQOG65"
RAZOR_SECRET = "wmMR51UhKWEJf1LeHKiJ24S5"

# Creating a Razorpay Client instance.
razorpay_client = razorpay.Client(auth=(RAZOR_KEY, RAZOR_SECRET))

def generate_unique_hash(data):
    # Convert the data to a string
    data_string = str(data)
    
    # Create an initial hash using SHA-256
    initial_hash = hashlib.sha256(data_string.encode()).hexdigest()
    
    # Generate a random alphanumeric suffix for uniqueness
    suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    
    # Combine the initial hash with the suffix and truncate to a manageable length
    unique_hash = (initial_hash + suffix)[:16]  # Truncate or adjust length as needed
    
    return "order_NR"+unique_hash


def date_time_precheck(entity_id, entity_type):
    """
    Pre-checks the entity type, existence, and event timing.
    
    :param entity_id: ID of the entity (event).
    :param entity_type: Collection name.
    :return: Tuple (boolean, message, entity_data) where:
             - boolean indicates validity,
             - message provides reason if invalid,
             - entity_data is the event details if valid.
    """
    if not is_valid_entity_type(entity_type):
        return False, BOOKINGS_MSG.INVALID_SELECTION, None
    
    # Fetch event details
    entity_doc_ref = FIREBASE_DB.collection(entity_type).document(entity_id)
    entity_doc = entity_doc_ref.get()
    
    if not entity_doc.exists:
        return False, BOOKINGS_MSG.EVENT_NOT_FOUND, None
    
    # Extract details
    entity_data = entity_doc.to_dict()
    event_date = entity_data.get("date")
    event_time = entity_data.get("time")
    start_time = event_time.split(" - ")[0].strip()
    
    # Perform time check
    try:
        logging.info(f'AR_ :---event_date {event_date}, event_time {start_time}')
        event_time_check = TimeNow(TimezoneConstants.IST, event_date, start_time)
        logging.info(f'event_time_check {event_time_check}')
        comparison_result = event_time_check.compare_with_now(TimezoneConstants.IST)
        
        if comparison_result < 0:
            return False, BOOKINGS_MSG.EVENT_PASSED, None
    except ValueError as ve:
        return False, f'Error processing event time: {ve}', None
    logging.info("Booking date_time_precheck passed")
    return True, None, entity_data


def capacity_check(entity_id, entity_type, user_id, capacity=0, persons_allowed=1):
    """
    Checks if the event has capacity for the given number of persons.
    
    :param entity_id: ID of the entity (event).
    :param entity_type: Collection name.
    :param user_id: ID of the user.
    :param entity_data: Dictionary with entity details (capacity, etc.)
    :param persons_allowed: Number of persons allowed in the booking.
    :return: Tuple (boolean, message) where:
             - boolean indicates capacity availability,
             - message provides reason if unavailable.
    """
    #capacity = entity_data.get("capacity", 0)
    capacity = int(capacity)
    logging.info(capacity)
    if entity_type == COLLECTIONS.WORKSHOPS:
        bookings_ref = FIREBASE_DB.collection(COLLECTIONS.BOOKINGS)
        query = bookings_ref.where("entity_id", "==", entity_id) \
                            .where("entity_type", "==", entity_type) \
                            .where("user_id", "==", user_id) \
                            .where("status", "==", PAYMENT_STATUS.SUCCESS)
        
        total_persons = sum(doc.to_dict().get("persons_allowed", 1) for doc in query.stream())
        
        if int(total_persons) >= int(capacity):
            return False, BOOKINGS_MSG.SEATS_FULL

        if int(total_persons) + int(persons_allowed) <= int(capacity):
            return True, None
        else:
            return False, BOOKINGS_MSG.SEATS_INSUFFICIENT
    
    elif entity_type == COLLECTIONS.OPENCLASSES:
        bookings_ref = FIREBASE_DB.collection(COLLECTIONS.BOOKINGS)
        query = bookings_ref.where("entity_id", "==", entity_id) \
                            .where("entity_type", "==", entity_type) \
                            .where("user_id", "==", user_id) \
                            .where("status", "==", PAYMENT_STATUS.SUCCESS)
        
        for doc in query.stream():
            return False, BOOKINGS_MSG.ALREADY_BOOKED + "Id: "+ str(doc.id ) 

    elif entity_type == COLLECTIONS.COURSES:
        # Non-zero Price + No cap limit
        return True, None

    return True, None


def check_event_availability(entity_id, entity_type, user_id, persons_allowed=1):
    """
    Wrapper function to check event availability based on date_time_precheck and capacity.
    
    :param entity_id: ID of the entity (event).
    :param entity_type: Collection name.
    :param user_id: ID of the user.
    :param persons_allowed: Number of persons allowed in the booking.
    :return: Dictionary with capacity and time check results.
    """
    # Step 1: Pre-check entity and timing
    is_valid, message, entity_data = date_time_precheck(entity_id, entity_type)
    if not is_valid:
        return False, message
    logging.info("Date Time Check passed")
    # Step 2: Perform capacity check
    capacity = entity_data.get("capacity", 0)
    is_capacity_ok, capacity_message = capacity_check(entity_id, entity_type, user_id, capacity, persons_allowed)
    return is_capacity_ok, capacity_message

@api_view(['POST'])
def intitate_booking(request):
    """
    Function-based view for creating a Razorpay Order.
    :return: necessary values to open Razorpay SDK
    """
    logging.info("AR_:intitate_booking started")
    # Extract new fields from request data
    name = request.data.get("name", None)
    email = request.data.get("email", "")
    currency = request.data.get("currency", "INR") #Lite
    price_per_person = request.data.get("price_per_person", "")
    discount_code = request.data.get("discount_code", None) #Lite
    persons_allowed = request.data.get("persons_allowed", "")
    total_amount = request.data.get("total_amount", "")
    #order_id = request.data.get("order_id", "")
    user_id = request.data.get("user_id", None)
    entity_id = request.data.get("entity_id", "")
    entity_name = request.data.get("entity_name", "")
    entity_type = request.data.get("entity_type", "")
    associated_studio_id = request.data.get("associated_studio_id","")
    if not user_id or not entity_id or not entity_type or not persons_allowed or not entity_name:
        logging.info(f'AR_:intitate_booking extracted {entity_id}, {entity_type}, {entity_name},{user_id}')
        return Response({'message':"Pay load incomplete" }, status= 401) 
    logging.info(f'AR_:intitate_booking extracted {entity_id}, {entity_type}, {entity_name},{user_id};')
    proceed , error = check_event_availability(entity_id, entity_type, user_id, persons_allowed)
    logging.info(f'AR_:intitate_booking proceed or not {proceed} {error}')
    if not proceed:
        err_data = {
            "message": error,
            "code": nSuccessCodes.NOT_ACCEPTED
        }
        logging.info(f'AR_:intitate_booking failed due to {err_data} ')
        return Response(err_data, status=status.HTTP_200_OK)

    if int(total_amount) == 0 or entity_type == COLLECTIONS.OPENCLASSES:
        
        new_order = {
        "name": name,
        "user_id": user_id,
        "amount": total_amount,
        "razorpay_order_id": None,
        "status": PAYMENT_STATUS.SUCCESS,
        "payment_id": None,
        "signature_id": None,
        "entity_id": entity_id,
        "entity_name": entity_name,
        "entity_type": entity_type,
        "billing_details": None,
        "payment_initiation_time": datetime.now(),
        "associated_studio_id" : associated_studio_id,
        "persons_allowed": persons_allowed,
        }
        try:
            order_id = generate_unique_hash(new_order)
            logging.info(new_order)
            FIREBASE_DB.collection(COLLECTIONS.BOOKINGS).document(order_id).set(new_order)

            data = {
            "name": name,
            "amount": total_amount,
            "currency": 'INR',
            "orderId": order_id,
            "code": nSuccessCodes.ACCEPTED,
            }
            logging.info(data)
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            logging.info(e)
            return Response({'Error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    

    billing_details = {
        "name": name,
        "email": email,
        "price_per_person": price_per_person,
        "no_of_persons": persons_allowed,
        "total_amount": total_amount,
        "currency": currency,
        "user_id": user_id,
    }


    # Create Razorpay order
    try:
        razorpay_order = razorpay_client.order.create(
            {"amount": int(total_amount) * 100, "currency": currency, "payment_capture": "1"}
        )
    except razorpay.errors.RazorpayError as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Add the new order to the db
    new_order = {
        "name": name,
        "user_id": user_id,
        "amount": total_amount,
        "razorpay_order_id": razorpay_order["id"],
        "status": PAYMENT_STATUS.PENDING,
        "payment_id": None,
        "signature_id": None,
        "entity_id": entity_id,
        "entity_name": entity_name,
        "entity_type": entity_type,
        "billing_details": billing_details,
        "payment_initiation_time": datetime.now(),
        "associated_studio_id" : associated_studio_id,
        "persons_allowed": persons_allowed,
    }
    FIREBASE_DB.collection(COLLECTIONS.BOOKINGS).document(razorpay_order["id"]).set(new_order)

    data = {
        "name": name,
        "merchantId": RAZOR_KEY,
        "amount": total_amount,
        "currency": 'INR',
        "orderId": razorpay_order["id"],
        "code": nSuccessCodes.ACCEPTED,
    }

    return Response(data, status=status.HTTP_200_OK)

@api_view(['POST'])
def create_payment(request):
    """
    Function-based view for creating a Razorpay Order.
    :return: necessary values to open Razorpay SDK
    """
    # Extract new fields from request data
    name = request.data.get("name", "")
    plan = request.data.get("plan", "")
    order_id = request.data.get("order_id", "")
    entity_id = request.data.get("entity_id", "")
    entity_name = request.data.get("entity_name", "")
    entity_type = request.data.get("entity_type", "")

    # Define amount based on plan
    mp = {"Super": 499, "Medium": 299, "Basic": 99}
    amount = mp.get(plan, 0)

    # Create Razorpay order
    try:
        razorpay_order = razorpay_client.order.create(
            {"amount": int(amount) * 100, "currency": "INR", "payment_capture": "1"}
        )
    except razorpay.errors.RazorpayError as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Add the new order to the db
    new_order = {
        "name": name,
        "amount": amount,
        "razorpay_order_id": None,
        "status": PAYMENT_STATUS.FREE,
        "entity_id": entity_id,
        "entity_name": entity_name,
        "entity_type": entity_type,
        "payment_initiation_time": datetime.datetime.now(tz=datetime.timezone.utc),
    }
    FIREBASE_DB.collection(COLLECTIONS.BOOKINGS).document(razorpay_order["id"]).set(new_order)


    data = {
        "name": name,
        "merchantId": RAZOR_KEY,
        "amount": amount,
        "currency": 'INR',
        "orderId": razorpay_order["id"],
    }

    return Response(data, status=status.HTTP_200_OK)

@api_view(['POST'])
def verify_payment(request):
    """
    Function-based view for verifying Razorpay Order.
    :return: Success and failure response messages
    """
    # Get data from request
    response = request.data.get('response')
    bookingData = request.data.get('bookingData')
    logging.info(response)
    if "razorpay_signature" in response:
        try:
            razorpay_client.utility.verify_payment_signature(response)
            payment_method = bookingData.get('payment_method','Unknown')
            confirmation = {
                "status": PAYMENT_STATUS.SUCCESS,
                "payment_id": response['razorpay_payment_id'],
                "signature_id": response['razorpay_signature'],
                "payment_completion_time": datetime.now(),
                "payment_method": payment_method
            }

            entity_id = bookingData.get('entity_id')
            entity_type = bookingData.get('entity_type')
            user_id = bookingData.get('user_id')
            persons_allowed = bookingData.get('persons_allowed')

            entity_doc_ref = FIREBASE_DB.collection(entity_type).document(entity_id)
            entity_doc = entity_doc_ref.get()
            
            if not entity_doc.exists:
                return False, BOOKINGS_MSG.EVENT_NOT_FOUND, None
            
            # Extract details
            entity_data = entity_doc.to_dict()
            capacity = entity_data.get("capacity", 0)

            if capacity_check(entity_id, entity_type, user_id, capacity, persons_allowed):
                FIREBASE_DB.collection(COLLECTIONS.BOOKINGS).document(response["razorpay_order_id"]).set(confirmation, merge=True)
                return Response({'message': BOOKINGS_MSG.SEATS_BOOKED}, status = BOOKINGS_STATUS.SEATS_BOOKED)
            else:
                confirmation = {
                "status": PAYMENT_STATUS.SUCCESS,
                "payment_id": response['razorpay_payment_id'],
                "signature_id": response['razorpay_signature'],
                "payment_completion_time": datetime.now(),
                "message": BOOKINGS_MSG.PAID_BUT_SEATS_INSUFFICIENT,
                "refund": PAYMENT_REFUNDED.STARTED
                }
                message = BOOKINGS_MSG.PAID_BUT_SEATS_INSUFFICIENT+ f'Send us {razorpay_order_id} for faster refund.'
                FIREBASE_DB.collection(COLLECTIONS.BOOKINGS).document(response["razorpay_order_id"]).set(confirmation, merge=True)  
                return Response({'message':message }, status= BOOKINGS_STATUS.PAID_BUT_SEATS_INSUFFICIENT) 

            
        except razorpay.errors.SignatureVerificationError:
            return Response({'message': BOOKINGS_MSG.SIGNATURE_MISMATCH}, status=BOOKINGS_STATUS.SIGNATURE_MISMATCH)
    else:
        # Handling failed payments
        error_code = response['error[code]']
        error_description = response['error[description]']
        error_source = response['error[source]']
        error_reason = response['error[reason]']
        error_metadata = json.loads(response['error[metadata]'])

        confirmation = {
                "status": PAYMENT_STATUS.FAILURE,
                "error_code": error_code,
                "error_description": error_description,
                "error_source": error_source,
                "error_reason": error_reason,
                "error_metadata": error_metadata,
                "payment_completion_time": datetime.datetime.now(tz=datetime.timezone.utc)
            }
        FIREBASE_DB.collection(COLLECTIONS.BOOKINGS).document(response["razorpay_order_id"]).set(confirmation, merge=True)

        return Response({'message': error_status}, status=status.HTTP_401_UNAUTHORIZED)
