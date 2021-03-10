from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json

def setup_session_users():
    with open(os.environ.get('USER_SETUP_JSON')) as user_file:
        users = json.load(user_file)
    if users:
        Users = {}
        for k, v in users.items():
            Users[k] = User(k, v)
        return Users
    else:
        print('user config not loaded')

class User(UserMixin):
    def __init__(self, username, password):
        self.username = username
        self.password_hash = self.set_password(password)


    def set_password(self, password):
        password_hash = generate_password_hash(password)
        return password_hash

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

Users = setup_session_users()

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




