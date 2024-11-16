import firebase_admin
import json
from firebase_admin import credentials, firestore, firestore_async,storage, auth
from celery import Celery
import os
from utils.env_loader import load_environment

env_config = load_environment()
STORAGE_BUCKET_NAME = env_config["STORAGE_BUCKET_NAME"]
REDIS_CONFIG_FILE = env_config["REDIS_CONFIG_FILE"]
FIREBASE_CONFIG_FILE = env_config["FIREBASE_CONFIG_FILE"]
ENVIRONMENT = env_config["ENVIRONMENT"]
print(ENVIRONMENT,"<->",STORAGE_BUCKET_NAME,"<->",REDIS_CONFIG_FILE,"<->",FIREBASE_CONFIG_FILE)

with open(REDIS_CONFIG_FILE) as config_file:
    config = json.load(config_file)

REDIS_HOST = config["REDIS_HOST"]
REDIS_PORT = config["REDIS_PORT"]
REDIS_USERNAME = config["REDIS_USERNAME"]
REDIS_PASSWORD = config["REDIS_PASSWORD"]
CELERY_BROKER_URL = f'redis://{REDIS_USERNAME}:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/0'

CACHE_UPDATE_INTERVAL = 600
FIREBASE_CREDENTIALS = credentials.Certificate(FIREBASE_CONFIG_FILE)
FIREBASE_APP = None
FIREBASE_DB = None
STORAGE_BUCKET =  None
FIREBASE_AUTH = None
CELERY_APP = None

def init_firebase():
    env_config = load_environment()
    STORAGE_BUCKET_NAME = env_config["STORAGE_BUCKET_NAME"]
    REDIS_CONFIG_FILE = env_config["REDIS_CONFIG_FILE"]
    FIREBASE_CONFIG_FILE = env_config["FIREBASE_CONFIG_FILE"]
    ENVIRONMENT = env_config["ENVIRONMENT"]
    print(ENVIRONMENT,"<->",STORAGE_BUCKET_NAME,"<->",REDIS_CONFIG_FILE,"<->",FIREBASE_CONFIG_FILE)
    global FIREBASE_APP
    FIREBASE_APP = firebase_admin.initialize_app(FIREBASE_CREDENTIALS)
    global FIREBASE_DB
    FIREBASE_DB = firestore.client()
    app = firebase_admin.initialize_app(FIREBASE_CREDENTIALS, {
        'storageBucket': STORAGE_BUCKET_NAME, 
    }, name='storage')

    global STORAGE_BUCKET 
    STORAGE_BUCKET = storage.bucket(app=app)

    global FIREBASE_AUTH
    FIREBASE_AUTH = auth

    global CELERY_APP
    CELERY_APP =  Celery('tasks', broker= CELERY_BROKER_URL)

def get_celery_broker_url():
    env_config = load_environment()
    REDIS_CONFIG_FILE = env_config["REDIS_CONFIG_FILE"]
    with open(REDIS_CONFIG_FILE) as config_file:
        config = json.load(config_file)
    return config["CELERY_BROKER_URL"]

def get_redis_host():
    env_config = load_environment()
    REDIS_CONFIG_FILE = env_config["REDIS_CONFIG_FILE"]  
    with open(REDIS_CONFIG_FILE) as config_file:
        config = json.load(config_file)
    return config["REDIS_HOST"]

def get_redis_port():
    env_config = load_environment()
    REDIS_CONFIG_FILE = env_config["REDIS_CONFIG_FILE"]
    with open(REDIS_CONFIG_FILE) as config_file:
        config = json.load(config_file)
    return config["REDIS_PORT"]

def get_redis_username():
    env_config = load_environment()
    REDIS_CONFIG_FILE = env_config["REDIS_CONFIG_FILE"]
    with open(REDIS_CONFIG_FILE) as config_file:
        config = json.load(config_file)
    return config["REDIS_USERNAME"]

def get_redis_password():
    env_config = load_environment()
    REDIS_CONFIG_FILE = env_config["REDIS_CONFIG_FILE"]
    with open(REDIS_CONFIG_FILE) as config_file:
        config = json.load(config_file)
    return config["REDIS_PASSWORD"]

def get_env():
    env_config = load_environment()
    return env_config["ENVIRONMENT"]