# gunicorn_config.py
import threading
from sample.views import getsquare
from djApi.processor import update_cache
import djApi.flags as flags
import time
import logging

logging.basicConfig(level=logging.INFO)

def on_starting(server):
    logging.info("gunicorn")
    flags.init_firebase()
    cache_update_thread = threading.Thread(target=update_cache_periodically)
    cache_update_thread.daemon = True
    cache_update_thread.start()

def update_cache_periodically():
    while True:
        update_cache()
        time.sleep(flags.CACHE_UPDATE_INTERVAL)  # Sleep for 10 minutes
