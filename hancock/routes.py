from .models import auth_creds_resource, token_resource, object_info_resource, url_resource, message_resource
from flask_restx import Resource, abort
from flask_jwt_extended import (create_access_token, get_jti, jwt_required)
from hancock import api, jwt, auth_manager
from hancock.config import ACCESS_EXPIRES
from .redis_utils import revoked_store
from .s3_utils import S3Operations
import ast
from .scicat_utils import get_associated_payload, create_scicat_message
from urllib.parse import urlparse
from .auth_utils import AuthentificationFail
from .smtp_utils import SMTPConnect


@api.route('/ping')
class Ping(Resource):
    def get(self):
        return {'hi':'there'}

@api.route('/token')
class Token(Resource):
    @api.expect(auth_creds_resource)
    @api.marshal_with(token_resource, code=201, description='The new access token')
    @api.doc(description='Create a new access token by providing a username and password that will be used for authenticating against an LDAP database')
    def post(self):
        username = api.payload['username']
        password = api.payload['password']

        try:
              auth_manager.authenticate_user(username, password)
        except AuthentificationFail as e:
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
    @api.expect(object_info_resource)
    @api.marshal_with(url_resource)
    @jwt_required()
    def post(self):
      S3Operations.client_options()
      response = S3Operations.generate_presigned_url(Bucket=api.payload['Bucket'], Key=api.payload['Key'])
      return response

@api.route('/receive_async_messages')

class ReceiveAsyncMessages(Resource):
    @jwt_required()
    @api.expect(message_resource)
    @api.response(200, 'Job Complete')
    def post(self):
        print(f"message received:{api.payload['async_message']}")
        try:
            payload = ast.literal_eval(api.payload['async_message'])
        except (SyntaxError, ValueError) as e:
            print(e)
            abort(401, "Cannot read async messages")

        datasetList = payload["datasetList"]
        output_ls = []
        for item in datasetList:
             output = get_associated_payload(item['pid'])
             output_ls.append(output)
        url_ls=[]
        if output_ls:
            for output in output_ls:
                bucket = urlparse(output[0]['sourceFolderHost'])[1].split('.')[0]
                key = output[0]['sourceFolder'].strip('/')
                S3Operations.client_options()
                url = S3Operations.generate_presigned_url(Bucket=bucket, Key=key)
                url_ls.append(url[0])
        else:
            abort(406, "Cannot retrieve dataset list")

        try:
            url_bytes_io = create_scicat_message(url_ls)
            app.logger.info('EMAIL created')
            SMTPConnect.send_email(payload["emailJobInitiator"], url_string_io=url_bytes_io)
        except Exception as e:
             app.logger.debug(e)
             abort(406, "Unable to successfully send email")


        return 'Job Complete', 200

@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, decrypted_token):
    jti = decrypted_token['jti']
    entry = revoked_store.get(jti)
    if entry is None:
        return True
    return entry == 'true'






