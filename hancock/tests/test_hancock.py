from unittest import TestCase
from hancock import app, api
from flask_jwt_extended import jwt_required
from flask_restx import Resource
import boto3
from hancock.s3_utils import S3Operations
import os
from moto import mock_s3


TEST_USERNAME = os.environ.get('TEST_USERNAME')
TEST_PASSWORD = os.environ.get('TEST_PASSWORD')

# Add REST API endpoint for testing basic functionality
@api.route('/protected')
class Protected(Resource):
    @jwt_required
    def get(self):
        return {'hello': 'world'}


def make_headers(jwt):
    return {'Authorization': 'Bearer {}'.format(jwt)}


class LoginTest(TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_good_login(self):
        # login and get token
        print('login')
        print(app.config['HANCOCK_REDIS_HOST'])
        response = self.client.post('/api/token', json=dict(username=TEST_USERNAME, password=TEST_PASSWORD))
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
        self.assertEqual(response.status_code,500)
        print('second revoke')
        # revoke token again
        response = self.client.delete('/api/token', json=dict(access_token=token))
        self.assertEqual(response.status_code, 204)
        print('confirm second revoke')
        # confirm token has been revoked
        response = self.client.get('/api/protected', headers=make_headers(token))
        self.assertEqual(response.status_code, 500)

    def test_bad_login(self):
        response = self.client.post('/api/token', json=dict(username='jaewjfpewqjfjpewp', password='jeawjfpfjewf'))
        self.assertEqual(response.status_code, 401)

        response = self.client.post('/api/token', json=dict(username='jaewjfpewqjfjpewp'))
        self.assertEqual(response.status_code, 400)

        response = self.client.post('/api/token', json=dict(password='jaewjfpewqjfjpewp'))
        self.assertEqual(response.status_code, 400)


class RetrieveUrlTest(TestCase):
    def setUp(self) -> None:

        self.client = app.test_client()
        self.s3 = boto3.client('s3', **S3Operations.client_options(use_ssl=True))
        self.s3.create_bucket(Bucket='rfi-test-bucket-abc')
        self.s3.put_object(Bucket='rfi-test-bucket-abc', Key='myfileobj.txt')


    def tearDown(self) -> None:
        self.s3.delete_object(Bucket='rfi-test-bucket-abc', Key='myfileobj.txt')
        self.s3.delete_bucket(Bucket='rfi-test-bucket-abc')

    @mock_s3
    def test_successful_retrieval(self):
        response = self.client.post('/api/token', json=dict(username=TEST_USERNAME, password=TEST_PASSWORD))
        token = response.get_json()['access_token']
        response = self.client.post('/api/fetch_url',
                                    json=dict(Bucket='rfi-test-bucket-abc', Key='myfileobj.txt'),
                                    headers=make_headers(token))

        self.assertNotEqual(response.status_code, '200')
        self.assertTrue('http' in response.json['presigned_url'])

    @mock_s3
    def test_bad_retrieval(self):
        response = self.client.post('/api/token', json=dict(username=TEST_USERNAME, password=TEST_PASSWORD))
        token = response.get_json()['access_token']
        response = self.client.post('/api/fetch_url',
                                    json=dict(Bucket='rfi-test-bucket-485', Key='notmyfileobj.txt'),
                                    headers=make_headers(token))
        print(response)
        self.assertEqual(response.status_code, 404)

