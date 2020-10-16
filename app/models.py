from app import api
from flask_restx import fields

greetings = api.model('GreetingFormat', {'greeting':fields.String, 'name':fields.String,})

auth_creds_resource = api.model('AuthenticationCredentials', {
    'username': fields.String(description='The LDAP username', required=True),
    'password': fields.String(description='The LDAP password', required=True),
})

token_resource = api.model('Token', {
    'access_token': fields.String(description='A previously generated access token', required=True)
})
