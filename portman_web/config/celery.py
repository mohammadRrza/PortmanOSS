import os
import sys

from celery import Celery
from django.core.wsgi import get_wsgi_application
# Set the default Django settings module for the 'celery' program.
sys.path.append('/opt/portmanv3/portman_web/')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
application = get_wsgi_application()

app = Celery('portman_async')
app.config_from_object('django.conf:settings', namespace='CELERY')


# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')