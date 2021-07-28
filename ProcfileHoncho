web: daphne molp_project.asgi:application
worker1: celery -A molp_project worker -l INFO
beat: celery -A molp_project beat -l INFO