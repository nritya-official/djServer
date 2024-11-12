release: python manage.py migrate
web: gunicorn djServer.wsgi:application --config gunicorn_config.py --env DJANGO_ENV=staging
worker: celery -A emailer.tasks worker --loglevel=info