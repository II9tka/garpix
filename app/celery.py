import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

app = Celery('app', broker='redis://redis:6379/0',)
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    # Executes everyday at 00:00

    'send_notification': {
        'task': 'backend.album.tasks.send_message',
        'schedule': crontab(minute=0, hour=3),
    },
}

