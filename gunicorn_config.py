# gunicorn_config.py
import threading
from djApi.processor import update_cache
import djApi.flags as flags
import redis
import time
import logging

logging.basicConfig(level=logging.INFO)


def on_starting(server):
    logging.info("gunicorn server started for nritya")
    flags.init_firebase()

