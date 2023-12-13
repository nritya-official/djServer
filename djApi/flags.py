import firebase_admin
from firebase_admin import credentials, firestore


CACHE_UPDATE_INTERVAL = 3600
FIREBASE_CREDENTIALS = credentials.Certificate('djApi/config.json')
FIREBASE_APP = None

def init_firebase():
    global FIREBASE_APP
    FIREBASE_APP = firebase_admin.initialize_app(FIREBASE_CREDENTIALS)