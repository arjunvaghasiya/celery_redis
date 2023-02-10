from __future__ import absolute_import,unicode_literals
import os
from celery import Celery
from django.conf import settings
from celery.schedules import crontab
os.environ.setdefault('DJANGO_SETTINGS_MODULE','celery_redis.settings')

app  = Celery('celery_redis')
app.conf.enable_utc = False
app.conf.update(timezone = 'Asia/Kolkata')
app.config_from_object('django.conf:settings',namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    # 'send-mail-every-user': {
    #     'task' : 'website.tasks.send_email_everyuser',
    #     'schedule' : crontab(hour=10,minute=23),
    # },
    'Top-update-at-every-two-minutes':{
        'task' : 'website.tasks.top_update',
        'schedule' : crontab(minute='*/2'),
    },
        'Top-DB-backup-after-every-ten-minutes':{
        'task' : 'website.tasks.db_backup',
        'schedule' : crontab(minute='*/10'),
    }
}

app.conf.update(CELERY_ACCEPT_CONTENT=["json"],
                CELERY_TASK_SERIALIZER="json",
                CELERY_RESULT_SERIALIZER="json")
@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}') 