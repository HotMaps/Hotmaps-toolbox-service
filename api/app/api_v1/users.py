from .. import constants
from ..decorators.exceptions import ParameterException, RequestException, ActivationException, \
	UserExistingException, UserNotExistingException
from ..decorators.restplus import api
from ..decorators.serializers import user_register_input, user_register_output, user_activate_input, \
	user_activate_output, user_ask_recovery_input, user_ask_recovery_output, user_recovery_output, user_recovery_input
from flask_mail import Message
from flask_restplus import Resource
from itsdangerous import URLSafeTimedSerializer
from passlib.hash import pbkdf2_sha256

from .. import dbGIS as db
from .. import user_datastore, mail
from ..models.user import User
from ..secrets import FLASK_SECRET_KEY

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

		#we check if the email has already been used
		if(User.get_by_email(email) is None):
			raise UserNotExistingException(email)
		try:
			#mail creation
			user = User.query.filter_by(email=email).first()
			link = constants.API_URL_LOCAL_DOCKER + '/recovery/' + generate_confirmation_token(email)
			msg = Message()
			msg.add_recipient(email)
			msg.subject = 'Password recovery for the HotMaps toolbox'
			msg.body = 'Hello ' + user.first_name + ' ' + user.last_name + ' you asked for a password recovery on your HotMaps account,\n' \
			   'to reset your password, please click on the following link: \n'+ link + \
			   '\n if you haven\'t ask for this modification, please delete this email.'

			mail.send(msg)
		except Exception, e:
			raise RequestException(str(e))
		output = 'request for recovery successful'

		# output
		return {
			"message": output
		}

@ns.route('/recovery')
@api.response(530, 'Request error')
@api.response(531, 'Missing parameter')
@api.response(537, 'Users not existing')
class AskingPasswordRecovery(Resource):
	@api.marshal_with(user_recovery_output)
	@api.expect(user_recovery_input)
	def post(self):
		"""
		Method to ask for a Password recovery
		:return:
		"""
		# Entries
		wrong_parameter=''
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
				if (i != len(wrong_parameter) - 1):
					exception_message += ', '
			raise ParameterException(exception_message + '')

		#password_encryption
		password = pbkdf2_sha256.hash(str(unencrypted_password))

		#verify mail adress
		mail_to_reset = confirm_token(token)
		if(mail_to_reset == False):
			raise ActivationException()
		else:
			try:
				#reset user password
				user_to_reset = User.query.filter_by(email=mail_to_reset).first()
				user_to_reset.password = password
				db.session.commit()
				output = 'user password reset'
			except Exception, e:
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
				if (i != len(wrong_parameter) - 1):
					exception_message += ', '
			raise ParameterException(exception_message + '')
		#password_encryption
		password = pbkdf2_sha256.hash(str(unencrypted_password))

		#we check if the email has already been used
		if(User.get_by_email(email) is not None):
			raise UserExistingException(email)
		try:
		#user creation in the DB
			user_datastore.create_user(email=email, password=password, active=False, first_name = first_name, last_name = last_name)
			db.session.commit()

			#mail creation
			link = constants.API_URL_LOCAL_DOCKER + '/confirm/' + generate_confirmation_token(email)
			msg = Message()
			msg.add_recipient(email)
			msg.subject = 'Your registration on the HotMaps toolbox'
			msg.body = 'Welcome ' + first_name + ' ' + last_name + ' on the HotMaps toolbox,\n' \
			   'To finalize your registration on the toolbox, please click on the following link: \n'\
				+ link

			mail.send(msg)
		except Exception, e:
			raise RequestException(str(e))
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

		#Find mail to activate
		mail_to_activate = confirm_token(token)
		if(mail_to_activate == False):
			raise ActivationException()
		else:
			#activate user
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

def generate_confirmation_token(email):
	'''
	this method will generate a confirmation token
	:return: the confirmation token
	'''
	serializer = URLSafeTimedSerializer(FLASK_SECRET_KEY)
	return serializer.dumps(email)

def confirm_token(token, expiration=3600):
	'''
	This method will confirm that the given token is correct
	:param token:
	:param expiration:
	:return:
	'''
	serializer = URLSafeTimedSerializer(FLASK_SECRET_KEY)
	try:
		email = serializer.loads(
			token,
			max_age=expiration
		)
	except:
		return False
	return email