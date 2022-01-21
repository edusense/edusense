#!/usr/bin/env python
import pika
import sys
credentials = pika.PlainCredentials('prasoon', 'edusenseMQ')
parameters = pika.ConnectionParameters('sensei-delta.wv.cc.cmu.edu',
                                   5672,
                                   '/',
                                   credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

# channel.exchange_declare(exchange='livedemo_exchange', exchange_type='direct')

# result = channel.queue_declare(queue='livedemo_test')
# queue_name = result.method.queue

channel.queue_declare(queue='livedemo_test')


# channel.queue_bind(
#         exchange='livedemo_exchange', queue=queue_name, routing_key='livedemo_test')

print(' [*] Waiting for logs. To exit press CTRL+C')


def callback(ch, method, properties, body):
    print(" [x] %r:%r" % (method.routing_key, body))


channel.basic_consume(
    queue='livedemo_test', on_message_callback=callback, auto_ack=True)

channel.start_consuming()