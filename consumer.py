#!/usr/bin/env python
import pika, sys, os
import requests


def main():
    parameters = pika.connection.URLParameters("amqp://consumer1:newpassword2@localhost:5672/")
   # parameters= pika.ConnectionParameters(host='localhost')
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    def callback(ch, method, properties, body):
        print(" [x] Received %r" % body.decode())
        r = requests.get("http://localhost:5000/api/ping")
        print(r.text)
        print(" [x] Done")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue='client.jobs.write', on_message_callback=callback)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)