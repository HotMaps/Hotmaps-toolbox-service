import datetime

from flask_mail import Message
from flask_restplus import Resource
from flask_security import SQLAlchemySessionUserDatastore
from itsdangerous import (URLSafeTimedSerializer, BadSignature, SignatureExpired)
from passlib.hash import bcrypt

from app import celery
from .upload import calculate_total_space
from .. import constants, mail, login_manager
from ..decorators.exceptions import ParameterException, RequestException, ActivationException, \
    UserExistingException, WrongCredentialException, UserUnidentifiedException, \
    UserNotActivatedException
from ..decorators.restplus import api
from ..decorators.serializers import user_register_input, user_register_output, user_activate_input, \
    user_activate_output, user_ask_recovery_input, user_ask_recovery_output, user_recovery_output, \
    user_recovery_input, user_login_input, user_login_output, user_logout_input, user_logout_output, \
    user_profile_input, user_profile_output, user_get_information_output, user_get_information_input, \
    upload_space_used_output, upload_space_used_input
from .. import dbGIS as db
from ..secrets import FLASK_SECRET_KEY, FLASK_SALT
from ..models.user import User
from ..models.role import Role

# Setup Flask-Security
user_datastore = SQLAlchemySessionUserDatastore(db.session, User, Role)

nsUsers = api.namespace('users', description='Operations related to users')
ns = nsUsers


@ns.route('/recovery/ask')
@api.response(530, 'Request error')
@api.response(531, 'Missing parameter')
class AskingPasswordRecovery(Resource):
    @api.marshal_with(user_ask_recovery_output)
    @api.expect(user_ask_recovery_input)
    @celery.task(name='ask for password recovery')
    def post(self):
        """
		Method to ask for a Password recovery
		:return:
		"""
        # Entries
        try:
            email = api.payload['email']
        except:
            raise ParameterException('email')
        # if the user is not existing, we return a standard error
        if User.get_by_email(email) is None:
            return {
                "message": 'request for recovery successful'
            }
        # mail creation
        user = User.query.filter_by(email=email).first()
        link = constants.CLIENT_URL + "/recover;token_recover=" + generate_confirmation_token(email)
        msg = Message()
        msg.add_recipient(email)
        msg.subject = 'Password recovery for the HotMaps toolbox'
        msg.body = 'Hello ' + user.first_name + ' ' + user.last_name + ' you asked for a password recovery ' \
                                                                       'on your HotMaps account,\n to reset your password, please click on the following link: ' \
                                                                       '\n' + link + '\n if you haven\'t ask for this modification, please delete this email.'
        try:
            mail.send(msg)
        except Exception as e:
            raise RequestException(str(e))

        output = 'request for recovery successful'
        # output
        return {
            "message": output
        }


@ns.route('/recovery')
@api.response(530, 'Request error')
@api.response(531, 'Missing parameter')
@api.response(536, 'Activation failed')
class RecoverPassword(Resource):
    @api.marshal_with(user_recovery_output)
    @api.expect(user_recovery_input)
    @celery.task(name='method for recover of password')
    def post(self):
        """
		Method to recover the password
		:return:
		"""
        # Entries
        wrong_parameter = []
        try:
            token = api.payload['token']
        except:
            wrong_parameter.append('token')
        try:
            unencrypted_password = api.payload['password']
        except:
            wrong_parameter.append('password')
        # raise exception if parameters are false
        if len(wrong_parameter) > 0:
            exception_message = ''
            for i in range(len(wrong_parameter)):
                exception_message += wrong_parameter[i]
                if i != len(wrong_parameter) - 1:
                    exception_message += ', '
            raise ParameterException(exception_message + '')

        # password_encryption
        password = bcrypt.using(salt=FLASK_SALT).hash(str(unencrypted_password))

        # verify mail address
        mail_to_reset = confirm_token(token)
        if not mail_to_reset:
            raise ActivationException()
        else:
            try:
                # reset user password
                user_to_reset = User.query.filter_by(email=mail_to_reset).first()
                user_to_reset.password = password
                db.session.commit()
                output = 'user password reset'
            except Exception as e:
                raise RequestException(str(e))
        # output
        return {
            "message": output
        }


@ns.route('/register')
@api.response(530, 'Request error')
@api.response(531, 'Missing parameter')
@api.response(535, 'User already exists')
class UserRegistering(Resource):
    @api.marshal_with(user_register_output)
    @api.expect(user_register_input)
    @celery.task(name='user registration')
    def post(self):
        """
		Returns the statistics for specific layers, area and year
		:return:
		"""
        # Entries
        wrong_parameter = []
        try:
            first_name = api.payload['first_name']
        except:
            wrong_parameter.append('first_name')
        try:
            last_name = api.payload['last_name']
        except:
            wrong_parameter.append('last_name')
        try:
            email = api.payload['email']
        except:
            wrong_parameter.append('email')
        try:
            unencrypted_password = api.payload['password']
        except:
            wrong_parameter.append('password')
        # raise exception if parameters are false
        if len(wrong_parameter) > 0:
            exception_message = ''
            for i in range(len(wrong_parameter)):
                exception_message += wrong_parameter[i]
                if i != len(wrong_parameter) - 1:
                    exception_message += ', '
            raise ParameterException(exception_message + '')
        # password_encryption
        try:
            password = bcrypt.using(salt=FLASK_SALT).hash(str(unencrypted_password))
        except Exception as e:
            raise RequestException(str(e))
        # we check if the email has already been used
        if User.get_by_email(email) is not None:
            raise UserExistingException(email)

        # user creation in the DB
        user_datastore.create_user(email=email, password=password, active=False, first_name=first_name,
                                   last_name=last_name)
        db.session.commit()

        # mail creation
        try:
            link = constants.CLIENT_URL + "/register;token_activation=" + generate_confirmation_token(email)
            msg = Message()
            msg.add_recipient(email)
            msg.subject = 'Your registration on the HotMaps toolbox'
            msg.body = 'Welcome ' + first_name + ' ' + last_name + ' on the HotMaps toolbox,\n' \
                                                                   'To finalize your registration on the toolbox, please click on the following link: \n' \
                       + link

            mail.send(msg)

        except Exception as e:
            raise RequestException("Problem with the mail sending.")

        output = 'user registered'

        # output
        return {
            "message": output
        }


@ns.route('/register/activate')
@api.response(530, 'Request error')
@api.response(531, 'Missing parameter')
@api.response(536, 'Activation failure')
class ActivateUser(Resource):
    @api.marshal_with(user_activate_output)
    @api.expect(user_activate_input)
    @celery.task(name='user activation')
    def post(self):
        '''
		The method called to activate a user with a token given by email
		:return:
		'''
        # Entries
        try:
            token = api.payload['token']
        except:
            raise ParameterException('token')

        # Find mail to activate
        mail_to_activate = confirm_token(token)
        if not mail_to_activate:
            raise ActivationException()
        else:
            # activate user
            try:
                user_to_activate = User.query.filter_by(email=mail_to_activate).first()
                user_to_activate.active = True
                db.session.commit()
                output = 'user activated'
            except Exception as e:
                raise RequestException(str(e))
        # output
        return {
            "message": output
        }


@ns.route('/login')
@api.response(530, 'Request error')
@api.response(531, 'Missing parameter')
@api.response(537, 'User not existing')
@api.response(538, 'Wrong Password')
class LoginUser(Resource):
    @api.marshal_with(user_login_output)
    @api.expect(user_login_input)
    @celery.task(name='user login')
    def post(self):
        '''
		The method called to login a user
		:return:
		'''
        # Entries
        wrong_parameter = []
        try:
            email = api.payload['email']
        except:
            wrong_parameter.append('email')
        try:
            password = api.payload['password']
        except:
            wrong_parameter.append('password')
        # raise exception if parameters are false
        if len(wrong_parameter) > 0:
            exception_message = ''
            for i in range(len(wrong_parameter)):
                exception_message += wrong_parameter[i]
                if i != len(wrong_parameter) - 1:
                    exception_message += ', '
            raise ParameterException(str(exception_message))

        # find the user in the db
        connecting_user = User.query.filter_by(email=email).first()
        if connecting_user is None:
            raise WrongCredentialException
        # check password
        if not bcrypt.using(salt=FLASK_SALT).verify(password, connecting_user.password):
            raise WrongCredentialException

        if connecting_user.active is False:
            raise UserNotActivatedException

        token = User.generate_auth_token(connecting_user)

        # output
        output = 'user connected'

        return {
            "message": output,
            "token": token
        }


@ns.route('/logout')
@api.response(530, 'Request error')
@api.response(531, 'Missing parameter')
@api.response(539, 'User Unidentified')
class LogoutUser(Resource):
    @api.marshal_with(user_logout_output)
    @api.expect(user_logout_input)
    @celery.task(name='user logout')
    def post(self):
        '''
		The method called to logout a user
		:return:
		'''
        try:
            token = api.payload['token']
        except:
            raise ParameterException('token')

        # check token
        user = User.verify_auth_token(token)
        if user is None:
            raise UserUnidentifiedException
        user.active_token = None
        db.session.commit()

        # output
        output = 'user disconnected'

        return {
            "message": output
        }


@ns.route('/profile/update')
@api.response(530, 'Request error')
@api.response(531, 'Missing parameter')
@api.response(539, 'User Unidentified')
class ProfileUser(Resource):
    @api.marshal_with(user_profile_output)
    @api.expect(user_profile_input)
    @celery.task(name='user profile update')
    def post(self):
        '''
        The method called to update the profile of a user
        :return:
        '''
        # Entries
        wrong_parameter = []
        try:
            token = api.payload['token']
        except:
            wrong_parameter.append('token')
        try:
            first_name = api.payload['first_name']
        except:
            wrong_parameter.append('first_name')
        try:
            last_name = api.payload['last_name']
        except:
            wrong_parameter.append('last_name')
        # raise exception if parameters are false
        if len(wrong_parameter) > 0:
            exception_message = ''
            for i in range(len(wrong_parameter)):
                exception_message += wrong_parameter[i]
                if i != len(wrong_parameter) - 1:
                    exception_message += ', '
            raise ParameterException(str(exception_message))

        # check token
        user = User.verify_auth_token(token)
        if user is None:
            raise UserUnidentifiedException

        # select and update the user
        user_to_modify = User.query.filter_by(email=user.email).first()
        user_to_modify.first_name = first_name
        user_to_modify.last_name = last_name
        db.session.commit()

        # output
        output = 'User ' + last_name + ' ' + first_name + ' updated'

        return {
            "message": output
        }


@ns.route('/information')
@api.response(530, 'Request error')
@api.response(531, 'Missing parameter')
@api.response(539, 'User Unidentified')
class GetUserInformation(Resource):
    @api.marshal_with(user_get_information_output)
    @api.expect(user_get_information_input)
    @celery.task(name='get user informations')
    def post(self):
        '''
        The method called to return the infos of a user by its token
        :return:
        '''
        # Entries
        try:
            token = api.payload['token']
        except:
            raise ParameterException('token')

        # check token
        user = User.verify_auth_token(token)
        if user is None:
            raise UserUnidentifiedException

        # get the user informations
        first_name = user.first_name
        last_name = user.last_name
        email = user.email

        # output
        return {
            'first_name': first_name,
            'last_name': last_name,
            'email': email
        }


@ns.route('/space_used')
@api.response(530, 'Request error')
@api.response(531, 'Missing parameter')
@api.response(539, 'User Unidentified')
class SpaceUsedUploads(Resource):
    @api.marshal_with(upload_space_used_output)
    @api.expect(upload_space_used_input)
    @celery.task(name='get user space used')
    def post(self):
        """
        The method called to see the space used by an user
        :return:
        """
        # Entries
        try:
            token = api.payload['token']
        except:
            raise ParameterException('token')

        # check token
        user = User.verify_auth_token(token)
        if user is None:
            raise UserUnidentifiedException

        # get the user uploads
        uploads = user.uploads
        used_size = calculate_total_space(uploads)

        # output
        return {
            "used_size": used_size,
            "max_size": constants.USER_DISC_SPACE_AVAILABLE
        }

def generate_confirmation_token(email):
    """
	this method will generate a confirmation token
	:return: the confirmation token
	"""
    s = URLSafeTimedSerializer(FLASK_SECRET_KEY, salt=FLASK_SALT)
    token = s.dumps(
        {
            'email': email,
            'date': str(datetime.datetime.now())
        })
    user = User.query.filter_by(email=email).first()
    user.active_token = token
    db.session.commit();
    return token


def confirm_token(token, expiration=3600):
    '''
	This method will confirm that the given token is correct
	:param token:
	:param expiration:
	:return:
	'''
    s = URLSafeTimedSerializer(FLASK_SECRET_KEY, salt=FLASK_SALT)
    try:
        data = s.loads(token)
    except SignatureExpired:
        return None  # valid token, but expired
    except BadSignature:
        return None  # invalid token
    user = User.query.filter_by(email=data['email']).first()
    if user.active_token != token:
        return None  # the user has been logout
    user.active_token="None"
    return user.email

@login_manager.user_loader
def load_user(user_id):
    '''
	this method will return the current user
	:param user_id:
	:return:
	'''
    return User.query.filter_by(id=user_id).first()
