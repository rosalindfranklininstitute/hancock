from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import json


class AuthManager:
    def __init__(self, app=None, add_context_processor=True):
        self.Users =  {}
        self.user = {}
        if app is not None:
            self.init_app(app, add_context_processor)

    # from flask login - include this to work with Blue Print Factory pattern
    def init_app(self, app, add_context_processor=True):
        '''
        Configures an application. This registers an `after_request` call, and
        attaches this `LoginManager` to it as `app.login_manager`.

        :param app: The :class:`flask.Flask` object to configure.
        :type app: :class:`flask.Flask`
        :param add_context_processor: Whether to add a context processor to
            the app that adds a `current_user` variable to the template.
            Defaults to ``True``.
        :type add_context_processor: bool
        '''
        app.auth_manager = self

        if add_context_processor:
            app.context_processor(self._user_context_processor)

        self.Users = self.setup_session_users(app)

    def _get_user(self):
        return self.user

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
            self.user = user
            if not user.is_authenticated:
                raise AuthentificationFail('invalid username or password')
        except Exception as e:
            raise AuthentificationFail('invalid username or password')

    def _user_context_processor(self):
        return dict(current_user=self._get_user())


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





