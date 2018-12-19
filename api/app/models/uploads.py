import json
from .. import dbGIS as db


class Uploads(db.Model):
    '''
    This class will describe the model of a file uploaded by a user
    '''
    __tablename__ = 'uploads'
    __table_args__ = (
        {"schema": 'user'}
    )

    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(255))
    size = db.Column(db.Numeric)
    url = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('user.users.id'))
