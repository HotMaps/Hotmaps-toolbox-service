from .. import dbGIS as db
from flask_security import UserMixin
from .role import Role

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
    roles = db.relationship('Role', secondary='user.roles_users', backref=db.backref('user_id', lazy='dynamic'))


    @classmethod
    def get_by_email(cls, email):
        '''
        return a user by its email
        :param cls:
        :param email:
        :return: the user
        '''
        return db.session.query(User).filter(User.email == email).first()


class RolesUsers(db.Model):
    __tablename__ = 'roles_users'
    __table_args__ = (
        {"schema": 'user'}
    )
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column('user_id', db.Integer(), db.ForeignKey('user.users.id'))
    role_id = db.Column('role_id', db.Integer(), db.ForeignKey('user.roles.id'))
