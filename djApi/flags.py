import firebase_admin
from firebase_admin import credentials, firestore, firestore_async,storage, auth
from celery import Celery

REDIS_HOST = 'redis-11857.c276.us-east-1-2.ec2.cloud.redislabs.com'
REDIS_PORT = 11857
REDIS_USERNAME = 'default'  # Use the correct Redis user
REDIS_PASSWORD = 'Fw82cxCVcMZED9ubfJVxeuSqcCb1vFqi'  # Use your Redis password

CELERY_BROKER_URL = f'redis://{REDIS_USERNAME}:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/0'

CACHE_UPDATE_INTERVAL = 600
FIREBASE_CREDENTIALS = credentials.Certificate('djApi/config.json')
FIREBASE_APP = None
FIREBASE_DB = None
STORAGE_BUCKET =  None
FIREBASE_AUTH = None
CELERY_APP = None

class COLLECTIONS:
    USER = 'User'
    STUDIO = 'Studio'
    COURSES = 'Courses'
    OPENCLASSES = 'OpenClasses'
    WORKSHOPS = 'Workshops'
    BOOKINGS = 'Bookings'
    RATINGS = 'Ratings'
    USER_KYC = 'UserKyc'
    TRANSACTIONS = 'Transactions'
    FREE_TRIAL_BOOKINGS = 'FreeTrialBookings'
    INSTRUCTORS = 'Instructors'

class STORAGE_FOLDER:
    STUDIO_IMAGES = 'StudioImages'
    STUDIO_ANNOUNCEMENTS = 'StudioAnnouncements'
    STUDIO_ICON = 'StudioIcon'

class nSuccessCodes:
    CREATED = 201
    ALREADY_BOOKED = 202

def init_firebase():
    global FIREBASE_APP
    FIREBASE_APP = firebase_admin.initialize_app(FIREBASE_CREDENTIALS)
    global FIREBASE_DB
    FIREBASE_DB = firestore.client()
    app = firebase_admin.initialize_app(FIREBASE_CREDENTIALS, {
        'storageBucket': 'nritya-7e526.appspot.com', 
    }, name='storage')

    global STORAGE_BUCKET 
    STORAGE_BUCKET = storage.bucket(app=app)

    global FIREBASE_AUTH
    FIREBASE_AUTH = auth

    global CELERY_APP
    CELERY_APP =  Celery('tasks', broker= CELERY_BROKER_URL)