from flask import Blueprint
from flask_restx import Api

hancock_bp = Blueprint('hancock_api', __name__)
hancock_api = Api(hancock_bp)
from . import routes,  models
