import requests
import json
from flask import current_app
import logging


SCICAT_URL = current_app.config['SCICAT_URL']

def get_associated_payload(pid):
    try:
        r = requests.post(SCICAT_URL + 'Users/login', json=dict(username='ingestor', password='aman'))
        r.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
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
