release: python manage.py migrate
web: gunicorn djServer.wsgi --config gunicorn_config.py
cache_updation: python manage.py update_cache 5