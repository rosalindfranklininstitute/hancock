import os
from datetime import timedelta
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(os.path.sep, basedir, '..', '.env'))

ACCESS_EXPIRES = timedelta(minutes=15)
REFRESH_EXPIRES =  timedelta(days=30)

class Config(object):
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

    # SQLLITE FOR USE AUTH
    SQLALCHEMY_DATABASE_URI ='sqlite:///../hancock_users.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    #JWT
    JWT_ACCESS_TOKEN_EXPIRES = ACCESS_EXPIRES
    JWT_REFRESH_TOKEN_EXPIRES = REFRESH_EXPIRES
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access']

    #Redis
    HANCOCK_REDIS_HOST = os.environ.get('HANCOCK_REDIS_HOST')


    #S3
    S3_ENDPOINT_URL = os.environ.get('S3_ENDPOINT_URL')
    ACCESS_KEY = os.environ.get('ACCESS_KEY')
    SECRET_ACCESS_KEY = os.environ.get('SECRET_ACCESS_KEY')
    CERTIFICATE_VERIFY= True

    #SCICAT
    SCICAT_URL = os.environ.get('SCICAT_URL')