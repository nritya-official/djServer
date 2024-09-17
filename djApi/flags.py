import firebase_admin
from firebase_admin import credentials, firestore, firestore_async,storage, auth


CACHE_UPDATE_INTERVAL = 600
FIREBASE_CREDENTIALS = credentials.Certificate('djApi/config.json')
FIREBASE_APP = None
FIREBASE_DB = None
STORAGE_BUCKET =  None
FIREBASE_AUTH = None

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