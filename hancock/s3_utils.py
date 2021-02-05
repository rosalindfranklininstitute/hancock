import boto3
from botocore.exceptions import ClientError
from hancock import app

class S3Operations:
    @classmethod
    def client_options(cls, **kwargs):
        client_options = dict()
        client_options['endpoint_url'] = app.config['S3_ENDPOINT_URL']
        client_options['verify'] = app.config['CERTIFICATE_VERIFY']
        client_options['aws_access_key_id'] = app.config['ACCESS_KEY']
        client_options['aws_secret_access_key'] = app.config['SECRET_ACCESS_KEY']

        for k, v in kwargs.items():
            client_options[k] = v
        return client_options

    @classmethod
    def generate_presigned_url(cls, Bucket, Key, Expiration=900):

        try:
              s3_client = boto3.client('s3', **cls.client_options())

        except ClientError as e:
             print(e)
             return {'presigned_url': None}, 404

        # check bucket and object exist
        try:
             s3_client.head_object(Bucket=Bucket, Key=Key)
        except ClientError as e:
             print(e)
             return {'presigned_url': None}, 404

        try:
            url = s3_client.generate_presigned_url('get_object',
                                                        Params={'Bucket': Bucket,
                                                                'Key': Key},
                                                        ExpiresIn=Expiration)
        except ClientError as e:
                 print(e)
                 return {'presigned_url': None}, 404

        return {'presigned_url': url}, 200