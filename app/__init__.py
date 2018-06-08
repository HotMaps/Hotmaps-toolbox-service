from flask import Flask

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
from .api_v1 import nsStats as main_stats_namespace
from .api_v1 import load_profile_namespace as main_heat_load_profile_namespace
from flask_celery import make_celery
import logging.config
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from flask_cors import CORS
from celery import Celery
celery = Celery()




from app.decorator.restplus import api


from app.flask_celery import make_celery
# methods
"""log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logging.conf')
logging.config.fileConfig(log_file_path)
log = logging.getLogger(__name__)
logging.getLogger('flask_cors').level = logging.DEBUG"""




def create_app(config_name):
    """
    Create app instance
    """
    app = Flask(__name__)
    cfg = os.path.join(os.getcwd(), 'config', config_name + '.py')
    app.config.from_pyfile(cfg)

    # initialize extensions
    from .api_v1 import blueprint
    api.init_app(blueprint)
    api.add_namespace(main_stats_namespace)
    api.add_namespace(main_heat_load_profile_namespace)
    app.register_blueprint(blueprint)
    db.init_app(app)
    celery = make_celery(app)
    CORS(app, resources={
        r"/api/*": {"origins": {
            "http://hotmaps.hevs.ch",
            "http://hotmaps.hevs.ch:8080",
            "http://hotmaps.hevs.ch:9006",
            "http://172.17.0.5/"
            "http://172.17.0.6/"
            "http://maps.googleapis.com/"
            "http://hotmaps.hevs.ch:9006",
            "http://lesly-hotmaps:4200",
            "http://albain-hotmaps:4200",
            "http://dany-hotmaps:4200",
            "http://hotmapsdev.hevs.ch",
            "http://maps.googleapis.com/maps/api/geocode/",
            "http://maps.googleapis.com/maps/api/",
            "http://maps.googleapis.com/*"
        }
        }})
    return app



#log.info(app)
