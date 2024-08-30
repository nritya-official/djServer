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

def match_tokens(query_tokens, name_tokens):
    for query_token in query_tokens:
        for name_token in name_tokens:
            if fuzzy_match(query_token, name_token, 75):
                return True
    return False

def filter_by_level(data, level_filters, entity):
    if isinstance(level_filters, str):
        level_filters = {level.strip().lower() for level in level_filters.split(',')}

    if not level_filters or "all" in level_filters:
        return True  

    if entity != "Studio":
        entity_level = data.get("level", "All").lower()
        if entity_level == "all" or entity_level in level_filters:
            return True

    return False


def filter_by_price(data, price_filter, entity):
    if price_filter and entity in ['Workshops', 'Courses']:
        entity_price = int(data.get("price", 0))
        if entity_price > price_filter:
            return False
    return True

def filter_by_dance_style(data, dance_style_filters, dance_style_field_name):
    if len(dance_style_filters) == 0:
        return True
    dance_styles_data = data.get(dance_style_field_name, "")
    if isinstance(dance_styles_data, str):
        entity_dance_styles = set(map(str.strip, dance_styles_data.lower().split(',')))
    elif isinstance(dance_styles_data, list):
        entity_dance_styles = set(map(lambda x: x.strip().lower(), dance_styles_data))
    else:
        entity_dance_styles = set()
    logging.debug(f"{dance_style_filters} --- {entity_dance_styles}")
    if dance_style_filters:
        match_set = dance_style_filters.intersection(entity_dance_styles)
        if len(match_set) == 0:
            return False
    return True

def filter_by_query(query_tokens, entity_name_tokens):
    if len(query_tokens) == 0:
        return True
    return match_tokens(query_tokens, entity_name_tokens)

def full_text_search(query, dance_style='', cache={}, entity="Studio", level="All", price=10**10):
    logging.info(f"FTS: Cache length {len(cache)}")
    results = {}
    dance_style_field_name = collection_danceStyles_field.get(entity, 'danceStyles')
    entity_name_field = collection_name_field.get(entity, 'studioName')

    # Preprocessing & Tokenization of query and dance_style filters
    query_tokens = query.lower().split()
    if dance_style:
        dance_style_filters = set(map(str.strip, dance_style.lower().split(',')))
    else:
        dance_style_filters = set()
    level_filter = level.lower()
    price_filter = int(price)

    for data_id, data in cache.items():
        if data_id == 'null' or data is None:
            continue

        if entity != 'Studio':
            if not filter_by_level(data, level_filter, entity):
                continue

        if entity in ['Workshops','OpenClasses']:
            if not filter_by_price(data, price_filter, entity):
                continue

        if not filter_by_dance_style(data, dance_style_filters, dance_style_field_name):
            continue

        entity_name_data = data.get(entity_name_field, "").lower()
        entity_name_tokens = entity_name_data.split()

        if filter_by_query(query_tokens, entity_name_tokens):
            results[data_id] = data

    logging.info(f"Total results found: {len(results)}")
    return results
