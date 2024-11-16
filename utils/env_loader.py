import os
from dotenv import load_dotenv

def load_environment():
    """Load environment variables and return configuration values."""
    dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.env"))
    load_dotenv(dotenv_path=dotenv_path)
    environment = os.getenv("ENVIRONMENT", "staging").lower()

    if environment == "production":
        return {
            "STORAGE_BUCKET_NAME": "nritya-production.appspot.com",
            "REDIS_CONFIG_FILE": os.path.join(os.path.dirname(__file__), "config_redis_production.json"),
            "FIREBASE_CONFIG_FILE": os.path.join(os.path.dirname(__file__), "config_firebase_production.json"),
            "ENVIRONMENT": environment,
        }
    else:
        return {
            "STORAGE_BUCKET_NAME": "nritya-7e526.appspot.com",
            "REDIS_CONFIG_FILE": os.path.join(os.path.dirname(__file__), "config_redis_staging.json"),
            "FIREBASE_CONFIG_FILE": os.path.join(os.path.dirname(__file__), "config_firebase_staging.json"),
            "ENVIRONMENT": environment,
        }
