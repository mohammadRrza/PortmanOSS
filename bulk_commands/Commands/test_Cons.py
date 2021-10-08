import pika
from get_massage import get_massage
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))

channel = connection.channel()

channel.queue_declare('echo')

channel.basic_consume(queue='echo', on_message_callback=get_massage, auto_ack=True)

channel.start_consuming()

