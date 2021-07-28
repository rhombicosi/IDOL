release: python manage.py migrate
web: daphne molp_project.asgi:application --port $PORT --bind 0.0.0.0 -v2
worker1: celery -A molp_project worker -l INFO
worker2: python manage.py runworker channels --settings=core.settings -v2
beat: celery -A molp_project beat -l INFO