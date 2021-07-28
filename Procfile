web: gunicorn molp_project.wsgi
worker: celery -A molp_project worker -l INFO
beat: celery -A molp_project beat -l INFO