from ..decorators.restplus import api
from ..decorators.exceptions import RequestException, ParameterException, UserUnidentifiedException, \
    SnapshotNotExistingException
from ..models.user import User
from ..models.saved_session import SavedSessions
from ..models.cm_indicators import IndicatorsCM
from ..decorators.serializers import saved_session_load_input, saved_session_load_output, saved_session_add_input, \
    saved_session_add_output, saved_session_delete_input, saved_session_delete_output, saved_session_list_input, saved_session_list_output
from app import celery
from flask_restplus import Resource
import datetime

nsSavedsession = api.namespace('scenarios', description='Operations related to scenarios')
ns = nsSavedsession


@ns.route('/add')
@api.response(530, 'Request error')
@api.response(531, 'Missing parameter')
@api.response(539, 'User Unidentified')
class Addsession(Resource):
    @api.marshal_with(saved_session_add_output)
    @api.expect(saved_session_add_input)
    @celery.task(name='add a session')
    def post(self):
        """
        The method called to add a snapshot for the connected user
        :return:
        """
        # Entries
        wrong_parameter = []
        try:
            token = api.payload['token']
        except:
            wrong_parameter.append('token')
        try:
            name_session = api.payload['name']
        except:
            wrong_parameter.append('name_session')
        try:
            name_cm = api.payload['name_cm']
        except:
            wrong_parameter.append('name_cm')
        try:
            indicators = api.payload['indicators']
        except:
            wrong_parameter.append('indicators')

        if len(wrong_parameter) > 0:
            exception_message = ', '.join(wrong_parameter)
            raise ParameterException(str(exception_message))

        # check token
        user = User.verify_auth_token(token)
        if user is None:
            raise UserUnidentifiedException

        time = datetime.utcnow()
        session = SavedSessions(name=name_session, nema_cm=name_cm, saved_at=time, user_id=user.id)
        for indicator in indicators:
            wrong_parameter = []
            try:
                name_indicator = api.payload['name']
            except:
                wrong_parameter.append('name_indicator')
            try:
                unit = api.payload['unit']
            except:
                wrong_parameter.append('unit')
            try:
                value = api.payload['value']
            except:
                wrong_parameter.append('value')

            if len(wrong_parameter) > 0:
                exception_message = ', '.join(wrong_parameter)
                raise ParameterException(str(exception_message))

            indicator = IndicatorsCM(name=name_indicator, unit=unit, value=value, session_id=session.id)
            db.session.add(indicator)
        db.session.add(session)
        db.session.commit()

        # output
        return {
            "message": 'session created successfully'
        }


@ns.route('/list')
@api.response(530, 'Request error')
@api.response(531, 'Missing parameter')
@api.response(539, 'User Unidentified')
class ListSession(Resource):
    @api.marshal_with(session_list_output)
    @api.expect(session_list_input)
    @celery.task(name='list all sessions saved by a user')
    def post(self):
        """
        The method called to list all sessions saved of the connected user
        :return:
        """
        # Entries
        wrong_parameter = []
        try:
            token = api.payload['token']
        except:
            wrong_parameter.append('token')

        if len(wrong_parameter) > 0:
            exception_message = ', '.join(wrong_parameter)
            raise ParameterException(str(exception_message))

        # check token
        user = User.verify_auth_token(token)
        if user is None:
            raise UserUnidentifiedException

        #sessions = SavedSessions.query.filter_by(user_id=user.id).all()
        #print(sessions)
        print(user.sessions)
        all_indicators = []
        for session in user.sessions:
            indicators = IndicatorsCM.query.filter_by(session_id=session.id).all()
            all_indicators.append(indicators)
        print(all_indicators)

        # output
        #return {
        #    "sessions": sessions
        #}
        return {"sessions" : user.sessions, "indicators": all_indicators}


@ns.route('/groups')
@api.response(530, 'Request error')
@api.response(531, 'Missing parameter')
@api.response(539, 'User Unidentified')
class GroupSession(Resource):
    @api.marshal_with(session_list_output)
    @api.expect(session_list_input)
    @celery.task(name='list all sessions grouped together by the user')
    def post(self):
        """
        The method called to list sessions grouped by scenarios by the user
        :return:
        """
        # Entries
        wrong_parameter = []
        try:
            token = api.payload['token']
        except:
            wrong_parameter.append('token')
        try:
            ids = api.payload['ids']
        except:
            wrong_parameter.append('ids')

        if len(wrong_parameter) > 0:
            exception_message = ', '.join(wrong_parameter)
            raise ParameterException(str(exception_message))

        # check token
        user = User.verify_auth_token(token)
        if user is None:
            raise UserUnidentifiedException

        #sessions = SavedSessions.query.filter_by(user_id=user.id).all()

        print(user.sessions)
        # output
        #return {
        #    "sessions": sessions
        #}
        return {"sessions": user.sessions}


@ns.route('/delete')
@api.response(530, 'Request error')
@api.response(531, 'Missing parameter')
@api.response(537, 'Snapshot not existing')
@api.response(539, 'User Unidentified')
class DeleteSnapshot(Resource):
    @api.marshal_with(snapshot_delete_output)
    @api.expect(snapshot_delete_input)
    @celery.task(name='delete a session')
    def delete(self):
        """
        The method called to delete a session of the connected user
        :return:
        """
        # Entries
        wrong_parameter = []
        try:
            token = api.payload['token']
        except:
            wrong_parameter.append('token')
        try:
            id = api.payload['id']
        except:
            wrong_parameter.append('id')

        if len(wrong_parameter) > 0:
            exception_message = ', '.join(wrong_parameter)
            raise ParameterException(str(exception_message))

        # check token
        user = User.verify_auth_token(token)
        if user is None:
            raise UserUnidentifiedException

        session = SavedSessions.query.get(id)
        #print(sessions)

        if session is None:
            raise SessionNotExistingException

        if session.user_id != user.id:
            raise SessionNotExistingException

        db.session.delete(session)
        db.session.commit()

        # output
        return {
            "message": "The session has been deleted"
        }
