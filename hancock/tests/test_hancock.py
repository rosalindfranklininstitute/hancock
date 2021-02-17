from unittest import TestCase
from flask_jwt_extended import jwt_required
from flask_restx import Resource
import boto3
import os
from moto import mock_s3
from hancock import create_app
from hancock.hancock_api import hancock_api
from datetime import timedelta


ACCESS_EXPIRES = timedelta(minutes=15)
REFRESH_EXPIRES = timedelta(days=30)


class TestConfig(object):
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

    #JWT
    JWT_ACCESS_TOKEN_EXPIRES = ACCESS_EXPIRES
    JWT_REFRESH_TOKEN_EXPIRES = REFRESH_EXPIRES
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access']
    LDAP_HOST = 'ldaps://localhost'
    LDAP_PORT = 10636
    LDAP_BASE_DN = 'dc=planetexpress,dc=com'
    LDAP_USER_DN = 'ou=people'
    LDAP_USER_LOGIN_ATTR = 'uid'
    LDAP_USER_RDN_ATTR = 'cn'
    LDAP_BIND_USER_DN = 'cn=admin,dc=planetexpress,dc=com'
    LDAP_BIND_USER_PASSWORD = 'GoodNewsEveryone'
    LDAP_USER_SEARCH_SCOPE = 'SUBTREE'
    LDAP_USER_OBJECT_FILTER = '(objectclass=inetOrgPerson)'
    LDAP_GROUP_OBJECT_FILTER = '(objectclass=Group)'
    LDAP_USE_SSL = False
    S3_ENDPOINT_URL = 'http: // s3.amazonaws.com'
    ACCESS_KEY = 'N0T4R34L4CC3SSK3Y'
    SECRET_ACCESS_KEY = 'N0T4R34LS3CR3TACC3SSK3Y'
    REDIS_URL = 'redis://127.0.0.1:6379'
    SCICAT_URL = 'http://localhost/api/v3/'


# Add REST API endpoint for testing basic functionality
@hancock_api.route('/protected')
class Protected(Resource):
    @jwt_required
    def get(self):
        return {'hello': 'world'}


def make_headers(jwt):
    return {'Authorization': 'Bearer {}'.format(jwt)}


class LoginTest(TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()

    def test_good_login(self):
        # login and get token
        print('login')
        response = self.client.post('/api/token', json=dict(username="fry", password="fry"))
        self.assertEqual(response.status_code, 201)
        self.assertIn('access_token', response.get_json())
        token = response.get_json()['access_token']
        print('access protected page')
        # use token for accessing protected page
        response = self.client.get('/api/protected', headers=make_headers(token))
        self.assertEqual(response.status_code, 200)
        self.assertIn('hello', response.get_json())
        print("revoke token")
        # revoke token
        response = self.client.delete('/api/token', json=dict(access_token=token))
        self.assertEqual(response.status_code, 204)
        print('confirm token revoked')
        # confirm token has been revoked
        response = self.client.get('/api/protected', headers=make_headers(token))
        self.assertEqual(response.status_code, 500)
        print('second revoke')
        # revoke token again
        response = self.client.delete('/api/token', json=dict(access_token=token))
        self.assertEqual(response.status_code, 204)
        print('confirm second revoke')
        # confirm token has been revoked
        response = self.client.get('/api/protected', headers=make_headers(token))
        self.assertEqual(response.status_code, 500)

    def test_bad_login(self):
        response = self.client.post('/api/token', json=dict(username="jaewjfpewqjfjpewp", password="jeawjfpfjewf"))
        self.assertEqual(response.status_code, 401)

        response = self.client.post('/api/token', json=dict(username='jaewjfpewqjfjpewp'))
        self.assertEqual(response.status_code, 500)

        response = self.client.post('/api/token', json=dict(password='jaewjfpewqjfjpewp'))
        self.assertEqual(response.status_code, 500)

@mock_s3
class RetrieveUrlTest(TestCase):

    def setUp(self) -> None:
        self.session = boto3.session.Session()
        self.conn=self.session.resource('s3', region_name='us-east-1')
        # We need to create the bucket since this is all in Moto's 'virtual' AWS account
        self.conn.create_bucket(Bucket='rfi-test-bucket-abc')
        self.conn.Object('rfi-test-bucket-abc','myfileobj.txt').put()
        creds = self.session.get_credentials()
        self.app = create_app(TestConfig)
        self.app.config['ACCESS_KEY'] = creds.access_key
        self.app.config['SECRET_ACCESS_KEY'] = creds.secret_key
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

    def tearDown(self) -> None:
        self.conn.Object('rfi-test-bucket-abc', 'myfileobj.txt').delete()
        self.conn.Bucket('rfi-test-bucket-abc').delete()
        self.client.delete()


    def test_successful_retrieval(self):
        response = self.client.post('/api/token', json=dict(username=TEST_USERNAME, password=TEST_PASSWORD))
        token = response.get_json()['access_token']
        response = self.client.post('/api/fetch_url',
                                    json=dict(Bucket='rfi-test-bucket-abc', Key='myfileobj.txt'),
                                    headers=make_headers(token))

        self.assertNotEqual(response.status_code, '200')
        self.assertTrue('http' in response.json['presigned_url'])

    def test_bad_retrieval(self):
        response = self.client.post('/api/token', json=dict(username=TEST_USERNAME, password=TEST_PASSWORD))
        token = response.get_json()['access_token']
        response = self.client.post('/api/fetch_url',
                                    json=dict(Bucket='rfi-test-bucket-485', Key='notmyfileobj.txt'),
                                    headers=make_headers(token))
        self.assertEqual(response.status_code, 404)

