from .models import auth_creds_resource, token_resource, object_info_resource, url_resource
from flask_restx import Resource, abort
from flask_ldap3_login import AuthenticationResponseStatus
from flask_jwt_extended import (create_access_token, get_jti, jwt_required)
from app import api, ldap_manager, jwt
from app.config import  ACCESS_EXPIRES
from .redis_utils import revoked_store
from .s3_utils import S3Operations



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

@api.route('/fetch_url')
class FetchUrl(Resource):
    #don't forget to add a token
    @api.expect(object_info_resource)
    @api.marshal_with(url_resource)
    @jwt_required
    def post(self):
        # access the s3 bucket
        presigned_url = S3Operations.generate_presigned_url(api.payload['Bucket'], api.payload['Key'])
        return presigned_url

@jwt.token_in_blacklist_loader
def check_if_token_is_revoked(decrypted_token):
    jti = decrypted_token['jti']
    entry = revoked_store.get(jti)
    if entry is None:
        return True
    return entry == 'true'
