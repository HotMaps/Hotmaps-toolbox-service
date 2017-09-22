import logging.config
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from flask import Flask, Blueprint
from flask_cors import CORS
from main_api import settings
from main_api.api.main.endpoints.population import ns as main_population_namespace
from main_api.api.main.endpoints.heat_density_map import ns as main_heat_density_map_namespace
from main_api.api.main.endpoints.stats import ns as main_stats_namespace
from main_api.api.restplus import api
from main_api.models import db

log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logging.conf')
logging.config.fileConfig(log_file_path)
log = logging.getLogger(__name__)
logging.getLogger('flask_cors').level = logging.DEBUG

# methods
def configure_app(flask_app):
    flask_app.config['DEBUG'] = settings.FLASK_DEBUG
    #flask_app.config['SERVER_NAME'] = settings.FLASK_SERVER_NAME
    flask_app.config['SECRET_KEY'] = settings.FLASK_SECRET_KEY
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = settings.SQLALCHEMY_DATABASE_URI
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = settings.SQLALCHEMY_TRACK_MODIFICATIONS
    flask_app.config['SWAGGER_UI_DOC_EXPANSION'] = settings.RESTPLUS_SWAGGER_UI_DOC_EXPANSION
    flask_app.config['RESTPLUS_VALIDATE'] = settings.RESTPLUS_VALIDATE
    flask_app.config['RESTPLUS_MASK_SWAGGER'] = settings.RESTPLUS_MASK_SWAGGER
    flask_app.config['ERROR_404_HELP'] = settings.RESTPLUS_ERROR_404_HELP


def initialize_app(flask_app):
    configure_app(flask_app)

    blueprint = Blueprint('api', __name__, url_prefix='/api')
    api.init_app(blueprint)
    api.add_namespace(main_population_namespace)
    api.add_namespace(main_heat_density_map_namespace)
    api.add_namespace(main_stats_namespace)
    flask_app.register_blueprint(blueprint)

    db.init_app(flask_app)
    #with app.app_context():
        #db.create_all()


def create_app():
    """
    Create app instance
    """
    app = Flask(__name__)
    
    initialize_app(app)

    CORS(app, resources={r"/api/*": {"origins": {"http://hotmaps.hevs.ch","http://hotmaps.hevs.ch:8080"}}})

    return app
