import traceback
import logging

from flask_restplus import Api
from .. import constants
from sqlalchemy.orm.exc import NoResultFound
from ..decorators.exceptions import HugeRequestException, IntersectionException, NotEnoughPointsException, \
    ParameterException, RequestException, ActivationException, UserExistingException, UserNotExistingException, \
    WrongPasswordException, UserUnidentifiedException

log = logging.getLogger(__name__)

api = Api(
    version='1.0',
    title='HotMaps Main API',
    description='HotMaps main API that serves data and computations to the app.'
)


@api.errorhandler(RequestException)
def handle_request_exception(error):
    '''
    decorator called by default when an error occured in the api
    :param error -- the called error:
    :return:
    '''
    message = error.message
    response = {
           "message":message,
           "error":{
              "message":message,
              "status":"530",
              "statusText":"REQUEST"
           }
        }
    return response, 530


@api.errorhandler(ParameterException)
def handle_false_parameters(error):
    '''
    decorator called with an error caused by wrong parameters
    :param error -- the called error:
    :return:
    '''
    message = 'Missing Parameter: ' + error.message
    response = {
        "message":message,
        "error":{
              "message":message,
              "status":"531",
              "statusText":"PARAMETERS"
           }
        }
    return response, 531


@api.errorhandler(HugeRequestException)
def handle_too_big_request(error):
    '''
    decorator called with an error caused by a too big request
    :param error -- the called error:
    :return:
    '''
    message = 'Your request is too big for the server'
    response = {
        "message": message,
           "error":{
              "message":message,
              "status":"532",
              "statusText":"HUGE REQUEST"
           }
        }
    return response, 532


@api.errorhandler(IntersectionException)
def handle_intersection_request(error):
    '''
    decorator called with an error caused by an intersection in a SQL request
    :param error -- the called error:
    :return:
    '''
    message = 'Problem with your point selection'
    response = {
        "message": message,
           "error":{
              "message":message,
              "status":"533",
              "statusText":"INTERSECTION"
           }
        }
    return response, 533


@api.errorhandler(NotEnoughPointsException)
def handle_not_enough_point(error):
    '''
    decorator called with an error caused by two points or less in a request
    :param error -- the called error:
    :return:
    '''
    message = 'Please specify more than 2 coordinates'
    response = {
        "message": message,
           "error":{
              "message":message,
              "status":"534",
              "statusText":"NOT ENOUGH POINTS"
           }
        }
    return response, 534


@api.errorhandler(UserExistingException)
def handle_mail_existing(error):
    '''
    decorator called with an error caused trying to create a second account with the same email
    :param error -- the called error:
    :return:
    '''
    message = 'the user '+error.message+' already exists !'
    response = {
        "message": message,
           "error":{
              "message":message,
              "status":"535",
              "statusText":"USER EXISTING"
           }
        }
    return response, 535


@api.errorhandler(ActivationException)
def handle_activation_failure(error):
    '''
    decorator called with an error caused when the activation of a user fail
    :param error -- the called error:
    :return:
    '''
    message = 'Can\'t activate the user'
    response = {
        "message": message,
           "error":{
              "message":message,
              "status":"536",
              "statusText":"ACTIVATION"
           }
        }
    return response, 536


@api.errorhandler(UserNotExistingException)
def handle_inexisting_user(error):
    '''
    decorator called with an error caused when trying to reach a non-existing user
    :param error -- the called error:
    :return:
    '''
    message = 'User ' + error.message + 'does not exists'
    response = {
        "message": message,
           "error":{
              "message":message,
              "status":"537",
              "statusText":"USER NOT EXISTING"
           }
        }
    return response, 537


@api.errorhandler(WrongPasswordException)
def handle_inexisting_user(error):
    '''
    decorator called with an error caused when trying to reach a non-existing user
    :param error -- the called error:
    :return:
    '''
    message = 'The password does not match the user'
    response = {
        "message": message,
           "error":{
              "message":message,
              "status":"538",
              "statusText":"WRONG PASSWORD"
           }
        }
    return response, 538


@api.errorhandler(UserUnidentifiedException)
def handle_inexisting_user(error):
    '''
    decorator called with an error caused when trying to reach a non-existing user
    :param error -- the called error:
    :return:
    '''
    message = 'There is no authenticated user'
    response = {
        "message": message,
           "error":{
              "message":message,
              "status":"539",
              "statusText":"USER UNIDENTIFIED"
           }
        }
    return response, 539


@api.errorhandler
def default_error_handler(e):
    message = 'An unhandled exception occurred.'
    log.exception(message)

    if not constants.FLASK_DEBUG:
        return {'message': message}, 500


@api.errorhandler(NoResultFound)
def database_not_found_error_handler(e):
    log.warning(traceback.format_exc())
    return {'message': 'A models result was required but none was found.'}, 404