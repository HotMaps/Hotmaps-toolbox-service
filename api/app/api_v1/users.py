from app import celery
import logging
import re

from flask_restplus import Resource
from app.decorators.serializers import user_register_input, user_register_output
from app.decorators.restplus import api
from app.decorators.exceptions import HugeRequestException, IntersectionException, NotEnoughPointsException, ParameterException, RequestException
from app import constants
from app.models import generalData
from app.helper import find_key_in_dict, getValuesFromName, retrieveCrossIndicator
from ..models.user import User
import app
from .. import dbGIS as db
from .. import user_datastore, mail
from celery.utils.log import get_task_logger
import json
from passlib.hash import pbkdf2_sha256
from flask_mail import Message

from app import log

nsUsers = api.namespace('users', description='Operations related to users')
ns = nsUsers


@ns.route('/register')
@api.response(530, 'Request error')
@api.response(531, 'Missing parameter')
class UserRegistering(Resource):
	@api.marshal_with(user_register_output)
	@api.expect(user_register_input)
	def post(self):
		"""
		Returns the statistics for specific layers, area and year
		:return:
		"""
		# Entrees
		wrong_parameter = [];
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
		# TODO we need https to avoid the password being passed in the request body clearly
		try:
			#password_encryption
			password = pbkdf2_sha256.hash(str(unencrypted_password))

			#we check if the email has already been used
			if(User.get_by_email(email) is not None):
				return {
					"message": 'the user '+email+' already exists !'
				}
			#user creation in the DB
			user_datastore.create_user(email=email, password=password)
			db.session.commit()
			output = 'user registered'

			#mail creation
			# msg = Message()
			# msg.body = "Testing"
			# msg.add_recipient(email)
			#TODO set up the default mail sender on the MAIL_DEFAULT_SENDER parameter

			#mail.send(msg)

		except Exception, e:
			raise RequestException(str(e))

		# output
		return {
			"message": output
		}