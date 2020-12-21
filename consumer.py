#!/usr/bin/env python
import pika, sys, os
import requests
import ast
import json

TEST_USERNAME = 'RFI Github'
TEST_PASSWORD = '!xk8wa>cb4'
SCICAT_URL = 'http://localhost/api/v3/'
HANCOCK_URL = 'http://localhost:5000/api/'

def make_headers(jwt):
    return {'Authorization': 'Bearer {}'.format(jwt)}

def main():
    parameters = pika.connection.URLParameters("amqp://consumer1:newpassword2@localhost:5672/")
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    def callback(ch, method, properties, body):
        print(" [x] Received from rabbitmq" )
        body = ast.literal_eval(body.decode())
        print("retrieving info from Scicat....")
        # get info from Scicat
        r = requests.post(SCICAT_URL + 'Users/login', json=dict(username='ingestor', password='aman'))
        scicat_token = r.json()['id']
        if body is not None:
            query = json.dumps({"where": {"pid": f"{body['datasetList'][0]['pid']}"}})
            r = requests.get(SCICAT_URL + "Datasets", params={"filter": query, "access_token": scicat_token})
            cat_entry = r.json()
            bucket = cat_entry[0]['sourceFolderHost'].split('//')[1].split('.')[0]
            key = cat_entry[0]['sourceFolder']
        else:
            print('no pid')
            return

        # retrieve from hancock
        r = requests.post(HANCOCK_URL + "token",json=dict(username=TEST_USERNAME, password=TEST_PASSWORD))
        print(r.status_code)
        if r.status_code == 200 | 201:
            hancock_token = r.json()['access_token']
            signed_url = requests.post(HANCOCK_URL + 'fetch_url',  json=dict(Bucket=bucket, Key=key),
                                    headers=make_headers(hancock_token))
            print(f" [x] {signed_url.json()}")
        else:
            print("could not retrieve URL")
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