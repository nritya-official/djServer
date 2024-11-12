# gunicorn_config.py
import threading
import utils.flags as flags
import redis
import time
import logging

logging.basicConfig(level=logging.INFO)


def on_starting(server):
    logging.info("gunicorn server started for nritya")
    flags.init_firebase()

