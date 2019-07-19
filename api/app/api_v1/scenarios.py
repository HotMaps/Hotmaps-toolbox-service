from ..decorators.restplus import api
from ..decorators.exceptions import RequestException, ParameterException, UserUnidentifiedException, \
    SessionNotExistingException
from ..decorators.serializers import session_delete_input, session_delete_output, \
    session_list_input, session_list_output

from ..models.user import User
from ..models.saved_session import SavedSessions
from ..models.cm_indicators import IndicatorsCM

from app import celery
from flask_restplus import Resource
import datetime

nsScenarios = api.namespace('scenarios', description='Operations related to scenarios')
ns = nsScenarios


@ns.route('/list')
@api.response(530, 'Request error')
@api.response(531, 'Missing parameter')
@api.response(539, 'User Unidentified')
class ListSession(Resource):
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
        sessions = user.sessions
        #print(sessions)

        output = {}
        for session in sessions:
            #print(session)
            if session['cm_name'] not in output:
                output[session['cm_name']] = []
            output[session['cm_name']].append({'id':session['id'], 'session_name':session['session_name'], 'saved_at':session['saved_at']})
        #print(output)

        return {"output" : output }


@ns.route('/group')
@api.response(530, 'Request error')
@api.response(531, 'Missing parameter')
@api.response(537, 'Session not existing')
@api.response(539, 'User Unidentified')
class GroupSession(Resource):
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
            sessions = api.payload['sessions']
        except:
            wrong_parameter.append('sessions')

        if len(wrong_parameter) > 0:
            exception_message = ', '.join(wrong_parameter)
            raise ParameterException(str(exception_message))

        # check token
        user = User.verify_auth_token(token)
        if user is None:
            raise UserUnidentifiedException

        for element in sessions:
            #TODO
            session = SavedSessions.query.get(element['session_id'])
            if session is None:
                raise SessionNotExistingException
            if session.user_id != user.id:
                raise SessionNotExistingException
            print(session)


        # output
        return {"output": "TODO"}


@ns.route('/delete')
@api.response(530, 'Request error')
@api.response(531, 'Missing parameter')
@api.response(537, 'Session not existing')
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
