from hancock import api
from flask_restx import fields


auth_creds_resource = api.model('AuthenticationCredentials', {
    'username': fields.String(description='The LDAP username', required=True),
    'password': fields.String(description='The LDAP password', required=True),
})

token_resource = api.model('Token', {
    'access_token': fields.String(description='A previously generated access token', required=True)
})

object_info_resource = api.model('ObjectCredentials', {
    'Bucket': fields.String(description='path to source folder on S3 object', required=True),
    'Key': fields.String(description='path to object', required=True)
})

url_resource = api.model('PresignedUrl', {
                            'presigned_url': fields.String(description="presigned url to download the data",
                                                           required=True)})

message_resource = api.model('AsynchronousMessage', {
                                'async_message': fields.String(description="message from rabbitMQ",
                                                               required=True)})

sourcefolder_resource = api.model('SourceFolder', {'sourceFolder': fields.String(description="sourceFolder field from catamel,"
                                                                                             "more generally, this is the key"),
                                                   'sourceFolderHost': fields.String(description="sourceFolderHost field from catamel, "
                                                                                                 "more generally , this is the url for the bucket.")})