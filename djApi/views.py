from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from django.shortcuts import render
from .processor import cache, full_text_search, calculate_distance
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
    user_location = (float(request.GET.get("user_lat", 0)), float(request.GET.get("user_lon", 0)))


    try:
        cache_key = city.lower()
        cached_data = json.loads(rc.get(cache_key) or '[]')
        logging.info(cache_key)
        logging.info(cached_data)
        results = full_text_search(query, dance_style, cached_data)
        distance = int(request.GET.get("distance", 0))
        if distance in [2, 5, 10, 20] and user_location != (0, 0):
            filtered_results = []
            for result in results:
                if result.get("geolocation") :
                    distance_in_kms =  calculate_distance(user_location,(float(result["geolocation"]["lat"]), float(result["geolocation"]["lng"])))
                    if(distance_in_kms <= distance):
                        result["distance_in_kms"] = round(distance_in_kms, 2)
                        filtered_results.append(result)
            results = filtered_results

        logging.info("results length: {}".format(len(results)))
        return JsonResponse(results, safe=False)
    except Exception as e:
        logging.error("Error searching: ", e)
        return JsonResponse({"error": "Internal Server Error"}, status=500)


def autocomplete(request):
    studio_name_query = request.GET.get('query', '').lower()
    city = request.GET.get('city', '').lower()

    if not studio_name_query or not city:
        return jsonify([])

    # Fetch studio names from Redis based on the provided city
    key = city.lower()+"-Lite"
    studio_names_json = rc.get(key)

    if studio_names_json:
        studio_names = json.loads(studio_names_json)
        # Filter studio names based on the query
        suggestions = []
        for name in studio_names:
            ratio = fuzz.partial_ratio(studio_name_query, name.lower())
            if ratio >= 70:
                suggestions.append(name)

        return jsonify(suggestions)
    else:
        return jsonify([])



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
