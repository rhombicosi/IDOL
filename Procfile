web: daphne molp_project.asgi:application --port $PORT --bind 0.0.0.0 -v2
worker: celery -A molp_project worker -l INFO
beat: celery -A molp_project beat -l INFO