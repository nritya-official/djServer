web: gunicorn djServer.wsgi --config gunicorn_config.py
worker: celery worker -A djServer -l info