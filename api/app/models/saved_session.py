from .. import dbGIS as db
import datetime

class SavedSessions(db.Model):
    '''
    The model for a session saved by a user
    '''
    __tablename__ = 'saved_sessions'
    __table_args__ = (
        {
            "schema": 'user',
        }
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    saved_at = db.Column(db.DateTime())
    cm_name = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('user.users.id'))
    indicators = db.relationship('IndicatorsCM')
