from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
import json
import time
import logging

class PerformanceMonitoringMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.start_time = time.time()

    def process_response(self, request, response):
        duration = time.time() - request.start_time
        logging.INFO(f"Processed {request.path} in {duration*1000:.9f} milli seconds")
        return response
