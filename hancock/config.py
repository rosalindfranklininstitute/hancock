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
    HANCOCK_REDIS_HOST = os.environ['HANCOCK_REDIS_HOST']

    # Microservice auth
    USER_SETUP_JSON = os.environ['USER_SETUP_JSON']

    #S3
    S3_ENDPOINT_URL = os.environ['S3_ENDPOINT_URL']
    ACCESS_KEY = os.environ['ACCESS_KEY']
    SECRET_ACCESS_KEY = os.environ['SECRET_ACCESS_KEY']
    CERTIFICATE_VERIFY = True
    URL_EXPIRATION = os.environ.get('URL_EXPIRATION', default=24*60*60)

    #SCICAT
    SCICAT_URL = os.environ['SCICAT_URL']

    # SMTP
    SMTP_SERVER = os.environ['SMTP_SERVER']
    SMTP_PORT = os.environ['SMTP_PORT']
    SMTP_LOGIN_USER = os.environ['SMTP_LOGIN_USER']
    SMTP_LOGIN_PASSWORD = os.environ['SMTP_LOGIN_PASSWORD']
    SMTP_SENDER_EMAIL = os.environ['SMTP_SENDER_EMAIL']
    EMAIL_BODY_FILE = os.environ.get('EMAIL_BODY_FILE', default='config/email_body_file.txt')