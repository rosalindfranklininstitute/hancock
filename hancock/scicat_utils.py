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

def create_scicat_message(url_list):

    url_str = "\n"
    for url in url_list:
        url_str = url_str + url['presigned_url'] + '\n'

    message =  """\
    Subject: Batch Data Job 
    """ + url_str
    """
    
    This message is sent from hancock.
    
    """
    return message