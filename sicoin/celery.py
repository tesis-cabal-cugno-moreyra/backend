from __future__ import absolute_import

import os
import time

from celery import Celery
from django.conf import settings

import configurations

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sicoin.config')
os.environ.setdefault('DJANGO_CONFIGURATION', 'Production')

configurations.setup()

app = Celery('sicoin')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    time.sleep(120)
    print('jahsgvdjlkhavsdujhasd')
