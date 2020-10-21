from unittest import TestCase
from app import app, api
from flask_jwt_extended import jwt_required
from flask_restx import Api, Resource, fields, abort
import boto3
from moto import mock_s3
from app.s3_utils import S3Operations

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


class TestConfig:
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
    S3_ENDPOINT_URL = 'https://s3.amazonaws.com'
    ACCESS_KEY = 'testing'
    SECRET_ACCESS_KEY = 'testing'


class LoginTest(TestCase):
    def setUp(self):
        self.client = app.test_client(TestConfig)

    def test_good_login(self):
        # login and get token
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
        self.client = app.test_client(TestConfig)

    @mock_s3
    def test_successful_retrieval(self):
        self.s3 = boto3.client('s3')
        print(self.s3.meta.endpoint_url)
        self.s3.create_bucket(Bucket='rfi-test-bucket')
        self.s3.put_object(Bucket='rfi-test-bucket', Key='myobj.txt')

        response = S3Operations.generate_presigned_url(Bucket='rfi-test-bucket',
                                                         Key='myobj.txt',
                                                         Expiration=15)
        self.assertNotEqual(response, None)
        self.assertTrue('http' in response)


    def test_cannot_connect(self):
       pass
    # 
    # def cannotFindObj(self):
    #     pass
    # 
    # def authorisationUnsuccessful(self):
    #     pass
