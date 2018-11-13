from .. import constants
from ..decorators.exceptions import ParameterException, RequestException, ActivationException, \
    UserExistingException, UserNotExistingException, WrongPasswordException, UserUnidentifiedException,\
    UserNotActivatedException
from ..decorators.restplus import api
from ..decorators.serializers import user_register_input, user_register_output, user_activate_input, \
    user_activate_output, user_ask_recovery_input, user_ask_recovery_output, user_recovery_output, \
    user_recovery_input, user_login_input, user_login_output, user_logout_input, user_logout_output, user_profile_input, \
    user_profile_output
from flask_mail import Message
from flask_restplus import Resource
from flask_login import login_user, logout_user, login_required
from flask_security import SQLAlchemySessionUserDatastore
from itsdangerous import URLSafeTimedSerializer
from passlib.hash import bcrypt

from .. import dbGIS as db
from .. import mail, login_manager
from ..secrets import FLASK_SECRET_KEY, FLASK_SALT
from ..models.user import User
from ..models.role import Role
from ..models.uploads import Uploads

# Setup Flask-Security
user_datastore = SQLAlchemySessionUserDatastore(db.session, User, Role)

nsUsers = api.namespace('users', description='Operations related to users')
ns = nsUsers


@ns.route('/recovery/ask')
@api.response(530, 'Request error')
@api.response(531, 'Missing parameter')
@api.response(537, 'Users not existing')
class AskingPasswordRecovery(Resource):
    @api.marshal_with(user_ask_recovery_output)
    @api.expect(user_ask_recovery_input)
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

        # we check if the email has already been used
        if User.get_by_email(email) is None:
            raise UserNotExistingException(email)
        # mail creation
        user = User.query.filter_by(email=email).first()
        link = generate_confirmation_token(email)
        msg = Message()
        msg.add_recipient(email)
        msg.subject = 'Password recovery for the HotMaps toolbox'
        msg.body = 'Hello ' + user.first_name + ' ' + user.last_name + ' you asked for a password recovery ' \
                                                                       'on your HotMaps account,\n to reset your password, please click on the following link: ' \
                                                                       '\n' + link + '\n if you haven\'t ask for this modification, please delete this email.'

        mail.send(msg)

        output = 'request for recovery successful'

        # output
        return {
            "message": output
        }


@ns.route('/recovery')
@api.response(530, 'Request error')
@api.response(531, 'Missing parameter')
@api.response(537, 'Activation failed')
class AskingPasswordRecovery(Resource):
    @api.marshal_with(user_recovery_output)
    @api.expect(user_recovery_input)
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
            # reset user password
            user_to_reset = User.query.filter_by(email=mail_to_reset).first()
            user_to_reset.password = password
            db.session.commit()
            output = 'user password reset'
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
        password = bcrypt.using(salt=FLASK_SALT).hash(str(unencrypted_password))
        # we check if the email has already been used
        if User.get_by_email(email) is not None:
            raise UserExistingException(email)
        # user creation in the DB
        user_datastore.create_user(email=email, password=password, active=False, first_name=first_name,
                                   last_name=last_name)
        db.session.commit()

        # mail creation
        link = generate_confirmation_token(email)
        msg = Message()
        msg.add_recipient(email)
        msg.subject = 'Your registration on the HotMaps toolbox'
        msg.body = 'Welcome ' + first_name + ' ' + last_name + ' on the HotMaps toolbox,\n' \
                                                               'To finalize your registration on the toolbox, please click on the following link: \n' \
                   + link

        mail.send(msg)

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
            except Exception, e:
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
            raise UserNotExistingException
        # check password
        if not bcrypt.using(salt=FLASK_SALT).verify(password, connecting_user.password):
            raise WrongPasswordException

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
@api.response(539, 'User Unidentified')
class LogoutUser(Resource):
    @api.marshal_with(user_logout_output)
    @api.expect(user_logout_input)
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
@api.response(537, 'User Unidentified')
class ProfileUser(Resource):
    @api.marshal_with(user_profile_output)
    @api.expect(user_profile_input)
    def post(self):
        '''
        The method called to update the profile of a user
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
        # raise exception if parameters are false
        if len(wrong_parameter) > 0:
            exception_message = ''
            for i in range(len(wrong_parameter)):
                exception_message += wrong_parameter[i]
                if i != len(wrong_parameter) - 1:
                    exception_message += ', '
            raise ParameterException(str(exception_message))

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


def generate_confirmation_token(email):
    '''
	this method will generate a confirmation token
	:return: the confirmation token
	'''
    serializer = URLSafeTimedSerializer(FLASK_SECRET_KEY, salt=FLASK_SALT)
    return serializer.dumps(email)


def confirm_token(token, expiration=3600):
    '''
	This method will confirm that the given token is correct
	:param token:
	:param expiration:
	:return:
	'''
    serializer = URLSafeTimedSerializer(FLASK_SECRET_KEY, salt=FLASK_SALT)
    try:
        email = serializer.loads(
            token,
            max_age=expiration
        )
    except:
        return False
    return email


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()
