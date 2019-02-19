import traceback
import logging

from flask_restplus import Api
from .. import constants
from sqlalchemy.orm.exc import NoResultFound
from ..decorators.exceptions import HugeRequestException, IntersectionException, NotEnoughPointsException, \
    ParameterException, RequestException, ActivationException, UserExistingException, \
    WrongCredentialException, UserUnidentifiedException, UserDoesntOwnUploadsException, NotEnoughSpaceException, \
    UploadNotExistingException, UserNotActivatedException, SnapshotNotExistingException

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
       "message": message,
       "error": {
          "message": message,
          "status": "530",
          "statusText": "REQUEST"
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
        "message": message,
        "error": {
              "message": message,
              "status": "531",
              "statusText": "PARAMETERS"
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
        "error": {
            "message": message,
            "status": "532",
            "statusText": "HUGE REQUEST"
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
        "error": {
            "message": message,
            "status": "533",
            "statusText": "INTERSECTION"
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
        "error": {
            "message": message,
            "status": "534",
            "statusText": "NOT ENOUGH POINTS"
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
        "error": {
            "message": message,
            "status": "535",
            "statusText": "USER EXISTING"
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
        "error": {
            "message": message,
            "status": "536",
            "statusText": "ACTIVATION"
        }
    }
    return response, 536


@api.errorhandler(SnapshotNotExistingException)
def handle_activation_failure(error):
    '''
    decorator called with an error caused when you reach a non existing snapshot
    :param error -- the called error:
    :return:
    '''
    message = 'This snapshot does not exists'
    response = {
        "message": message,
        "error": {
            "message": message,
            "status": "537",
            "statusText": "SNAPSHOT MISSING"
        }
    }
    return response, 537


@api.errorhandler(WrongCredentialException)
def handle_wrong_credential(error):
    '''
    decorator called with an error caused when the credentials entered are wrong
    :param error -- the called error:
    :return:
    '''
    message = 'The credentials are wrong'
    response = {
        "message": message,
        "error": {
            "message": message,
            "status": "538",
            "statusText": "WRONG CREDENTIAL"
        }
    }
    return response, 538


@api.errorhandler(UserUnidentifiedException)
def handle_unidentified_user(error):
    '''
    decorator called with an error caused when the user is not identified
    :param error -- the called error:
    :return:
    '''
    message = 'There is no authenticated user'
    response = {
        "message": message,
        "error": {
            "message": message,
            "status": "539",
            "statusText": "USER UNIDENTIFIED"
        }
    }
    return response, 539


@api.errorhandler(UserDoesntOwnUploadsException)
def handle_doesnt_own_upload(error):
    '''
    decorator called with an error caused when trying to delete an upload not belonging to the user
    :param error -- the called error:
    :return:
    '''
    message = 'The current user does not own the upload'
    response = {
        "message": message,
        "error": {
            "message": message,
            "status": "540",
            "statusText": "USER NOT OWNER"
        }
    }
    return response, 540


@api.errorhandler(NotEnoughSpaceException)
def handle_not_enough_space(error):
    '''
    decorator called with an error caused when trying to create an upload that will exceed the space limit
    :param error -- the called error:
    :return:
    '''
    message = 'Not enough space on your data storage'
    response = {
        "message": message,
        "error": {
            "message": message,
            "status": "542",
            "statusText": "NOT ENOUGH SPACE"
            }
        }
    return response, 542


@api.errorhandler(UploadNotExistingException)
def handle_not_enough_space(error):
    '''
    decorator called with an error caused when trying to access a non existing upload
    :param error -- the called error:
    :return:
    '''
    message = 'There is no upload on this URL'
    response = {
        "message": message,
        "error": {
            "message": message,
            "status": "543",
            "statusText": "NO UPLOAD FOUND"
            }
        }
    return response, 543


@api.errorhandler(UserNotActivatedException)
def handle_user_not_activated(error):
    '''
    decorator called with an error caused when a non activated user try to connect
    :param error -- the called error:
    :return:
    '''
    message = 'Please activate your user before connection'
    response = {
        "message": message,
        "error": {
            "message": message,
            "status": "544",
            "statusText": "USER NOT ACTIVATED"
            }
        }
    return response, 544


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