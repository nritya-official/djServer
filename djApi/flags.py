import firebase_admin
from firebase_admin import credentials, firestore, firestore_async


CACHE_UPDATE_INTERVAL = 600
FIREBASE_CREDENTIALS = credentials.Certificate('djApi/config.json')
FIREBASE_APP = None
FIREBASE_DB = None
class COLLECTIONS:
    USER = 'User'
    STUDIO = 'Studio'
    FREE_TRIAL_BOOKINGS = 'FreeTrialBookings'
    INSTRUCTORS = 'Instructors'

class nSuccessCodes:
    CREATED = 201
    ALREADY_BOOKED = 202



def init_firebase():
    global FIREBASE_APP
    FIREBASE_APP = firebase_admin.initialize_app(FIREBASE_CREDENTIALS)
    global FIREBASE_DB
    FIREBASE_DB = firestore.client()