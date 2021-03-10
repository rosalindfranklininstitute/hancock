from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import json


class AuthManager:
    def __init__(self, app):
        self.Users = self.setup_session_users(app)

    @staticmethod
    def setup_session_users(app):
        with open(app.config['USER_SETUP_JSON']) as user_file:
            users = json.load(user_file)
        if users:
            Users = {}
            for k, v in users.items():
                Users[k] = User(k, v)
            return Users
        else:
            print('user config not loaded')

    def authenticate_user(self, username, password):
        try:
            user = self.Users[username]
            user.check_password(password)

            if not user.is_authenticated:
                raise AuthentificationFail('invalid username or password')
        except Exception as e:
            raise AuthentificationFail('invalid username or password')


class User(UserMixin):
    def __init__(self, username, password):
        self.username = username
        self.password_hash = self.set_password(password)


    def set_password(self, password):
        password_hash = generate_password_hash(password)
        return password_hash

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)



class AuthentificationFail(Exception):
    """Info required in Scicat Payload not found"""
    pass





