from flask import Blueprint
api = Blueprint('api', __name__, url_prefix='/api')
from .stats import nsStats
from .heat_load_profile import  load_profile_namespace
from ..decorators import etag
from .computation_module import nsCM
from .users import nsUsers
from .upload import nsUpload
from .snapshot import nsSnapshot

@api.before_request
def before_request():
    """All routes in this blue#print require authentication."""
    pass


@api.after_request
@etag
def after_request(rv):
    """Generate an ETag header for all routes in this blue#print."""

    return rv

from . import computation_module
# from . import  computation, errors
