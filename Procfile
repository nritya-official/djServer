release: python manage.py migrate
web: gunicorn djServer.wsgi --config gunicorn_config.py
worker: celery -A emailer.tasks worker --loglevel=info