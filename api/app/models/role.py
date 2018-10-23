from .. import dbGIS as db
from flask_security import RoleMixin

class Role(db.Model, RoleMixin):
    '''
    The model for a user in the database
    '''
    __tablename__ = 'roles'
    __table_args__ = (
        {
            "schema": 'user',
        }
    )
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

