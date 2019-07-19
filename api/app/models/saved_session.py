from .. import dbGIS as db
import datetime

from ..decorators.exceptions import ParameterException, UserUnidentifiedException, \
    SessionNotExistingException
from ..decorators.restplus import api

from ..models.user import User
from ..models.cm_indicators import IndicatorsCM

from app import celery

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


@api.response(530, 'Request error')
@api.response(531, 'Missing parameter')
@api.response(539, 'User Unidentified')
@celery.task(name='add a session')
def save_session(payload_front, response_cm):
    """
    The method called to add a snapshot for the connected user
    :return:
    """
    print('adding session in the database')

    # Entries
    wrong_parameter = []
    try:
        token = payload_front['token']
    except:
        wrong_parameter.append('token')
    try:
        name_session = payload['name_session']
    except:
        wrong_parameter.append('name_session')
    try:
        name_cm = response_cm['name']
    except:
        wrong_parameter.append('name')
    try:
        indicators = response_cm['indicator']
    except:
        wrong_parameter.append('indicator')

    if len(wrong_parameter) > 0:
        exception_message = ', '.join(wrong_parameter)
        raise ParameterException(str(exception_message))

    # check token
    user = User.verify_auth_token(token)
    if user is None:
        raise UserUnidentifiedException

    time = datetime.utcnow()
    session = SavedSessions(name=name_session, name_cm=name_cm, saved_at=time, user_id=user.id)
    db.session.add(session)

    for indicator in indicators:
        wrong_parameter = []
        try:
            name_indicator = indicator['name']
        except:
            wrong_parameter.append('name_indicator')
        try:
            unit = indicator['unit']
        except:
            wrong_parameter.append('unit')
        try:
            value = indicator['value']
        except:
            wrong_parameter.append('value')

        if len(wrong_parameter) > 0:
            exception_message = ', '.join(wrong_parameter)
            raise ParameterException(str(exception_message))

        indicator = IndicatorsCM(name=name_indicator, unit=unit, value=value, session_id=session.id)
        db.session.add(indicator)

    db.session.commit()

    # output
    return {
        "message": 'session created successfully'
    }
