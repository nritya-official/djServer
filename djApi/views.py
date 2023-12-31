from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from django.shortcuts import render
from .processor import cache, full_text_search
from fuzzywuzzy import fuzz
import json
import logging
import redis
logging.basicConfig(level=logging.INFO)  # Set the desired logging level

rc = redis.Redis(
    host="redis-11857.c276.us-east-1-2.ec2.cloud.redislabs.com", port=11857,
    username="default", # use your Redis user. More info https://redis.io/docs/management/security/acl/
    password="Fw82cxCVcMZED9ubfJVxeuSqcCb1vFqi", # use your Redis password
    )

def landing_page(request):
    return JsonResponse("Hello User! For more check /help", safe=False)

def get_all_data(request):
    # Assuming cache is a global variable
    
    logging.info("get all data called")
    logging.info(cache)
    cached_data_json = rc.get('studio_data')  
    if cached_data_json is not None:
        cached_data = json.loads(cached_data_json)
        return JsonResponse(cached_data)
    else:
        # Handle case where cache is not populated yet
        return JsonResponse({})


def search(request):
    query = request.GET.get("query", "")
    city = request.GET.get("city", "")
    dance_style = request.GET.get("danceStyle", "")
    results = full_text_search(query, city, dance_style, json.loads(rc.get('studio_data')))
    return JsonResponse(results, safe=False)

def autocomplete(request):
    query = request.GET.get("query", "")
    results_studio_name = autocomplete_field(cache, query, "studioName")
    results_dance_styles = autocomplete_field(cache, query, "danceStyles")
    combined_results = list(set(results_studio_name + results_dance_styles))
    return JsonResponse(combined_results, safe=False)

def help(request):
    endpoint_map = {
        "/": "Landing page",
        "/get_all_data": "Get all data from the cache",
        "/search?query=<your_query>&city=<your_city>&danceStyle=<your_dance_style>": "Perform a filtered full-text search",
        "/autocomplete?query=<your_query>": "Get autocomplete suggestions",
        "/help": "API guide (you are here)"
    }
    #return JsonResponse(endpoint_map, safe=False)
    return render(request, 'apiGuide.html', {'endpoint_map': endpoint_map})
