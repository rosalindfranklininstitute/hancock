from . import hancock_api
from flask_restx import fields


auth_creds_resource = hancock_api.model('AuthenticationCredentials', {
    'username': fields.String(description='The LDAP username', required=True),
    'password': fields.String(description='The LDAP password', required=True),
})

token_resource = hancock_api.model('Token', {
    'access_token': fields.String(description='A previously generated access token', required=True)
})

object_info_resource = hancock_api.model('ObjectCredentials', {
    'Bucket': fields.String(description= 'path to source folder on S3 object', required=True),
    'Key': fields.String(description= 'path to object', required=True)
})

url_resource = hancock_api.model('PresignedUrl', {'presigned_url': fields.String(description= "presigned url to download the data",
                                           required= True)})

message_resource = hancock_api.model('AsynchronusMessage', {'async_message': fields.String(description ="message from rabbitMQ")})