from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import os

class User(UserMixin):
    def __init__(self, username, password):
        self.username = username
        self.password_hash = self.set_password(password)


    def set_password(self, password):
        password_hash = generate_password_hash(password)
        return password_hash

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

Users = {'xchanger': User('xchanger', os.environ.get('XCHANGER_PASSWORD')),
         'catanie': User('catanie', os.environ.get('CATANIE_PASSWORD'))}


def authenticate_user(username, password):
    try:
        user = Users[username]
        user.check_password(password)

        if not user.is_authenticated:
            raise AuthentificationFail('invalid username or password')
    except Exception as e:
        raise AuthentificationFail('invalid username or password')



class AuthentificationFail(Exception):
    """Info required in Scicat Payload not found"""
    pass