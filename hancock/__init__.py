from flask import Flask
from hancock.config import Config
from flask_restx import Api
from flask_ldap3_login import LDAP3LoginManager
from flask_jwt_extended import JWTManager
from flask import Blueprint
from flask_redis import FlaskRedis

revoked_store = FlaskRedis()
ldap_manager = LDAP3LoginManager()
jwt = JWTManager()

def create_app(config_file=Config):
        app = Flask(__name__)
        app.config.from_object(Config)
        ldap_manager.init_app(app)
        jwt.init_app(app)
        revoked_store.init_app(app)

        from .hancock_api import hancock_bp
        app.register_blueprint(hancock_bp,  url_prefix='/api')

        return app