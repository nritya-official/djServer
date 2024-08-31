import json
import os
import razorpay
from djApi.flags import FIREBASE_DB, COLLECTIONS
from payments.constants import PAYMENT_STATUS
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
import datetime
import logging

# Get Razorpay Key id and secret for authorizing Razorpay client.
RAZOR_KEY = "rzp_test_KGN4elrXhQOG65"
RAZOR_SECRET = "wmMR51UhKWEJf1LeHKiJ24S5"

# Creating a Razorpay Client instance.
razorpay_client = razorpay.Client(auth=(RAZOR_KEY, RAZOR_SECRET))

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
        "razorpay_order_id": razorpay_order["id"],
        "status": PAYMENT_STATUS.PENDING,
        "payment_id": None,
        "signature_id": None,
        "order_id": order_id,
        "entity_id": entity_id,
        "entity_name": entity_name,
        "entity_type": entity_type,
        "payment_initiation_time": datetime.datetime.now(tz=datetime.timezone.utc),
    }
    FIREBASE_DB.collection(COLLECTIONS.TRANSACTIONS).document(razorpay_order["id"]).set(new_order)

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
    response = request.data
    logging.info(response)
    if "razorpay_signature" in response:
        try:
            razorpay_client.utility.verify_payment_signature(response)
            confirmation = {
                "status": PAYMENT_STATUS.SUCCESS,
                "payment_id": response['razorpay_payment_id'],
                "signature_id": response['razorpay_signature'],
                "payment_completion_time": datetime.datetime.now(tz=datetime.timezone.utc)
            }
            FIREBASE_DB.collection(COLLECTIONS.TRANSACTIONS).document(response["razorpay_order_id"]).set(confirmation, merge=True)

            return Response({'status': 'Payment Done'}, status=status.HTTP_200_OK)
        except razorpay.errors.SignatureVerificationError:
            return Response({'status': 'Signature Mismatch!'}, status=status.HTTP_400_BAD_REQUEST)
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
        FIREBASE_DB.collection(COLLECTIONS.TRANSACTIONS).document(response["razorpay_order_id"]).set(confirmation, merge=True)

        return Response({'error_data': error_status}, status=status.HTTP_401_UNAUTHORIZED)
