from flask import Flask
from hancock.config import Config
from flask_restx import Api
from flask_jwt_extended import JWTManager
from hancock.auth_utils import AuthManager
import logging
from logging.handlers import RotatingFileHandler
import os

app = Flask(__name__)

app.config.from_object(Config)

api = Api(app, version='0.1', title='Hancock API',
        description='REST API to return presigned URLs',
        prefix='/api', doc='/api', validate=True, default='Hancock')

jwt = JWTManager(app)


auth_manager = AuthManager(app)

if not app.debug:
        if not os.path.exists('logs'):
                os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/antigen.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.DEBUG)
        app.logger.info('HANCOCK START UP')
        app.logger.info(f'Scicat URL connection: {app.config["SCICAT_URL"]}')
        app.logger.info(f'redis connection: {app.config["HANCOCK_REDIS_HOST"]}')

from hancock import routes, models
