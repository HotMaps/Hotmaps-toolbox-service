from ..decorators.restplus import api
from ..decorators.exceptions import RequestException, ParameterException, UserUnidentifiedException, \
    SessionNotExistingException
from ..decorators.serializers import session_delete_input, session_delete_output, \
    session_list_input, session_group_input

from ..models.user import User
from ..models.saved_session import SavedSessions
from ..models.cm_indicators import IndicatorsCM

from app import celery
from flask_restplus import Resource
import datetime

nsScenarios = api.namespace('scenarios', description='Operations related to scenarios')
ns = nsScenarios

@ns.route('/add')
@api.response(530, 'Request error')
@api.response(531, 'Missing parameter')
@api.response(539, 'User Unidentified')
class AddSession(Resource):
    @celery.task(name='add a session')
    def post(payload_front, response_cm):
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

        sessions = SavedSessions.query.filter_by(user_id=user.id).all()
        #print(sessions)

        output = {}
        for session in sessions:
            #print(session)
            if session['cm_name'] not in output:
                output[session['cm_name']] = []
            output[session['cm_name']].append({'id':session['id'], 'session_name':session['session_name'], 'saved_at':session['saved_at']})
        #print(output)

        return {"result" : output }


@ns.route('/group')
@api.response(530, 'Request error')
@api.response(531, 'Missing parameter')
@api.response(537, 'Session not existing')
@api.response(539, 'User Unidentified')
class GroupSession(Resource):
    @api.expect(session_group_input)
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
            sessions = api.payload['cm_sessions']
        except:
            wrong_parameter.append('cm_sessions')
        try:
            scenario_assessment = api.payload['scenario_assessment']
        except:
            wrong_parameter.append('scenario_assessment')

        if len(wrong_parameter) > 0:
            exception_message = ', '.join(wrong_parameter)
            raise ParameterException(str(exception_message))

        # check token
        user = User.verify_auth_token(token)
        if user is None:
            raise UserUnidentifiedException

        for element in cm_sessions:
            #TODO
            session = SavedSessions.query.get(element['session_id'])
            if session is None:
                raise SessionNotExistingException
            if session.user_id != user.id:
                raise SessionNotExistingException
            print(session)

        for element in scenario_assessment:
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
class DeleteSession(Resource):
    @api.marshal_with(session_delete_output)
    @api.expect(session_delete_input)
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
