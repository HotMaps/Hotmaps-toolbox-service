from .. import dbGIS as db
from flask_security import UserMixin
from .role import Role
from itsdangerous import (TimedJSONWebSignatureSerializer, BadSignature, SignatureExpired)
import sys
from ..secrets import FLASK_SECRET_KEY
import datetime


class User(db.Model, UserMixin):
    '''
    The model for a user in the database
    '''
    __tablename__ = 'users'
    __table_args__ = (
        {
            "schema": 'user',
        }
    )

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())
    last_login_ip = db.Column(db.String(100))
    current_login_ip = db.Column(db.String(100))
    active = db.Column(db.Boolean, default=False)
    confirmed_at = db.Column(db.DateTime())
    active_token = db.Column(db.String(255))
    roles = db.relationship('Role', secondary='user.roles_users', backref=db.backref('user_id', lazy='dynamic'))
    uploads = db.relationship('Uploads')

    @classmethod
    def get_by_email(cls, email):
        '''
        return a user by its email
        :param cls:
        :param email:
        :return: the user
        '''
        return db.session.query(User).filter(User.email == email).first()

    def generate_auth_token(self, expiration=6000):
        '''
        Method called for generating an authentification token for the user that will last for 6000 seconds
        :param expiration:
        :return: the serialized token
        '''
        s = TimedJSONWebSignatureSerializer(FLASK_SECRET_KEY, expires_in=expiration)
        token = s.dumps(
            {
                'id': self.id,
                'date': str(datetime.datetime.now())
            })
        self.active_token = token
        db.session.commit();
        return token

    @staticmethod
    def verify_auth_token(token):
        '''
        Method used to verify if the given token correspond to the user
        :param token:
        :return: the user if it exists, None otherwise
        '''
        s = TimedJSONWebSignatureSerializer(FLASK_SECRET_KEY)
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            return None  # invalid token
        user = User.query.filter_by(id=data['id']).first()
        if user.active_token != token:
            return None  # the user has been logout
        return user


class RolesUsers(db.Model):
    __tablename__ = 'roles_users'
    __table_args__ = (
        {"schema": 'user'}
    )
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column('user_id', db.Integer(), db.ForeignKey('user.users.id'))
    role_id = db.Column('role_id', db.Integer(), db.ForeignKey('user.roles.id'))
