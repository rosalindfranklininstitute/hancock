import unittest
from app import app, api
from flask_restx import Resource
from flask_jwt_extended import jwt_required

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

      
class LoginTest(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

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

        # revoke token
        response = self.client.delete('/api/token', json=dict(access_token=token))
        self.assertEqual(response.status_code, 204)

        # confirm token has been revoked
        response = self.client.get('/api/protected', headers=make_headers(token))
        self.assertEqual(response.status_code, 401)

        # revoke token again
        response = self.client.delete('/api/token', json=dict(access_token=token))
        self.assertEqual(response.status_code, 204)

        # confirm token has been revoked
        response = self.client.get('/api/protected', headers=make_headers(token))
        self.assertEqual(response.status_code, 401)

    def test_bad_login(self):
        print('testing bad login')
        response = self.client.post('/api/token', json=dict(username='jaewjfpewqjfjpewp', password='jeawjfpfjewf'))
        self.assertEqual(response.status_code, 401)

        response = self.client.post('/api/token', json=dict(username='jaewjfpewqjfjpewp'))
        self.assertEqual(response.status_code, 400)

        response = self.client.post('/api/token', json=dict(password='jaewjfpewqjfjpewp'))
        self.assertEqual(response.status_code, 400)
