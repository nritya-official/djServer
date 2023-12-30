import firebase_admin.firestore
import json
from fuzzywuzzy import fuzz
import redis
import logging
from django.core.cache import cache

logging.basicConfig(level=logging.INFO)

#cache = {}
def update_cache(rc):
    print("Cache updating....")
    logging.info("Cache updating...")

    try:
        db = firebase_admin.firestore.client()
        docs = db.collection('Studio').stream()
        data_source = {}

        for doc in docs:
            data = {}
            for field, value in doc.to_dict().items():
                if isinstance(value, firebase_admin.firestore.DocumentReference):
                    data[field] = value.id
                else:
                    data[field] = value
            data["studioId"]=doc.id
            data_source[doc.id] = data
            #data_source[doc.id].data["studioId"]=doc.id

        data_source_json = json.dumps(data_source)
        rc.set('studio_data', data_source_json)  
        print("Cache updated successfully")
        logging.info("Cache updated successfully")
    except Exception as e:
        print("Error updating cache:", e)
        logging.error("Error updating cache : ",e)

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

def full_text_search(query, city='', dance_style='',cache={}):
    print(query)
    results = []
    query_tokens = query.lower().split()  # Tokenize search query

    for key, data in cache.items():
        # Check if both the city and danceStyle filters are satisfied
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
            if len(query_tokens) == 0:
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

