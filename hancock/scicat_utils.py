import requests
import json
import logging
from hancock import app


SCICAT_URL = app.config['SCICAT_URL']

def get_associated_payload(pid):
    r = requests.post(SCICAT_URL + 'Users/login', json=dict(username='ingestor', password='aman'))
    scicat_token = r.json()['id']
    query = json.dumps({"where": {"pid": pid}})

    payload = requests.get(SCICAT_URL + "Datasets", params={"filter": query, "access_token": scicat_token})
    return payload.json()
