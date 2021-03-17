import requests
import json
from hancock import app
from urllib.parse import urlparse

SCICAT_URL = app.config['SCICAT_URL']

def get_associated_payload(pid):
    r = requests.post(SCICAT_URL + 'Users/login', json=dict(username='ingestor', password='aman'))
    scicat_token = r.json()['id']
    query = json.dumps({"where": {"pid": pid}})

    payload = requests.get(SCICAT_URL + "Datasets", params={"filter": query, "access_token": scicat_token})
    return payload.json()

def check_process_bucket_key(payload):
    """
    checks the source folder host coming in from scicat

    params:
         payload: the payload returned from scicat datasets query
    """
    if ('sourceFolderHost' and 'sourceFolder') in payload.keys():
        bucket = urlparse(payload['sourceFolderHost'])[1].split('.')[0]
        key = payload['sourceFolder'].strip('/')
        return bucket, key
    else:
        return None




def create_scicat_message(url_list):

    url_str = " \n "
    for url in url_list:
        url_str = url_str + url['presigned_url'] + url_str

    message = "Subject: Batch Data Job \n" + url_str + "This message is sent from hancock. "

    return message