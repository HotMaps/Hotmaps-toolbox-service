from .. import dbGIS as db
from ..decorators.restplus import api
from ..decorators.exceptions import RequestException, ParameterException, UserUnidentifiedException, \
    SnapshotNotExistingException
from ..models.user import User
from ..models.snapshots import Snapshots
from ..decorators.serializers import snapshot_load_input, snapshot_load_output, snapshot_add_input, \
    snapshot_add_output, snapshot_delete_input, snapshot_delete_output, snapshot_list_input, snapshot_list_output, \
    snapshot_update_input, snapshot_update_output
from app import celery
from flask_restplus import Resource

nsSnapshot = api.namespace('snapshot', description='Operations related to snapshots')
ns = nsSnapshot


@ns.route('/add')
@api.response(530, 'Request error')
@api.response(531, 'Missing parameter')
@api.response(539, 'User Unidentified')
class AddSnapshot(Resource):
    @api.marshal_with(snapshot_add_output)
    @api.expect(snapshot_add_input)
    @celery.task(name='config a snapshot')
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
            config = api.payload['config']
        except:
            wrong_parameter.append('config')

        if len(wrong_parameter) > 0:
            exception_message = ''
            for i in range(len(wrong_parameter)):
                exception_message += wrong_parameter[i]
                if i != len(wrong_parameter) - 1:
                    exception_message += ', '
            raise ParameterException(str(exception_message))
        # check token
        user = User.verify_auth_token(token)
        if user is None:
            raise UserUnidentifiedException

        snapshot = Snapshots(config=config, user_id=user.id)
        db.session.add(snapshot)
        db.session.commit()

        # output
        return {
            "message": 'snapshot created successfully'
        }


@ns.route('/load')
@api.response(530, 'Request error')
@api.response(531, 'Missing parameter')
@api.response(537, 'Snapshot not existing')
@api.response(539, 'User Unidentified')
class LoadSnapshot(Resource):
    @api.marshal_with(snapshot_load_output)
    @api.expect(snapshot_load_input)
    @celery.task(name='load a snapshot')
    def post(self):
        """
        The method called to load a snapshot of the connected user
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
            exception_message = ''
            for i in range(len(wrong_parameter)):
                exception_message += wrong_parameter[i]
                if i != len(wrong_parameter) - 1:
                    exception_message += ', '
            raise ParameterException(str(exception_message))

        # check token
        user = User.verify_auth_token(token)
        if user is None:
            raise UserUnidentifiedException

        snapshot = Snapshots.query.filter_by(id=id).first()

        if snapshot is None:
            raise SnapshotNotExistingException

        if snapshot.user_id != user.id:
            raise SnapshotNotExistingException

        # output
        return {
            "config": snapshot.config
        }


@ns.route('/delete')
@api.response(530, 'Request error')
@api.response(531, 'Missing parameter')
@api.response(537, 'Snapshot not existing')
@api.response(539, 'User Unidentified')
class DeleteSnapshot(Resource):
    @api.marshal_with(snapshot_delete_output)
    @api.expect(snapshot_delete_input)
    @celery.task(name='delete a snapshot')
    def delete(self):
        """
        The method called to delete a snapshot of the connected user
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
            exception_message = ''
            for i in range(len(wrong_parameter)):
                exception_message += wrong_parameter[i]
                if i != len(wrong_parameter) - 1:
                    exception_message += ', '
            raise ParameterException(str(exception_message))

        # check token
        user = User.verify_auth_token(token)
        if user is None:
            raise UserUnidentifiedException

        snapshot = Snapshots.query.filter_by(id=id).first()

        if snapshot is None:
            raise SnapshotNotExistingException

        if snapshot.user_id != user.id:
            raise SnapshotNotExistingException

        db.session.delete(snapshot)
        db.session.commit()

        # output
        return {
            "message": "The snapshot has been deleted"
        }


@ns.route('/update')
@api.response(530, 'Request error')
@api.response(531, 'Missing parameter')
@api.response(537, 'Snapshot not existing')
@api.response(539, 'User Unidentified')
class UpdateSnapshot(Resource):
    @api.marshal_with(snapshot_update_output)
    @api.expect(snapshot_update_input)
    @celery.task(name='update a celery')
    def post(self):
        """
        The method called to update a snapshot of the connected user
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
        try:
            config = api.payload['config']
        except:
            wrong_parameter.append('config')

        if len(wrong_parameter) > 0:
            exception_message = ''
            for i in range(len(wrong_parameter)):
                exception_message += wrong_parameter[i]
                if i != len(wrong_parameter) - 1:
                    exception_message += ', '
            raise ParameterException(str(exception_message))

        # check token
        user = User.verify_auth_token(token)
        if user is None:
            raise UserUnidentifiedException

        snapshot = Snapshots.query.filter_by(id=id).first()
        if snapshot is None:
            raise SnapshotNotExistingException

        if snapshot.user_id != user.id:
            raise SnapshotNotExistingException

        snapshot.config = config
        db.session.commit()

        # output
        return {
            "message": "The snapshot has been updated"
        }


@ns.route('/list')
@api.response(530, 'Request error')
@api.response(531, 'Missing parameter')
@api.response(539, 'User Unidentified')
class ListSnapshot(Resource):
    @api.marshal_with(snapshot_list_output)
    @api.expect(snapshot_list_input)
    @celery.task(name='list all snapshots of a user')
    def post(self):
        """
        The method called to list all snapshots of the connected user
        :return:
        """
        # Entries
        wrong_parameter = []
        try:
            token = api.payload['token']
        except:
            wrong_parameter.append('token')

        if len(wrong_parameter) > 0:
            exception_message = ''
            for i in range(len(wrong_parameter)):
                exception_message += wrong_parameter[i]
                if i != len(wrong_parameter) - 1:
                    exception_message += ', '
            raise ParameterException(str(exception_message))

        # check token
        user = User.verify_auth_token(token)
        if user is None:
            raise UserUnidentifiedException

        snapshots = Snapshots.query.filter_by(user_id=user.id).all()

        # output
        return {
            "snapshots": snapshots
        }
