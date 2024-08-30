from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from django.shortcuts import render
from .processor import cache, full_text_search, calculate_distance
from djApi.flags import *
import datetime
from fuzzywuzzy import fuzz
import json
import logging
import redis
from rest_framework.decorators import api_view
logging.basicConfig(level=logging.INFO)  # Set the desired logging level

rc = redis.Redis(
    host="redis-11857.c276.us-east-1-2.ec2.cloud.redislabs.com", port=11857,
    username="default", # use your Redis user. More info https://redis.io/docs/management/security/acl/
    password="Fw82cxCVcMZED9ubfJVxeuSqcCb1vFqi", # use your Redis password
    )

@api_view(['GET'])
def landing_page(request):
    return JsonResponse("Hello User! For more check /help", safe=False)

@api_view(['GET'])
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

@api_view(['GET'])
def studioFullPage(request, studioId):

    db = firestore.client()
    doc_ref = db.collection("Studio").document(studioId)

    doc = doc_ref.get()
    if doc.exists:
        studio_data = doc.to_dict()
    else:

        return JsonResponse({"error": "No such document!"}, status=404)

    path = "StudioImages/{}/".format(studioId)
    logging.info(path)
    blobs = STORAGE_BUCKET.list_blobs(prefix=path, delimiter="/")
    signed_urls = []

    if blobs:
        for blob in blobs:
            signed_url = blob.generate_signed_url(datetime.timedelta(seconds=600), method='GET')
            signed_urls.append(signed_url)
    studio_data['studioImages'] = signed_urls

    return JsonResponse(studio_data)

def get_studio_data(studioId):
    db = firestore.client()
    doc_ref = db.collection("Studio").document(studioId)

    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    else:
        return None

def get_signed_urls(studioId):
    path = f"StudioImages/{studioId}/"
    blobs = STORAGE_BUCKET.list_blobs(prefix=path, delimiter="/")
    signed_urls = []

    if blobs:
        for blob in blobs:
            signed_url = blob.generate_signed_url(datetime.timedelta(seconds=600), method='GET')
            signed_urls.append(signed_url)
    return signed_urls

@api_view(['GET'])
def studioTextData(request, studioId):
    studio_data = get_studio_data(studioId)

    if studio_data is None:
        return JsonResponse({"error": "No such document!"}, status=404)

    return JsonResponse(studio_data)

@api_view(['GET'])
def studioImageURLs(request, studioId):
    signed_urls = get_signed_urls(studioId)
    return JsonResponse({"studioImages": signed_urls})


@api_view(['GET'])
def studioRatingChange(request):

    userId = request.GET.get("userId", "")
    studioId = request.GET.get("studioId", "")
    newRating = float(request.GET.get("newRating", ""))
    db = firestore.client()
    ratingsId = userId + "_" + studioId

    ratings_ref = db.collection("Ratings").document(ratingsId)
    studio_ref = db.collection("Studio").document(studioId)

    ratings_doc = ratings_ref.get()

    if ratings_doc.exists:
        old_rating = ratings_doc.get("rating")
        total_rating = studio_ref.get("totalRating")
        rated_by = studio_ref.get("ratedBy")
        new_total_rating = total_rating - old_rating + newRating
        avg_rating = new_total_rating / rated_by
    else:
        total_rating = studio_ref.get("totalRating")
        rated_by = studio_ref.get("ratedBy")
        new_total_rating = total_rating + newRating
        avg_rating = new_total_rating / (rated_by + 1)
        rated_by += 1

    ratings_ref.set({"rating": newRating}, merge=True)

    studio_ref.set({
        "totalRating": new_total_rating,
        "ratedBy": rated_by,
        "avgRating": avg_rating
    }, merge=True)

    return JsonResponse({"success": True})

@api_view(['GET'])
def getStudioRating(request,studioId,userId):

    if not studioId or not userId:
        JsonResponse({"success": False})

    ratingsId = userId + "_" + studioId
    db = firestore.client()
    ratings_ref = db.collection("Ratings").document(ratingsId)
    ratings_doc = ratings_ref.get()

    if ratings_doc.exists:
        rating = ratings_doc.get("rating")
        return JsonResponse({"success": True,"rating":rating})
    else:
        return JsonResponse({"success": False})

@api_view(['GET'])
def landingPageImages(request):
    blobs = STORAGE_BUCKET.list_blobs(prefix="LandingPageImages/D", delimiter="/")
    signed_urls = []
    for blob in blobs:
        signed_url = blob.generate_signed_url(datetime.timedelta(seconds=800), method='GET')
        signed_urls.append(signed_url)
    return JsonResponse({"signed_urls": signed_urls,"count":len(signed_urls)})

@api_view(['GET'])
def search(request):
    city = request.GET.get("city", "New Delhi")
    entity = request.GET.get("entity", "Studio")

    query = request.GET.get("query", "")
    dance_style = request.GET.get("danceStyle", "")
    level = request.GET.get("level", "All")
    price = request.GET.get("price", 10**10)
    
    user_location = (float(request.GET.get("user_lat", 0)), float(request.GET.get("user_lon", 0)))

    logging.info(f"FTS parameters {query}, {city}, {dance_style}, {entity}, {level}, {price}, {user_location}")
    if city is None or city == 'null':
        return {}
    try:
        cache_key = f"{city.lower()}-{entity}"
        cached_data = json.loads(rc.get(cache_key) or '{}')
        logging.info("Before FTS")
        results = full_text_search(query, dance_style, cached_data, entity=entity,level=level, price=price)
        # logging.info(results)
        distance = int(request.GET.get("distance", 20))
        if user_location != (0, 0):
            filtered_results = []
            for result_id, result in results.items():
                if result.get("geolocation"):
                    distance_in_kms = calculate_distance(user_location, (float(result["geolocation"]["lat"]), float(result["geolocation"]["lng"])))
                    if distance_in_kms <= distance:
                        result["distance_in_kms"] = round(distance_in_kms, 2)
                        filtered_results.append(result)
            results = {result["id"]: result for result in filtered_results}

        logging.info("results length: {}".format(len(results)))
        return JsonResponse(results, safe=False)
    except Exception as e:
        logging.error("Error searching: ", e)
        return JsonResponse({"error": "Internal Server Error"}, status=500)


@api_view(['GET'])
def search1(request):
    query = request.GET.get("query", "")
    city = request.GET.get("city", "New Delhi")
    dance_style = request.GET.get("danceStyle", "")
    entity = request.GET.get("entity", "Studio")
    user_location = (float(request.GET.get("user_lat", 0)), float(request.GET.get("user_lon", 0)))
    logging.info(entity)
    try:
        cache_key = city.lower()
        cache_key = cache_key + "-" + entity
        logging.info(entity)
        cached_data = json.loads(rc.get(cache_key) or '[]')
        #if entity != 'Studio':
            #return JsonResponse(cached_data, safe=False)
        
        results = full_text_search(query, dance_style, cached_data,entity=entity)
        distance = int(request.GET.get("distance", 20))
        if user_location != (0, 0):
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

@api_view(['GET'])
def autocomplete(request):
    #studio_name_query = request.GET.get('query', '').lower()
    city = request.GET.get('city', '').lower()
    entity = request.GET.get("entity", "Studio")
    key = city.lower()+"-"+entity+'-'+"Lite"
    studio_names_json = rc.get(key)
    logging.info(studio_names_json)
    if studio_names_json:
        return JsonResponse(json.loads(studio_names_json),safe=False)
    else:
        return JsonResponse([])



def help(request):
    endpoint_map = {
        "/": "Landing page",
        "/get_all_data": "Get all data from the cache",
        "/search?query=<your_query>&city=<your_city>&danceStyle=<your_dance_style>": "Perform a filtered full-text search",
        "/autocomplete?query=<your_query>": "Get autocomplete suggestions",
        "/landingPageImages":"Urls of Landing Page img",
        "/studioFullPage/<str:studioId>":"Studio Full Page Data with Images Url",
        "/getStudioRating/<str:studioId>/<str:userId>/":"Get rating of studio by a user",
        "/studioRatingChange/":"Change rating of studio by a user",
        "/help": "API guide (you are here)"
    }
    #return JsonResponse(endpoint_map, safe=False)
    return render(request, 'apiGuide.html', {'endpoint_map': endpoint_map})
