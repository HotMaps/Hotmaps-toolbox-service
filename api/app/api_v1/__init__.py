from flask import Blueprint
api = Blueprint('api', __name__, url_prefix='/api')
# from .stats import nsStats
# from .heat_load_profile import  load_profile_namespace
# from .computation_module import nsCM
from .users import nsUsers
from ..decorators import etag
#from . import computation_module
#from . import  computation, errors

@api.before_request
def before_request():
    """All routes in this blueprint require authentication."""
    pass


@api.after_request
@etag
def after_request(rv):
    """Generate an ETag header for all routes in this blueprint."""

    return rv