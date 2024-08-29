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
    db = firebase_admin.firestore.client()
    docs = db.collection('Studio').stream()
    data_source = {}
    city_studio_names = {}

    for doc in docs:
        data = {}
        for field, value in doc.to_dict().items():
            allowed_fields = ['city', 'avgRating', 'status', 'isPremium', 'danceStyles', 'state', 'studioName', 'UserId','geolocation','street']
            if field in allowed_fields:
                if isinstance(value, firebase_admin.firestore.DocumentReference):
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


collection_name_field ={
    'Studio' : 'studioName',
    'Workshops' : 'workshopName',
    'OpenClasses' : 'openClassName',
    'Courses' : 'workshopName'
}


collection_danceStyles_field ={
    'Studio' : 'danceStyles',
    'Workshops' : 'danceStyles',
    'OpenClasses' : 'danceStyle',
    'Courses' : 'danceStyles'
}

def fuzzy_match(token1, token2, threshold):
    return fuzz.partial_ratio(token1, token2) >= threshold

def match_tokens(query_tokens, name_tokens, style_tokens):
    for query_token in query_tokens:
        for name_token in name_tokens:
            if fuzzy_match(query_token, name_token, 75):
                return True
        for style_token in style_tokens:
            if fuzzy_match(query_token, style_token, 60):
                return True
    return False

def full_text_search(query, dance_style='', cache={}, entity="Studio"):
    logging.info("FTS")
    logging.debug(len(cache))
    results = {}
    dance_style_field_name = collection_danceStyles_field.get(entity, 'danceStyles')
    entity_name_field = collection_name_field.get(entity, 'studioName')

    # Preprocessing & Tokenization of query and dance_style filters
    query_tokens = query.lower().split()
    dance_style_filters = set(map(str.strip, dance_style.lower().split(',')))
    
    for data_id, data in cache.items():
        logging.info(type(data))
        if data_id == 'null' or data is None:
            continue
        # Retrieve dance styles and entity name from cache
        dance_styles_data = data.get(dance_style_field_name, "")
        entity_name_data = data.get(entity_name_field, "").lower()

        # Tokenize dance styles data from cache to a set of tokens
        if isinstance(dance_styles_data, str):
            entity_dance_styles = set(map(str.strip, dance_styles_data.lower().split(',')))
            dance_styles_tokens = dance_styles_data.lower().split(',')
        elif isinstance(dance_styles_data, list):
            entity_dance_styles = set(map(lambda x: x.strip().lower(), dance_styles_data))
            dance_styles_tokens = [style.lower() for style in dance_styles_data]
        else:
            entity_dance_styles = set()
            dance_styles_tokens = []

        if len(query_tokens) == 0 and len(dance_style_filters) == 0:
            results[data_id] = data
            continue

        if dance_style_filters:
            if dance_style_filters.intersection(entity_dance_styles):
                results[data_id] = data
                continue
        
        if len(query_tokens) == 0:
            continue

        entity_name_tokens = entity_name_data.split()
        if match_tokens(query_tokens, entity_name_tokens, dance_styles_tokens):
            results[data_id] = data
    #logging.info(results)
    logging.info(f"Total results found: {len(results)}")
    return results
