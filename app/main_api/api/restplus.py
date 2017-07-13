import traceback
import logging

from flask_restplus import Api, cors
from main_api import settings
from sqlalchemy.orm.exc import NoResultFound


log = logging.getLogger(__name__)

api = Api(version='1.0',
          title='HotMaps Main API',
          description='HotMaps main API that serves data and computations to the app.',
          decorators=[cors.crossdomain(
              origin=settings.CORS_ORIGIN,
              credentials=settings.CORS_CREDENTIALS,
              headers=settings.CORS_HEADERS
          )])

@api.errorhandler
def default_error_handler(e):
    message = 'An unhandled exception occurred.'
    log.exception(message)

    if not settings.FLASK_DEBUG:
        return {'message': message}, 500


@api.errorhandler(NoResultFound)
def database_not_found_error_handler(e):
    log.warning(traceback.format_exc())
    return {'message': 'A models result was required but none was found.'}, 404