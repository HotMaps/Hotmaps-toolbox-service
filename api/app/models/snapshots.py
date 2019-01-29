from .. import dbGIS as db
from ..decorators.restplus import UserUnidentifiedException, ParameterException, RequestException


class Snapshots(db.Model):
    '''
    This class will describe the model of the snapshot for a user
    '''
    __tablename__ = 'snapshot'
    __table_args__ = (
        {"schema": 'user'}
    )

    id = db.Column(db.Integer, primary_key=True)
    config = db.Column(db.Text())
    user_id = db.Column(db.Integer, db.ForeignKey('user.users.id'))
