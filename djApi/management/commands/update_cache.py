from django.core.management.base import BaseCommand, CommandError
import firebase_admin.firestore
from firebase_admin import credentials, firestore, firestore_async,storage
import json
from fuzzywuzzy import fuzz
import redis
from django.core.cache import cache
from djApi.flags import FIREBASE_DB, FIREBASE_CREDENTIALS, STORAGE_BUCKET, COLLECTIONS
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
    help = 'Manages cache updation'

    def handle(self, *args, **options):
        interval = 5
        logging.info(f'Scheduling cache update every {interval} minutes...')
        x=2
        while x:
            x = x-1
            try:
                rc = redis.Redis(
                    host="redis-11857.c276.us-east-1-2.ec2.cloud.redislabs.com", port=11857,
                    username="default", # use your Redis user. More info https://redis.io/docs/management/security/acl/
                    password="Fw82cxCVcMZED9ubfJVxeuSqcCb1vFqi", # use your Redis password
                    )
                rc.set("foo","bar")

        
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
        if collection_name == COLLECTIONS.STUDIO:
            print(data)
        if signed_urls:
            data["iconUrl"] = signed_urls[0]
        else:
            data["iconUrl"] = ""

        city = data.get("city", "")
        if city:
            if city not in data_source:
                #data_source[city] = []
                data_source[city] = {None:None}
            #data_source[city].append(data)
            data_source[city][data["id"]] = data

            item_name = data.get(collection_name_field[collection_name], "")
            if item_name:
                if city not in city_item_names:
                    city_item_names[city] = {None:None}
                city_item_names[city][data["id"]] = item_name 

    for city, items in data_source.items():
        rc.set(f"{city.lower()}-{collection_name}", json.dumps(items))

    for city, item_names in city_item_names.items():
        logging.info(f"{city.lower()}-{collection_name}-Lite")
        logging.info(item_names)
        rc.set(f"{city.lower()}-{collection_name}-Lite", json.dumps((item_names)))
    
    last_updated_time = time.time()
    rc.set(f"last_updated_{collection_name.lower()}", last_updated_time)
    
    logging.info(f"Cache for collection {collection_name} updated successfully.")

