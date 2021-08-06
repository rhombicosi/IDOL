# Django settings
import os
from django.conf import settings
# Celery app
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'molp_project.settings')

app = Celery('molp_project')

# namespace='CELERY' means all celery-related configuration keys
# should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.task_track_started = True

app.conf.beat_schedule = {
    'get_tasks_1s': {
        'task': 'molp_app.utilities.scalarization.get_tasks_info',
        'schedule': 1.0
    },
    'get_user_tasks_1s': {
        'task': 'molp_app.utilities.scalarization.get_user_tasks_info',
        'schedule': 1.0
    }
}

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
