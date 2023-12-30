# gunicorn_config.py
import threading
from sample.views import getsquare
from djApi.processor import update_cache
import djApi.flags as flags
import redis
import time
import logging

logging.basicConfig(level=logging.INFO)

rc = redis.Redis(
    host="redis-11857.c276.us-east-1-2.ec2.cloud.redislabs.com", port=11857,
    username="default", # use your Redis user. More info https://redis.io/docs/management/security/acl/
    password="Fw82cxCVcMZED9ubfJVxeuSqcCb1vFqi", # use your Redis password
    )

def on_starting(server):
    logging.info("gunicorn")
    flags.init_firebase()
    cache_update_thread = threading.Thread(target=update_cache_periodically)
    cache_update_thread.daemon = True
    cache_update_thread.start()

def update_cache_periodically():
    while True:
        update_cache(rc)
        time.sleep(flags.CACHE_UPDATE_INTERVAL)  # Sleep for 10 minutes
