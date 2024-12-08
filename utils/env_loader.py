import os
from dotenv import load_dotenv
import json

def get_firebase_config_production():
    firebase_config_json = os.environ.get("firebase_keys_production")
    if firebase_config_json:
        return json.loads(firebase_config_json)
    else:
        return os.path.join(os.path.dirname(__file__), "config_firebase_production.json")

def get_firebase_config_staging():
    firebase_config_json = os.environ.get("firebase_keys_staging")
    if firebase_config_json:
        return json.loads(firebase_config_json)
    else:
        return os.path.join(os.path.dirname(__file__), "config_firebase_staging.json")

def base_web_url():
    dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.env"))
    load_dotenv(dotenv_path=dotenv_path)
    environment = os.getenv("ENVIRONMENT", "staging").lower()
    if environment == "production":
        return 'https://www.nritya.co.in/nritya-webApp'
    else:
        return 'https://nritya-official.github.io/nritya-webApp'


def load_environment():
    """Load environment variables and return configuration values."""
    dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.env"))
    load_dotenv(dotenv_path=dotenv_path)
    environment = os.getenv("ENVIRONMENT", "staging").lower()

    if environment == "production":
        return {
            "STORAGE_BUCKET_NAME": "nritya-production.firebasestorage.app",
            "REDIS_CONFIG_FILE": os.path.join(os.path.dirname(__file__), "config_redis_production.json"),
            "FIREBASE_CONFIG_FILE": get_firebase_config_production(),
            "ENVIRONMENT": environment,
        }
    else:
        return {
            "STORAGE_BUCKET_NAME": "nritya-7e526.appspot.com",
            "REDIS_CONFIG_FILE": os.path.join(os.path.dirname(__file__), "config_redis_staging.json"),
            "FIREBASE_CONFIG_FILE": get_firebase_config_staging(),
            "ENVIRONMENT": environment,
        }
