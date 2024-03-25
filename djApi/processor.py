import firebase_admin.firestore
import json
from fuzzywuzzy import fuzz
import redis
import logging
from django.core.cache import cache
from djApi.flags import FIREBASE_DB
from geopy.distance import geodesic

logging.basicConfig(level=logging.INFO)

def calculate_distance(location1, location2):
    """
    Calculate the street distance between two geolocations.

    Parameters:
    - location1: Tuple of (latitude, longitude) for the first location
    - location2: Tuple of (latitude, longitude) for the second location

    Returns:
    - Distance in kilometers
    """
    distance = geodesic(location1, location2).kilometers
    logging.info("{} {} = {}".format(location1,location2,distance))
    return distance

def update_cache_old(rc):
    print("Cache updating....")
    logging.info("Cache updating...")
    x = True
    try:
        db = firebase_admin.firestore.client()
        docs = db.collection('Studio').stream()
        data_source = {}

        for doc in docs:
            data = {}
            for field, value in doc.to_dict().items():
                allowed_fields = ['city', 'avgRating', 'status', 'isPremium', 'danceStyles', 'state', 'studioName', 'UserId','geolocation']
                if field in allowed_fields:
                    if isinstance(value, firebase_admin.firestore.DocumentReference):
                        data[field] = value.id
                    else:
                        data[field] = value
            data["studioId"] = doc.id
            x =  False
            # Organize data by city in the cache
            city = data.get("city", "")
            logging.info(city)
            if city:
                if city not in data_source:
                    data_source[city] = []
                data_source[city].append(data)
        for city, studios in data_source.items():
            rc.set(city.lower(), json.dumps(studios))
            cached_data = rc.get(city.lower())
            #logging.info(json.loads(cached_data) if cached_data else [])


        print("Cache updated successfully")
        #logging.info(data_source)
        logging.info("Cache updated successfully")
    except Exception as e:
        #print("Error updating cache:", e)
        logging.error("Error updating cache: ", e)

def update_cache(rc):
    logging.info("Cache updating....")
    db = firestore.client()
    docs = db.collection('Studio').stream()
    data_source = {}
    city_studio_names = {}

    for doc in docs:
        data = {}
        for field, value in doc.to_dict().items():
            allowed_fields = ['city', 'avgRating', 'status', 'isPremium', 'danceStyles', 'state', 'studioName', 'UserId','geolocation']
            if field in allowed_fields:
                if isinstance(value, firestore.DocumentReference):
                    data[field] = value.id
                else:
                    data[field] = value
        data["studioId"] = doc.id

        # Organize data by city in the cache
        city = data.get("city", "")
        if city:
            if city not in data_source:
                data_source[city] = []
            data_source[city].append(data)

            studio_name = data.get("studioName", "")
            if studio_name:
                if city not in city_studio_names:
                    city_studio_names[city] = set()
                city_studio_names[city].add(studio_name)

    
    for city, studios in data_source.items():
        rc.set(city.lower(), json.dumps(studios))
        cached_data = rc.get(city.lower())

    # Save city_studio_names data in Redis
    for city, studio_names in city_studio_names.items():
        rc.set(f"{city.lower()}-Lite", json.dumps(list(studio_names)))
    
    logging.info("Cache updated successfully")


def autocomplete(cache, query):
    results = []

    for key in cache.keys():
        if query.lower() in key.lower():
            results.append(key)

    return results


def filter_by_city(data, city):
    return city is None or data.get("city", "").lower() == city.lower()

def filter_by_dance_style(data, dance_style):
    return dance_style is None or data.get("danceStyles", "").lower() == dance_style.lower()


def full_text_search(query, dance_style='', cache=[]):
    logging.info("FTS")
    logging.info(len(cache))
    results = []
    query_tokens = query.lower().split()  # Tokenize search query
    dance_style_filters = set(map(str.strip, dance_style.lower().split(',')))


    for data in cache:
        # Check if the danceStyle filter is satisfied
        studio_dance_styles = set(map(str.strip, data.get("danceStyles", "").lower().split(',')))
        dance_styles_tokens = data.get("danceStyles", "").lower().split(',')

        if len(query)==0 and len(dance_style)==0:
            results.append(data)
            continue

        if dance_style_filters:
            studio_name_tokens = data.get("studioName", "").lower().split()
            dance_style_filter_matched = not dance_style_filters or dance_style_filters.intersection(studio_dance_styles)

            if dance_style_filter_matched:
                results.append(data)
                continue


            # Check if any token in the query partially matches any token in danceStyles or studioName
            if any(
                fuzz.partial_ratio(query_token, dance_style_token) >= 70 or
                fuzz.partial_ratio(query_token, studio_name_token) >= 76
                for query_token in query_tokens
                for dance_style_token in dance_styles_tokens
                for studio_name_token in studio_name_tokens
            ):
                results.append(data)

    print(len(results))
    return results


def full_text_search1(query, city='', dance_style='',cache={}):
    print(query)
    results = []
    query_tokens = query.lower().split()  # Tokenize search query

    for key, data in cache.items():
        # Check if both the city and danceStyle filters are satisfied
        # city -> danceStyle-> query
        city_filter = (city is None) or (data.get("city", "").lower() == city.lower())
        dance_style_filter = (dance_style is None) or (data.get("danceStyles", "").lower() == dance_style.lower())

        processFurther = True

        if(city!='' or dance_style!=''):
            if city_filter or dance_style_filter:
                processFurther =  True
            else:
                processFurther = False
        print(processFurther,len(query_tokens))
        if processFurther:
            dance_styles_tokens = data.get("danceStyles", "").lower().split(',')
            studio_name_tokens = data.get("studioName", "").lower().split()
            if len(query_tokens) ==0 :
                results.append(data)
                print("Adding...")
                continue
            # Check if any token in the query partially matches any token in danceStyles or studioName
            if any(
                fuzz.partial_ratio(query_token, dance_style_token) >= 70 or
                fuzz.partial_ratio(query_token, studio_name_token) >= 76
                for query_token in query_tokens
                for dance_style_token in dance_styles_tokens
                for studio_name_token in studio_name_tokens
            ):
                results.append(data)

    print(len(results))
    return results

