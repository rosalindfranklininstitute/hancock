import boto3
from botocore.exceptions import ClientError
from app import app

class S3Operations:
    @classmethod
    def client_options(cls):
        client_options = dict()
        client_options['endpoint_url'] = app.config['S3_ENDPOINT_URL']
        client_options['verify'] = True
        client_options['aws_access_key_id'] = app.config['ACCESS_KEY']
        client_options['aws_secret_access_key'] = app.config['SECRET_ACCESS_KEY']
        return client_options

    @classmethod
    def generate_presigned_url(cls, Bucket, Key, Expiration=900):
        try:
            s3_client = boto3.client('s3', **cls.client_options())
        except ClientError as e:

             return '',e.response['Error']['Code']

        try:
            response = s3_client.generate_presigned_url('get_object',
                                                        Params={'Bucket': Bucket,
                                                                'Key': Key},
                                                        ExpiresIn=Expiration)
        except ClientError as e:

                 return '', e.response['Error']['Code']

        return response
