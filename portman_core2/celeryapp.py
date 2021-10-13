from celery import Celery
from . import celeryconfig

app = Celery('portman_core2')
app.config_from_object(celeryconfig)

if __name__ == '__main__':
    app.start()
