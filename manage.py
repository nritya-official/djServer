#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import threading
import time
from sample.views import getsquare
from djApi.processor import update_cache
import djApi.flags as flags
import logging
logging.basicConfig(level=logging.INFO)  # Set the desired logging level


def update_cache_periodically():
    while True:
        update_cache()
        time.sleep(flags.CACHE_UPDATE_INTERVAL)  # Sleep for 10 minutes

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djServer.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # Start the caching thread
    if(sys.argv[1]=='runserver'):
        print("Running server so threading for cache")
        logging.info("Threading for cache..")
        flags.init_firebase()
        cache_update_thread = threading.Thread(target=update_cache)
        cache_update_thread.daemon = True
        cache_update_thread.start()

    print("Running manage.py with ",sys.argv," calling execute from command line.")
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
