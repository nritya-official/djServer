from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
import json
import time
import logging
from utils.flags import FIREBASE_AUTH
import jwt

class PerformanceMonitoringMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.start_time = time.time()

    def process_response(self, request, response):
        duration = time.time() - request.start_time
        logging.info(f"Processed {request.path} in {duration*1000:.9f} milli seconds")
        return response

class FirebaseJWTMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response
        self.allowed_paths = [
            '/emailer/studioAdd/',
            '/emailer/studioUpdate/',
            '/emailer/freeTrialBookings/',
        ]

    def __call__(self, request):
        if request.path in self.allowed_paths:
            auth_header = request.headers.get('Authorization')
            id_token = None
            if auth_header and auth_header.startswith('Bearer '):
                id_token = auth_header.split('Bearer ')[1]
            if not id_token:
                return JsonResponse({'error': 'No token provided'}, status=401)
            try:
                decoded_token = FIREBASE_AUTH.verify_id_token(id_token)
                logging.info("Decoded token: %s", decoded_token)
                user_id_from_request = request.POST.get('user_id') or request.GET.get('user_id')
                if user_id_from_request != decoded_token.get('user_id'):
                    return JsonResponse({'error': 'User ID does not match'}, status=401)
                
                request.user = decoded_token
            except Exception as e:
                logging.warning(f"Exception for token {e}")
                try:
                    decoded_token = jwt.decode(id_token, options={"verify_signature": False}, algorithms=["RS256"])
                    logging.info("Decoded token: %s", decoded_token)
                    user_id_from_request = request.POST.get('user_id') or request.GET.get('user_id')

                    if user_id_from_request != decoded_token.get('user_id'):
                        return JsonResponse({'error': 'User ID does not match'}, status=401)
                    
                    request.user = decoded_token
                except Exception as er:
                    logging.error("Invalid token %s", str(er))
                    return JsonResponse({'error': 'Invalid token'}, status=401)

        response = self.get_response(request)
        return response
