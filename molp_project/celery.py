import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'molp_project.settings')

app = Celery('molp_project')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.task_track_started = True

app.conf.beat_schedule = {
    'get_tasks_1s': {
        'task': 'molp_app.utilities.scalarization.get_tasks_info',
        'schedule': 0.5
    },
    'get_user_tasks_1s': {
        'task': 'molp_app.utilities.scalarization.get_user_tasks_info',
        'schedule': 0.5
    }
}

app.autodiscover_tasks()
