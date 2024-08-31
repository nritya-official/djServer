import firebase_admin.firestore
import json
from fuzzywuzzy import fuzz
import redis
import logging
from django.core.cache import cache
from djApi.flags import FIREBASE_DB, COLLECTIONS
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

def autocomplete(cache, query):
    results = []

    for key in cache.keys():
        if query.lower() in key.lower():
            results.append(key)

    return results



collection_name_field ={
    COLLECTIONS.STUDIO : 'studioName',
    COLLECTIONS.WORKSHOPS : 'workshopName',
    COLLECTIONS.OPENCLASSES : 'openClassName',
    COLLECTIONS.COURSES : 'workshopName'
}


collection_danceStyles_field ={
    COLLECTIONS.STUDIO : 'danceStyles',
    COLLECTIONS.WORKSHOPS : 'danceStyles',
    COLLECTIONS.OPENCLASSES : 'danceStyle',
    COLLECTIONS.COURSES : 'danceStyles'
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

    if entity != COLLECTIONS.STUDIO:
        entity_level = data.get("level", "All").lower()
        if entity_level == "all" or entity_level in level_filters:
            return True

    return False


def filter_by_price(data, price_filter, entity):
    if price_filter and entity in [COLLECTIONS.WORKSHOPS, COLLECTIONS.COURSES]:
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

def full_text_search(query, dance_style='', cache={}, entity=COLLECTIONS.STUDIO, level="All", price=10**10):
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

        if entity != COLLECTIONS.STUDIO:
            if not filter_by_level(data, level_filter, entity):
                continue

        if entity in [COLLECTIONS.WORKSHOPS,COLLECTIONS.OPENCLASSES]:
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
