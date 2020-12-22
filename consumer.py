#!/usr/bin/env python
import pika
import os
import requests
import ast
import json
import sys
import logging
import dotenv

dotenv.load_dotenv()


TEST_USERNAME = os.environ.get('TEST_USERNAME')
TEST_PASSWORD = os.environ.get('TEST_PASSWORD')
SCICAT_URL = os.environ.get('SCICAT_URL')
HANCOCK_URL = os.environ.get('HANCOCK_URL')
LOG_PATH = os.environ.get('LOG_PATH')

logging.basicConfig(filename= LOG_PATH+ 'example.log', level=logging.INFO)


def make_headers(jwt):
    return {'Authorization': 'Bearer {}'.format(jwt)}


def get_associated_payload(pid):
    try:
        r = requests.post(SCICAT_URL + 'Users/login', json=dict(username='ingestor', password='aman'))
        r.raise_for_status()
    except requests.exceptions.HTTPError as err:
        logging.error(err)
        return None

    scicat_token = r.json()['id']
    query = json.dumps({"where": {"pid": pid}})

    try:
        payload = requests.get(SCICAT_URL + "Datasets", params={"filter": query, "access_token": scicat_token})
        payload.raise_for_status()
    except requests.exceptions.HTTPError as err:
        logging.error(err)
        return None
    return payload.json()


def retrieve_url(bucket, key):
    try:
        r = requests.post(HANCOCK_URL + "token", json=dict(username=TEST_USERNAME, password=TEST_PASSWORD))
        hancock_token = r.json()['access_token']
        r.raise_for_status()
    except requests.exceptions.HTTPError as err:
        logging.error(err)
        return None

    try:
        signed_url = requests.post(HANCOCK_URL + 'fetch_url', json=dict(Bucket=bucket, Key=key),
                                   headers=make_headers(hancock_token))
        signed_url.raise_for_status()
    except requests.exceptions.HTTPError as err:
        logging.error(err)
        return None

    return signed_url.json()


def main():

    parameters = pika.connection.URLParameters(os.environ.get('AMPQ_URI'))
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    def callback(ch, method, properties, body):
        logging.info(" [x] Received from rabbitmq")
        body = ast.literal_eval(body.decode())
        logging.info("retrieving info from Scicat....")

        # get info from Scicat

        if body is not None:
            cat_entry = get_associated_payload(body['datasetList'][0]['pid'])
            if cat_entry is not None:
                bucket = cat_entry[0]['sourceFolderHost'].split('//')[1].split('.')[0]
                key = cat_entry[0]['sourceFolder']
            else:
                logging.debug('cannot retrieve, bucket and key')
                return
        else:
            logging.debug('cannot retrieve payload, no message body')
            return

        signed_url = retrieve_url(bucket, key)
        if signed_url is None:
            logging.debug('no signed URL returned')
        ch.basic_ack(delivery_tag=method.delivery_tag)
        logging.info('presigned URL returned')

    channel.basic_consume(queue='client.jobs.write', on_message_callback=callback)

    logging.info(' [*] Waiting for messages. To exit press CTRL+C')
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
