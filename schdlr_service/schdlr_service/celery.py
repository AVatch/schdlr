from __future__ import absolute_import

import os

from celery import Celery

# set the default Django settings module for hte 'celery' program
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'schdlr_service.settings')

from django.conf import settings

app = Celery('schdlr_service')

app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
