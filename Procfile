web: sh -c 'python manage.py migrate && python manage.py collectstatic && gunicorn sg_attractions_outings.wsgi'   
worker: python manage.py celery -A sg_attractions_outings worker -B --loglevel=info