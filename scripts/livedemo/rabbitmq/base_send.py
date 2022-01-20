#!/usr/bin/env python
import pika
import sys

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='livedemo_exchange', exchange_type='direct')

message = 'INFO:Hello World!'
channel.basic_publish(
    exchange='livedemo_exchange', routing_key='livedemo_test', body=message)
print(" [x] Sent %r" % (message))
connection.close()