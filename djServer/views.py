from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt  
from utils.flags import FIREBASE_DB
from utils.common_utils import COLLECTIONS
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

def docs(request):
    # Get absolute paths to endpoint JSON files
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    djApi_endpoint_path = os.path.join(base_dir, 'djApi', 'endpoints.json')
    djBookings_endpoint_path = os.path.join(base_dir, 'djBookings', 'endpoints.json')
    djEmailer_endpoint_path = os.path.join(base_dir, 'emailer', 'endpoints.json')
    logging.info("{} {} {}".format(djApi_endpoint_path,djBookings_endpoint_path,djEmailer_endpoint_path))
    # Load endpoint maps from JSON files
    with open(djApi_endpoint_path) as f_djApi, open(djBookings_endpoint_path) as f_djBookings, open(djEmailer_endpoint_path) as f_djEmailer:
        endpoint_map_djApi = json.load(f_djApi)
        endpoint_map_djBookings = json.load(f_djBookings)
        endpoint_map_djEmailer = json.load(f_djEmailer)

    # Merge endpoint maps
    endpoint_map = {**endpoint_map_djApi, **endpoint_map_djBookings, **endpoint_map_djEmailer}

    return render(request, 'apiGuides.html', {'endpoint_map': endpoint_map})
