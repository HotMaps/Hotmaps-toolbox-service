from flask import Blueprint
blueprint = Blueprint('api', __name__, url_prefix='/api')
from stats import  nsStats
from heat_load_profile import  load_profile_namespace