from unittest import TestCase
from hancock import app, api
from flask_jwt_extended import jwt_required
from flask_restx import Resource
import boto3
from moto import mock_s3
from hancock.smtp_utils import create_email
from hancock.scicat_utils import create_scicat_message, get_associated_payload
from unittest.mock import patch



TEST_USERNAME = "myservice1"
TEST_PASSWORD = "weofnewofinoew"
TEST_USERNAME2= "myservice2"
TEST_PASSWORD2 = "sghiueswgeiwgh"
# Add REST API endpoint for testing basic functionality

@api.route('/protected')
class Protected(Resource):
    @jwt_required()
    def get(self):
        return dict(hello='world')


def make_headers(jwt):
    return dict(Authorization='Bearer {}'.format(jwt))


class LoginTest(TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_good_login(self):
        # login and get token
        print('login')
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

        response = self.client.post('/api/token', json=dict(username='myservice1', password='jeawjfpfjewf'))
        self.assertEqual(response.status_code, 401)


@mock_s3
class RetrieveUrlTest(TestCase):

    def setUp(self) -> None:
        self.session = boto3.session.Session()
        self.conn=self.session.resource('s3', region_name='us-east-1')
        # We need to create the bucket since this is all in Moto's 'virtual' AWS account
        self.conn.create_bucket(Bucket='rfi-test-bucket-abc')
        self.conn.Object('rfi-test-bucket-abc','myfileobj.txt').put()
        self.conn.Object('rfi-test-bucket-abc','dir_1/myfileobj.txt').put()
        self.conn.Object('rfi-test-bucket-abc', 'dir_1/myfileobj2.txt').put()
        creds = self.session.get_credentials()
        app.config['ACCESS_KEY'] = creds.access_key
        app.config['SECRET_ACCESS_KEY'] = creds.secret_key
        self.client = app.test_client()

    def tearDown(self) -> None:
        self.conn.Object('rfi-test-bucket-abc', 'myfileobj.txt').delete()
        self.conn.Object('rfi-test-bucket-abc','dir_1/myfileobj.txt').delete()
        self.conn.Object('rfi-test-bucket-abc', 'dir_1/myfileobj2.txt').delete()
        self.conn.Bucket('rfi-test-bucket-abc').delete()
        self.client.delete()


    def test_successful_retrieval(self):
        response = self.client.post('/api/token', json=dict(username=TEST_USERNAME2, password=TEST_PASSWORD2))
        token = response.get_json()['access_token']
        response = self.client.post('/api/fetch_url',
                                    json=dict(Bucket='rfi-test-bucket-abc', Key='myfileobj.txt'),
                                    headers=make_headers(token))

        self.assertNotEqual(response.status_code, '200')
        print(response.json)
        self.assertTrue('http' in response.json['presigned_url'])

    def test_successful_dir_retrieval(self):
        response = self.client.post('/api/token', json=dict(username=TEST_USERNAME2, password=TEST_PASSWORD2))
        token = response.get_json()['access_token']
        response = self.client.post('/api/fetch_url',
                                    json=dict(Bucket='rfi-test-bucket-abc', Key='dir_1'),
                                    headers=make_headers(token))

        self.assertNotEqual(response.status_code, '200')
        self.assertTrue('http' in response.json['presigned_url'])
        self.assertTrue(len(response.json['presigned_url']), 2)

    def test_bad_retrieval(self):
        response = self.client.post('/api/token', json=dict(username=TEST_USERNAME2, password=TEST_PASSWORD2))
        token = response.get_json()['access_token']
        response = self.client.post('/api/fetch_url',
                                    json=dict(Bucket='rfi-test-bucket-485', Key='notmyfileobj.txt'),
                                    headers=make_headers(token))
        self.assertEqual(response.status_code, 404)


class MockResponse:
            def __init__(self, json_data, status_code):
                self.json_data = json_data
                self.status_code = status_code

            def json(self):
                return self.json_data


SCICAT_URL = app.config['SCICAT_URL']


def mocked_requests_post(*args, **kwargs):
    if args[0] == SCICAT_URL + 'Users/login':
        return MockResponse({"id": "faketoken"}, 200)

    return MockResponse(None, 404)


def mocked_requests_get(*args, **kwargs):
    if SCICAT_URL + 'Dataset' in args[0]:
        return MockResponse({"pid": "my-fake-pid/123'",
                             "sourceFolderHost": "s3.myfakebucket.somecloud.org",
                             "sourceFolder": "myfile.txt"}, 200)

    return MockResponse(None, 404)


class ScicatUtilsTest(TestCase):
    def setUp(self):
        self.pid = 'my-fake-pid/123'

    @patch('hancock.scicat_utils.requests.post', side_effect=mocked_requests_post)
    @patch('hancock.scicat_utils.requests.get', side_effect=mocked_requests_get)
    def test_get_associated_payload(self, mock_post, mock_get):
        r = get_associated_payload(self.pid)
        self.assertIn('pid', r.keys())
        self.assertIn('sourceFolderHost', r.keys())
        self.assertIn('sourceFolder', r.keys())


    def test_create_message(self):
        url_list = [{'presigned_url': ['url_1', 'url_2']}, {'presigned_url': ['url_3']}]
        message = create_scicat_message(url_list)
        print(message)
        self.assertNotEqual(message, None)
        self.assertIsInstance(message, bytes)


class SMTPUtilsTest(TestCase):
    def setUp(self) -> None:
        pass

    def test_create_email(self):
        url_list = [{'presigned_url': 'url_1'}, {'presigned_url': 'url_2'}, {'presigned_url': 'url_3'}]
        url_bytes_io = create_scicat_message(url_list)
        main_body_file = "config/test_email_file.txt"
        message = create_email('myemail@gmail.com', main_body_file, attachment_bytes= url_bytes_io)
        self.assertIn("Content-Type: multipart/mixed", message)
        self.assertIn('To: myemail@gmail.com', message)
