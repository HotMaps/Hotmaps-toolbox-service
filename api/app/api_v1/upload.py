from .. import constants
from ..decorators.restplus import api
from ..decorators.restplus import UserUnidentifiedException, ParameterException, RequestException, \
    UserDoesntOwnUploadsException, UploadExistingUrlException, NotEnoughSpaceException, UploadNotExistingException
from ..decorators.serializers import upload_add_input, upload_add_output, upload_list_input, upload_list_output,\
    upload_space_used_input, upload_space_used_output, upload_delete_input, upload_delete_output

from flask_restplus import Resource

from .. import dbGIS as db
from ..models.uploads import Uploads
from ..models.user import User
nsUpload = api.namespace('upload', description='Operations related to file upload')
ns = nsUpload


@ns.route('/add')
@api.response(530, 'Request error')
@api.response(531, 'Missing parameter')
@api.response(537, 'User Unidentified')
@api.response(541, 'Upload URL existing')
@api.response(542, 'Not Enough Space')
class AddUploads(Resource):
    @api.marshal_with(upload_add_output)
    @api.expect(upload_add_input)
    def post(self):
        """
        The method called to add an upload
        :return:
        """
        # Entries
        wrong_parameter = []
        try:
            file_name = api.payload['file_name']
        except:
            wrong_parameter.append('file_name')
        try:
            url = api.payload['url']
        except:
            wrong_parameter.append('url')
        try:
            size = api.payload['size']
        except:
            wrong_parameter.append('size')
        try:
            token = api.payload['token']
        except:
            wrong_parameter.append('token')
        # raise exception if parameters are false
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

        # we need to check if the URL is already taken
        if Uploads.query.filter_by(url=url).first() is not None:
            raise UploadExistingUrlException

        # we need to check if there is enough disk space for the dataset
        used_size = calculate_total_space(user.uploads) + size
        if used_size > constants.USER_DISC_SPACE_AVAILABLE:
            raise NotEnoughSpaceException

        # add the upload on the db
        upload = Uploads(file_name=file_name, url=url, size=size, user_id=user.id)
        db.session.add(upload)
        db.session.commit()
        # output
        output = 'file '+file_name+' added for the user '+user.first_name
        return {
            "message": output
        }


@ns.route('/list')
@api.response(530, 'Request error')
@api.response(531, 'Missing parameter')
@api.response(537, 'User Unidentified')
class ListUploads(Resource):
    @api.marshal_with(upload_list_output)
    @api.expect(upload_list_input)
    def post(self):
        """
        The method called to list the uploads of the connected user
        :return:
        """
        # Entries
        try:
            token = api.payload['token']
        except:
            raise ParameterException('token')

        # check token
        user = User.verify_auth_token(token)
        if user is None:
            raise UserUnidentifiedException

        # get the user uploads
        uploads = user.uploads

        try:
            return {
                "uploads": uploads
            }
        except Exception, e:
            raise RequestException(str(e))
        # output


@ns.route('/space_used')
@api.response(530, 'Request error')
@api.response(531, 'Missing parameter')
@api.response(537, 'User Unidentified')
class SpaceUsedUploads(Resource):
    @api.marshal_with(upload_space_used_output)
    @api.expect(upload_space_used_input)
    def post(self):
        """
        The method called to see the space used by an user
        :return:
        """
        # Entries
        try:
            token = api.payload['token']
        except:
            raise ParameterException('token')

        # check token
        user = User.verify_auth_token(token)
        if user is None:
            raise UserUnidentifiedException

        # get the user uploads
        uploads = user.uploads
        used_size = calculate_total_space(uploads)

        # output
        return {
            "used_size": used_size,
            "max_size": constants.USER_DISC_SPACE_AVAILABLE
        }


@ns.route('/remove_upload')
@api.response(530, 'Request error')
@api.response(531, 'Missing parameter')
@api.response(537, 'User Unidentified')
@api.response(540, 'User doesn\'t own the upload')
@api.response(543, 'Uploads doesn\'t exists')
class DeleteUploads(Resource):
    @api.marshal_with(upload_delete_output)
    @api.expect(upload_delete_input)
    def delete(self):
        """
        The method called to remove an upload
        :return:
        """
        # Entries
        wrong_parameter = []
        try:
            url = api.payload['url']
        except:
            wrong_parameter.append('url')
        try:
            token = api.payload['token']
        except:
            wrong_parameter.append('token')
        # raise exception if parameters are false
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

        # find upload to delete
        upload_to_delete = Uploads.query.filter_by(url=url).first()
        if upload_to_delete is None:
            raise UploadNotExistingException

        # check if the user can delete the
        if upload_to_delete.user_id != user.id:
            raise UserDoesntOwnUploadsException

        # delete the upload
        db.session.delete(upload_to_delete)
        db.session.commit()
        # output
        return {
            "message": "Upload removed"
        }


def calculate_total_space(uploads):
    '''
    This method will calculate the amount of disc space taken by a list of uploads
    :param uploads:
    :return: the used disk space
    '''
    used_size = 0

    # sum of every size
    for upload in uploads:
        used_size += upload.size

    return used_size
