from .. import dbGIS as db


class IndicatorsCM(db.Model):
    '''
    The model for an indicator of a CM
    '''
    __tablename__ = 'indicators_cm'
    __table_args__ = (
        {
            "schema": 'user',
        }
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    value = db.Column(db.String(255))
    unit = db.Column(db.String(255))
    session_id = db.Column(db.Integer, db.ForeignKey('user.saved_sessions.id'))
