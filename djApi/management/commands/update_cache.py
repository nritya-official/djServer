from django.core.management.base import BaseCommand, CommandError
import firebase_admin.firestore
from firebase_admin import credentials, firestore, firestore_async,storage
import json
from fuzzywuzzy import fuzz
import redis
from django.core.cache import cache
from djApi.flags import FIREBASE_DB,FIREBASE_CREDENTIALS,STORAGE_BUCKET
from geopy.distance import geodesic
import time
import datetime
import logging

logging.basicConfig(level=logging.INFO)

    

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
    logging.info("Cache updating....")
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
        path = "StudioIcon/{}/".format(doc.id)
        logging.info(path)
        blobs = STORAGE_BUCKET.list_blobs(prefix=path, delimiter="/")
        signed_urls = []

        if blobs:
            for blob in blobs:
                signed_url = blob.generate_signed_url(datetime.timedelta(seconds=800), method='GET')
                signed_urls.append(signed_url)
        logging.info(signed_urls)
        if(len(signed_urls)>0):
            data["studioIconUrl"]=signed_urls
        else:
            data["studioIconUrl"]=""
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
    
    last_updated_time = time.time()  # Get current time in seconds since epoch
    rc.set("last_updated_gmt", last_updated_time)
    
    logging.info("Cache updated successfully")
