from django.shortcuts import render
from django.http import JsonResponse
import random
from twilio.rest import Client
from django.core.cache import cache
from djSms.flags import TWILIO_CREDS
from django.views.decorators.csrf import csrf_exempt
import logging

# Utility function to generate a random OTP
def generate_otp():
    return random.randint(1000, 9999)

def send_otp(phone_number, otp):
    phone_number = "+91" + phone_number
    account_sid = TWILIO_CREDS.ACCOUNT_SID
    auth_token = TWILIO_CREDS.AUTH_TOKEN
    client = Client(account_sid, auth_token)
    logging.debug(f'{phone_number} => {otp}')
    message = client.messages.create(
        body=f"Your OTP is {otp} for Nritya account.",
        from_= TWILIO_CREDS.PHONE_NUMBER ,  # Twilio number
        to=phone_number
    )
    return message.sid

# Utility function to store OTP in cache with a timeout
def store_otp(phone_number, otp):
    phone_number = "+91" + phone_number
    expiration_time = 300  # 5 minutes
    cache.set(f'otp_{phone_number}', otp, timeout=expiration_time)
    logging.debug(cache.get(f'otp_{phone_number}'))

# Utility function to verify OTP
def _verify_otp(phone_number, user_otp):
    phone_number = "+91" + phone_number
    logging.debug(f'{phone_number}.')
    stored_otp = cache.get(f'otp_{phone_number}')
    logging.info(f'{phone_number} - {stored_otp} - {user_otp}')
    if stored_otp is not None and user_otp and str(stored_otp) == str(user_otp):
        logging.info(f'{phone_number} verified')
        return True
    return False

# 1. Endpoint to request OTP generation
@csrf_exempt
def request_otp(request):
    logging.debug("request_otp")
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        logging.debug(f"request_otp {phone_number}")
        if phone_number:
            otp = generate_otp()
            store_otp(phone_number, otp)
            send_otp(phone_number, otp)
            return JsonResponse({"status": "success", "message": "OTP sent successfully!"})
        else:
            return JsonResponse({"status": "error", "message": "Phone number is required."})
    
    return JsonResponse({"status": "error", "message": "Invalid request method."})

# 2. Endpoint to verify the OTP
@csrf_exempt
def confirm_otp(request):
    logging.debug("confirm_otp")
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        user_otp = request.POST.get('otp')
        logging.info(f'confirm_otp {phone_number} - {user_otp}')
        if phone_number and user_otp:
            if _verify_otp(phone_number, user_otp):
                return JsonResponse({"status": "success", "message": "OTP verified successfully!"})
            else:
                return JsonResponse({"status": "error", "message": "Invalid OTP or OTP expired."})
        else:
            return JsonResponse({"status": "error", "message": "Phone number and OTP are required."})
    
    return JsonResponse({"status": "error", "message": "Invalid request method."})
