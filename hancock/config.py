import os
from datetime import timedelta
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
print(basedir)
load_dotenv(os.path.join(os.path.sep, basedir, '..', '.env'))

ACCESS_EXPIRES = timedelta(minutes=15)
REFRESH_EXPIRES =  timedelta(days=30)

class Config(object):
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

    #JWT
    JWT_ACCESS_TOKEN_EXPIRES = ACCESS_EXPIRES
    JWT_REFRESH_TOKEN_EXPIRES = REFRESH_EXPIRES
    # JWT_BLACKLIST_ENABLED = False
    # JWT_BLACKLIST_TOKEN_CHECKS = ['access']

    #Redis
    HANCOCK_REDIS_HOST = os.environ.get('HANCOCK_REDIS_HOST')

    # LDAP
    # using docker container rroemhild/test-openldap to provide ldap service
    LDAP_HOST = 'localhost'
    LDAP_PORT = 389
    LDAP_BASE_DN= 'dc=planetexpress,dc=com'
    LDAP_USER_DN = 'ou=people'
    LDAP_USER_RDN_ATTR = 'cn'
    LDAP_USER_LOGIN_ATTR = 'uid'
    LDAP_BIND_DN = 'cn=admin'
    LDAP_BIND_USER_PASSWORD = 'GoodNewsEveryone'

    #S3
    S3_ENDPOINT_URL = os.environ.get('S3_ENDPOINT_URL')
    ACCESS_KEY = os.environ.get('ACCESS_KEY')
    SECRET_ACCESS_KEY = os.environ.get('SECRET_ACCESS_KEY')
    CERTIFICATE_VERIFY= True

