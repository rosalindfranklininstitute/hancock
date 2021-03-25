import boto3
from botocore.exceptions import ClientError
from hancock import app
from flask import jsonify

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
              s3 = boto3.resource('s3', **cls.client_options())

        except ClientError as e:
             app.logger.debug(e)
             return {'presigned_url': None}, 404

        # check bucket and object exist
        try:
            bucket = s3.Bucket(Bucket)
            objs = bucket.objects.filter(Prefix=Key)

        except ClientError as e:
             app.logger.debug(e)
             return {'presigned_url': None}, 404

        try:
            url_ls =[]
            for obj in objs.all():
                app.logger.info(obj.key)
                url_ls.append(s3.meta.client.generate_presigned_url('get_object',
                                                            Params={'Bucket': Bucket,
                                                                    'Key': obj.key},
                                                            ExpiresIn=Expiration))
        except ClientError as e:
                 app.logger.debug(e)
                 return {'presigned_url': None}, 404

        return {'presigned_url': url_ls}, 200