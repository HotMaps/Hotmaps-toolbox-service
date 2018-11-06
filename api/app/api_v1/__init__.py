from flask import Blueprint
# from .stats import nsStats
# from .heat_load_profile import  load_profile_namespace
# from .computation_module import nsCM
from .users import nsUsers
from.upload import nsUpload
from ..decorators import etag
# from . import computation_module
# from . import  computation, errors

api = Blueprint('api', __name__, url_prefix='/api')

@api.before_request
def before_request():
    """All routes in this blueprint require authentication."""
    pass


@api.after_request
@etag
def after_request(rv):
    """Generate an ETag header for all routes in this blueprint."""

    return rv