from .models import auth_creds_resource, token_resource, greetings
from flask_restx import Resource, abort
from flask_ldap3_login import AuthenticationResponseStatus
from flask_jwt_extended import create_access_token
from app import api, ldap_manager
from flask_jwt_extended import get_jti
from app.config import  ACCESS_EXPIRES
from .redis_utils import revoked_store
from flask import request

@api.route('/greeting')
class Greeting(Resource):
    def get(self):
        return api.payload

    @api.expect(greetings, validate=True)
    def post(self):
       return  api.payload['username']


@api.route('/token')
class Token(Resource):
    @api.expect(auth_creds_resource)
    @api.marshal_with(token_resource, code=201, description='The new access token')
    @api.doc(description='Create a new access token by providing a username and password that will be used for authenticating against an LDAP database')
    def post(self):
        username = api.payload['username']
        password = api.payload['password']

        response = ldap_manager.authenticate(username, password)

        if response.status == AuthenticationResponseStatus.fail:
            abort(401, "Bad username or password")

        # Create our JWTs
        access_token = create_access_token(identity=username)

        # Store the tokens in redis with a status of not currently revoked. We
        # can use the `get_jti()` method to get the unique identifier string for
        # each token. We can also set an expires time on these tokens in redis,
        # so they will get automatically removed after they expire. We will set
        # everything to be automatically removed shortly after the token expires
        access_jti = get_jti(encoded_token=access_token)
        revoked_store.set(access_jti, 'false', ACCESS_EXPIRES * 1.2)

        ret = {
            'access_token': access_token,
        }
        return ret, 201


    @api.expect(token_resource)
    @api.response(204, 'Token deleted')
    @api.doc(description='Delete an access token')
    def delete(self):
        access_jti = get_jti(encoded_token=api.payload['access_token'])
        revoked_store.set(access_jti, 'true', ACCESS_EXPIRES * 1.2)
        return '', 204