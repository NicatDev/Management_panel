from __future__ import absolute_import
from __future__ import unicode_literals

import logging
import os

from celery import Celery
from datetime import timedelta
from django.conf import settings

from dotenv import load_dotenv
from app import settings as app_settings

# load_dotenv(os.path.join(app_settings.BASE_DIR, ".env"))

logger = logging.getLogger("Celery")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")

app = Celery("app")

app.config_from_object("django.conf:settings", namespace="CELERY")


app.autodiscover_tasks(lambda: app_settings.INSTALLED_APPS)
app.autodiscover_tasks()

# app.conf.beat_schedule = {
#     'check_task_deadlines': {
#         'task': 'workspace.tasks.check_task_deadlines',
#         'schedule': timedelta(seconds=60), # Run every minute by default
#     },
# }

@app.task(bind=True)
def debug_task(self):
    print("Request: {0!r}".format(self.request))


if settings.PROD:
    app.conf.update(
        BROKER_URL='redis://:{password}@redis:6379/0'.format
        (password='dKqs72RhtaPPYyfN'
         ),
        CELERYBEAT_SCHEDULER='django_celery_beat.schedulers:DatabaseScheduler',
        CELERY_RESULT_BACKEND='redis://:{password}@redis:6379/1'.format(
            password='dKqs72RhtaPPYyfN'
        ),
        CELERY_DISABLE_RATE_LIMITS=True,
        CELERY_ACCEPT_CONTENT=['json', ],
        CELERY_TASK_SERIALIZER='json',
        CELERY_RESULT_SERIALIZER='json',
    )
else:
    app.conf.update(
#         BROKER_URL='redis://localhost:6379/0',
        CELERYBEAT_SCHEDULER='django_celery_beat.schedulers:DatabaseScheduler',
#         CELERY_RESULT_BACKEND='redis://localhost:6379/1',
#         CELERY_DISABLE_RATE_LIMITS=True,
#         CELERY_ACCEPT_CONTENT=['json', ],
#         CELERY_TASK_SERIALIZER='json',
#         CELERY_RESULT_SERIALIZER='json',
    )
