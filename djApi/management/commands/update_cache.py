from django.core.management.base import BaseCommand, CommandError
import firebase_admin.firestore
from firebase_admin import credentials, firestore, firestore_async,storage
import json
from fuzzywuzzy import fuzz
import redis
from django.core.cache import cache
from utils.flags import (FIREBASE_CREDENTIALS, STORAGE_BUCKET, get_redis_host, 
            get_redis_port, get_redis_username, get_redis_password)
from utils.common_utils import COLLECTIONS, STORAGE_FOLDER
from geopy.distance import geodesic
import time
import datetime
import logging

logging.basicConfig(level=logging.INFO)

collection_fields = {
    COLLECTIONS.STUDIO : ['city', 'avgRating', 'status', 'isPremium', 'danceStyles', 'state', 'studioName', 'UserId', 'geolocation', 'street','youtubeViedoLink'],
    COLLECTIONS.WORKSHOPS : ['city', 'workshopName', 'time', 'date', 'level', 'danceStyles','StudioId','price','youtubeViedoLink'],
    COLLECTIONS.OPENCLASSES : ['city', 'date', 'active', 'danceStyles', 'level', 'time', 'venue', 'openClassName','StudioId','price','youtubeViedoLink'],
    COLLECTIONS.COURSES : ['city', 'date', 'level', 'workshopName','courseName','venue', 'time', 'danceStyles','StudioId','price','youtubeViedoLink']
}

collection_icon ={
    COLLECTIONS.STUDIO : 'StudioIcon',
    COLLECTIONS.WORKSHOPS : 'WorkshopIcon',
    COLLECTIONS.OPENCLASSES : 'OpenClassIcon',
    COLLECTIONS.COURSES : 'CourseIcon'
}

collection_name_field ={
    COLLECTIONS.STUDIO : 'studioName',
    COLLECTIONS.WORKSHOPS : 'workshopName',
    COLLECTIONS.OPENCLASSES : 'openClassName',
    COLLECTIONS.COURSES : 'workshopName'
}

class Command(BaseCommand):
    logging.info('Updating cache')
    help = 'Manages cache updation'
    logging.info(FIREBASE_CREDENTIALS)
    logging.info(STORAGE_BUCKET)
    def handle(self, *args, **options):
        interval = 5
        logging.info(f'Scheduling cache update every {interval} minutes...')
        x=2
        while x:
            x = x-1
            try:
                rc = redis.Redis(
                    host=get_redis_host(), port=get_redis_port(),
                    username=get_redis_username(), # use your Redis user. More info https://redis.io/docs/management/security/acl/
                    password=get_redis_password(), # use your Redis password
                    )
                #rc.set("foo","bar")

        
                logging.info("Shared task")
                update_cache(rc)
                rc.close()

                time.sleep(interval * 60)  
                if(x==0):
                    return
            except Exception as e:
                self.stdout.write(self.style.ERROR(str(e)))
                time.sleep(60)  

def update_cache(rc):
    logging.info("Cache updating from management....")
    logging.info(rc.keys('*'))
    if not firebase_admin._apps:
        # Initialize Firebase with your credentials
        #cred = credentials.Certificate(FIREBASE_CREDENTIALS)
        firebase_admin.initialize_app(FIREBASE_CREDENTIALS)
    
    if not globals().get('STORAGE_BUCKET'):
        app = firebase_admin.initialize_app(FIREBASE_CREDENTIALS, {
            'storageBucket': 'nritya-7e526.appspot.com',
        }, name='storage')
        globals()['STORAGE_BUCKET'] = storage.bucket(app=app)

    db = firebase_admin.firestore.client()
    collections = [COLLECTIONS.STUDIO, COLLECTIONS.WORKSHOPS, COLLECTIONS.OPENCLASSES, COLLECTIONS.COURSES]
    
    for collection in collections:
        process_collection(collection, collection_fields[collection], rc,db)

def process_collection(collection_name, allowed_fields, rc, db):
    logging.info(f"Processing collection: {collection_name} with allowed fields {allowed_fields}....")
    
    docs = db.collection(collection_name).stream()
    data_source = {}
    city_item_names = {}

    for doc in docs:
        data = {}
        min_fee = float('inf')  # Set min_fee to a large value initially
        free_trial_available = False  # Initialize freeTrialAvailable as False
        
        for field, value in doc.to_dict().items():
            if field in allowed_fields:
                if isinstance(value, firebase_admin.firestore.DocumentReference):
                    data[field] = value.id
                else:
                    data[field] = value

            if collection_name == COLLECTIONS.STUDIO and field == 'tableData':
                table_data = value  

                for key, class_data in table_data.items():
                    fee_value = class_data.get('fee')
                    if fee_value and fee_value.isdigit():
                        fee = int(fee_value)
                        if fee < min_fee:
                            min_fee = fee

                    if class_data.get('freeTrial', False):
                        free_trial_available = True

        if collection_name == COLLECTIONS.STUDIO:
            data['minFee'] = min_fee if min_fee != float('inf') else None
            data['freeTrialAvailable'] = free_trial_available


        data["id"] = doc.id  # Use a common key for document ID
        path = f"{collection_icon[collection_name]}/{doc.id}/"
        blobs = STORAGE_BUCKET.list_blobs(prefix=path, delimiter="/")
        signed_urls = []

        if blobs:
            for blob in blobs:
                signed_url = blob.generate_signed_url(datetime.timedelta(seconds=800), method='GET')
                signed_urls.append(signed_url)
        
        if signed_urls:
            data["iconUrl"] = signed_urls[0]
        else:
            data["iconUrl"] = ""

        city = data.get("city", "")
        if city:
            if city not in data_source:
                data_source[city] = {}
            data_source[city][data["id"]] = data  # Store data with entity ID as the key

            item_name = data.get(collection_name_field[collection_name], "")
            if item_name:
                if city not in city_item_names:
                    city_item_names[city] = {}
                city_item_names[city][data["id"]] = item_name 

    # Save data as hashes in Redis
    for city, items in data_source.items():
        items_str = {str(key): json.dumps(value) for key, value in items.items()}
        rc.hset(f"{city.lower()}-{collection_name}", mapping=items_str)


    # Save city item names as hashes in Redis
    for city, item_names in city_item_names.items():
        item_names_str = {str(key): str(value) for key, value in item_names.items()}
        rc.hset(f"{city.lower()}-{collection_name}-Lite", mapping=item_names_str)

    
    last_updated_time = time.time()
    rc.set(f"last_updated_{collection_name.lower()}", last_updated_time)
    
    logging.info(f"Cache for collection {collection_name} updated successfully.")
