web: python manage.py migrate && gunicorn sg_attractions_outings.wsgi 
worker: celery -A sg_attractions_outings worker -B --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler