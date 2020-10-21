from flask import Flask
from app.config import Config
from flask_restx import Api
from flask_ldap3_login import LDAP3LoginManager
from flask_jwt_extended import JWTManager

app = Flask(__name__)

app.config.from_object(Config)
api = Api(app, version='0.1', title='Hancock API',
    description='REST API to return presigned URLs',
    prefix='/api', doc='/api', validate=True, default='Hancock',
)


ldap_manager = LDAP3LoginManager(app)
jwt = JWTManager(app)

from app import routes, models
