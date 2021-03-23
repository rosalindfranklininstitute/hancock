import requests
import json
from hancock import app
from urllib.parse import urlparse
import itertools

SCICAT_URL = app.config['SCICAT_URL']

def get_scicat_token():
    r = requests.post(SCICAT_URL + 'Users/login', json=dict(username='ingestor', password='aman'))
    scicat_token = r.json()['id']

    return scicat_token

def get_associated_payload(pid):
    scicat_token = get_scicat_token()
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
        if not bucket:
            app.logger.debug('source folder host could not be parsed')
            return {}
        if not key:
            app.logger.debug('source folder could not be parsed')
            return {}
        return dict(bucket=bucket, key=key)
    else:
        return {}


def create_scicat_message(url_list):

    url_str = ""
    for url in url_list:
            url_str = url_str + "\n".join(url['presigned_url']) +"\n"
    return bytes(url_str,'ascii')