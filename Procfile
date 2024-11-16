release: python manage.py migrate
web: gunicorn djServer.wsgi:application --config gunicorn_config.py
worker: celery -A emailer.tasks worker --loglevel=info