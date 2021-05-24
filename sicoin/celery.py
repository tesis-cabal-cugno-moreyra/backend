# import os
#
# from celery import Celery
# import configurations
# from django.conf import settings
#
# # set the default Django settings module for the 'celery' program.
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sicoin.config')
# os.environ.setdefault('DJANGO_CONFIGURATION', 'Local')
#
# configurations.setup()
#
# app = Celery('sicoin')
#
# # Using a string here means the worker doesn't have to serialize
# # the configuration object to child processes.
# # - namespace='CELERY' means all celery-related configuration keys
# #   should have a `CELERY_` prefix.
# app.config_from_object('django.conf:settings', namespace='CELERY')
# app.conf
#
# import ipdb
# ipdb.set_trace()
#
# app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
#
#
# @app.task(bind=True)
# def debug_task(self):
#     print(f'Request: {self.request!r}')

from __future__ import absolute_import

import os

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
    print('Request: {0!r}'.format(self.request))
