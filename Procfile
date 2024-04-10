release: python manage.py migrate
web: gunicorn djServer.wsgi --config gunicorn_config.py
worker: python manage.py update_cache 5