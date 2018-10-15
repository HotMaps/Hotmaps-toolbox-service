import traceback
import logging

from flask_restplus import Api
from app import constants
from sqlalchemy.orm.exc import NoResultFound
from app.decorators.exceptions import HugeRequestException, IntersectionException, NotEnoughPointsException, ParameterException, RequestException

log = logging.getLogger(__name__)

api = Api(version='1.0',
          title='HotMaps Main API',
          description='HotMaps main API that serves data and computations to the app.'
)

@api.errorhandler(HugeRequestException)
def handle_too_big_request(error):
    '''
    decorator called with an error caused by a too big request
    :param error -- the called error:
    :return:
    '''
    message = 'Your request is too big for the server'
    return {'message': message}, 532
@api.errorhandler(IntersectionException)
def handle_intersection_request(error):
    '''
    decorator called with an error caused by an intersection in a SQL request
    :param error -- the called error:
    :return:
    '''
    message = 'Problem with your point selection'
    return {'message': message}, 533
@api.errorhandler(NotEnoughPointsException)
def handle_not_enough_point(error):
    '''
    decorator called with an error caused by two points or less in a request
    :param error -- the called error:
    :return:
    '''
    message = 'Please specify more than 2 coordinates'
    return {'message': message}, 534
@api.errorhandler(ParameterException)
def handle_false_parameters(error):
    '''
    decorator called with an error caused by wrong parameters
    :param error -- the called error:
    :return:
    '''
    message = 'Missing Parameter: ' + error.message
    return {'message': message}, 531

@api.errorhandler(RequestException)
def handle_request_exception(error):
    '''
    decorator called by default when an error occured in the api
    :param error -- the called error:
    :return:
    '''
    message = error.message
    return {'message': message}, 530

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