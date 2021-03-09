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


    #JWT
    JWT_ACCESS_TOKEN_EXPIRES = ACCESS_EXPIRES
    JWT_REFRESH_TOKEN_EXPIRES = REFRESH_EXPIRES
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access']

    #Redis
    HANCOCK_REDIS_HOST = os.environ.get('HANCOCK_REDIS_HOST')

    # Microservice auth
    USER_SETUP_JSON = os.environ.get('USER_SETUP_JSON')
    #S3
    S3_ENDPOINT_URL = os.environ.get('S3_ENDPOINT_URL')
    ACCESS_KEY = os.environ.get('ACCESS_KEY')
    SECRET_ACCESS_KEY = os.environ.get('SECRET_ACCESS_KEY')
    CERTIFICATE_VERIFY= True

    #SCICAT
    SCICAT_URL = os.environ.get('SCICAT_URL')

    # SMTP
    SMTP_SERVER = os.environ.get('SMTP_SERVER')
    SMTP_PORT = os.environ.get('SMTP_PORT')
    SMTP_LOGIN_USER = os.environ.get('SMTP_LOGIN_USER')
    SMTP_LOGIN_PASSWORD = os.environ.get('SMTP_LOGIN_PASSWORD')
    SMTP_SENDER_EMAIL = os.environ.get('SMTP_SENDER_EMAIL')