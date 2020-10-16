import os
from datetime import timedelta
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
print(basedir)
load_dotenv(os.path.join(os.path.sep, basedir, '..', '.env'))

ACCESS_EXPIRES = timedelta(minutes=15)
REFRESH_EXPIRES =  timedelta(days=30)

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    JWT_ACCESS_TOKEN_EXPIRES = ACCESS_EXPIRES
    JWT_REFRESH_TOKEN_EXPIRES = REFRESH_EXPIRES
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access']
    HANCOCK_REDIS_HOST = os.environ.get('HANCOCK_REDIS_HOST')
    # LDAP_HOST = os.environ.get('LDAP_HOST')
    # LDAP_PORT = int(os.environ.get('LDAP_PORT'))
    # LDAP_BASE_DN = os.environ.get('LDAP_BASE_DN')
    # LDAP_USER_LOGIN_ATTR = os.environ.get('LDAP_USER_LOGIN_ATTR')
    # #LDAP_USER_OBJECT_FILTER = os.environ.get('LDAP_USER_OBJECT_FILTER')
    # LDAP_BIND_USER_DN = os.environ.get('LDAP_BIND_USER_DN')
    # LDAP_BIND_USER_PASSWORD = os.environ.get('LDAP_BIND_USER_DN')
    # LDAP_USER_SEARCH_SCOPE = os.environ.get('LDAP_USER_SEARCH_SCOPE')

    # LDAP_USER_DN= os.environ.get('LDAP_USER_DN')
    # using docker container rroemhild/test-openldap to provide ldap service
    LDAP_HOST = 'localhost'

    LDAP_PORT = 389
    # Base DN of your directory
    LDAP_BASE_DN= 'dc=planetexpress,dc=com'

    # Users DN to be prepended to the Base DN
    LDAP_USER_DN = 'ou=people'



    # The RDN attribute for your user schema on LDAP
    LDAP_USER_RDN_ATTR = 'cn'

    # The Attribute you want users to authenticate to LDAP with.
    LDAP_USER_LOGIN_ATTR = 'uid'

    # The Username to bind to LDAP with
    LDAP_BIND_DN = 'cn=admin'

    # The Password to bind to LDAP with
    LDAP_BIND_USER_PASSWORD = 'GoodNewsEveryone'
