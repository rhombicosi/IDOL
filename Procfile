web: gunicorn molp_project.asgi:channel_layer $PORT --bind 0.0.0.0 -v2
worker: celery -A molp_project worker -l INFO
beat: celery -A molp_project beat -l INFO