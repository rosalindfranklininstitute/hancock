from flask import Flask
from app.config import Config
from flask_restx import Api
from flask_ldap3_login import LDAP3LoginManager
from flask_jwt_extended import JWTManager


app = Flask(__name__)

app.config.from_object(Config)
api = Api(app, prefix='/api', validate=True)
ldap_manager = LDAP3LoginManager(app)
jwt = JWTManager(app)

from app import routes, models
