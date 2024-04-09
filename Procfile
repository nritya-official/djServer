web: gunicorn djServer.wsgi --config gunicorn_config.py
worker: celery -A djServer worker --loglevel=info
beat: celery -A djServer beat --loglevel=info