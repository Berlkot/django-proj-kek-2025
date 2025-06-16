# animals/celery.py
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "animals.settings")

app = Celery("animals")

app.config_from_object("django.conf:settings", namespace="CELERY")


app.conf.beat_schedule = {
    'archive-old-ads-every-day': {
        'task': 'siteapp.tasks.archive_old_advertisements',
        'schedule': crontab(minute='0', hour='3'),
    },
    'send-weekly-digest-every-monday': {
        'task': 'siteapp.tasks.send_weekly_digest',
        'schedule': crontab(minute='0', hour='8', day_of_week='monday'),
        'args': (),
    },
}


app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    """
    Простая отладочная задача.
    """
    print(f'Request: {self.request!r}')