"""import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))

channel = connection.channel()

channel.queue_declare('echo')

channel.basic_publish(exchange='', routing_key='echo', body='Hello World')

connection.close()"""




