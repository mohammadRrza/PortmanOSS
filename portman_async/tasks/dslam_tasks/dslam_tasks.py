from celery import shared_task
import pika


@shared_task()
def get_zyxel_ports_info():
    pass
