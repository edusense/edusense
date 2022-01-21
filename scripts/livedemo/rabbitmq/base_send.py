#!/usr/bin/env python
import pika
import sys
import json
import time

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='livedemo_exchange', exchange_type='direct')

i=0
while(True):
    message = {'message_number':i}
    channel.basic_publish(
        exchange='livedemo_exchange', routing_key='livedemo_test', body=json.dumps(message))
    print(" [x] Sent %r" % (message))
    time.sleep(1)
    i+=1
connection.close()