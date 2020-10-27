from unittest import TestCase
from hancock import app, api
from flask_jwt_extended import jwt_required
from flask_restx import Resource
import boto3
import unittest
from hancock.s3_utils import S3Operations
from hancock.config import Config

TEST_USERNAME = 'zoidberg'
TEST_PASSWORD = 'zoidberg'


# Add REST API endpoint for testing basic functionality
@api.route('/protected')
class Protected(Resource):
    @jwt_required
    def get(self):
        return {'hello': 'world'}


def make_headers(jwt):
    return {'Authorization': 'Bearer {}'.format(jwt)}


class TestConfig(Config):
    HANCOCK_REDIS_HOST = '127.0.0.1'
    LDAP_HOST = 'localhost'
    LDAP_PORT = 389
    LDAP_BASE_DN = "dc=planetexpress,dc=com"
    LDAP_BIND_DN = "cn=admin"
    LDAP_BIND_PASSWORD = "GoodNewsEveryone"
    LDAP_USER_DN = "ou=people"
    LDAP_USER_LOGIN_ATTR = "uid"
    LDAP_USE_SSL = False
    LDAP_USER_SEARCH_SCOPE = 'SUBTREE'
    LDAP_USER_RDN_ATTR = 'cn'
    LDAP_USER_LOGIN_ATTR = 'uid'
    S3_ENDPOINT_URL = 'https://ceph-dev-gw3.gridpp.rl.ac.uk'
    ACCESS_KEY = 'E03XRPZ4MZLRJJXZE6JO'
    SECRET_ACCESS_KEY = 'Bxov4Jn0nannMhkVw8fI9HoFvMEdDSiO1xTudhCY'
    CERTIFICATE_VERIFY = False


class LoginTest(TestCase):
    def setUp(self):
        app.config.from_object(TestConfig)
        self.client = app.test_client()

    def test_good_login(self):
        # login and get token
        print(app.config['LDAP_HOST'])
        response = self.client.post('/api/token', json=dict(username=TEST_USERNAME, password=TEST_PASSWORD))
        self.assertEqual(response.status_code, 201)
        self.assertIn('access_token', response.get_json())
        token = response.get_json()['access_token']

        # use token for accessing protected page
        response = self.client.get('/api/protected', headers=make_headers(token))
        self.assertEqual(response.status_code, 200)
        self.assertIn('hello', response.get_json())

        # # revoke token
        # response = self.client.delete('/api/token', json=dict(access_token=token))
        # self.assertEqual(response.status_code, 204)
        #
        # # confirm token has been revoked
        # response = self.client.get('/api/protected', headers=make_headers(token))
        # self.assertEqual(response.status_code,401)
        #
        # # revoke token again
        # response = self.client.delete('/api/token', json=dict(access_token=token))
        # self.assertEqual(response.status_code, 204)
        #
        # # confirm token has been revoked
        # response = self.client.get('/api/protected', headers=make_headers(token))
        # self.assertEqual(response.status_code, 401)

    def test_bad_login(self):
        print('testing bad login')
        response = self.client.post('/api/token', json=dict(username='jaewjfpewqjfjpewp', password='jeawjfpfjewf'))
        self.assertEqual(response.status_code, 401)

        response = self.client.post('/api/token', json=dict(username='jaewjfpewqjfjpewp'))
        self.assertEqual(response.status_code, 400)

        response = self.client.post('/api/token', json=dict(password='jaewjfpewqjfjpewp'))
        self.assertEqual(response.status_code, 400)


class RetrieveUrlTest(TestCase):
    def setUp(self) -> None:
        app.config.from_object(TestConfig)
        self.client = app.test_client()
        self.s3 = boto3.client('s3', **S3Operations.client_options())
        self.s3.create_bucket(Bucket='rfi-test-bucket-abc')
        self.s3.put_object(Bucket='rfi-test-bucket-abc', Key='myfileobj.txt')


    def tearDown(self) -> None:
        self.s3.delete_object(Bucket='rfi-test-bucket-abc', Key='myfileobj.txt')
        self.s3.delete_bucket(Bucket='rfi-test-bucket-abc')


    def test_successful_retrieval(self):
        response =  self.client.post('/api/token', json=dict(username=TEST_USERNAME, password=TEST_PASSWORD))
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
        print(response)
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()