from .. import constants
from ..decorators.restplus import api
from ..decorators.restplus import UserUnidentifiedException, ParameterException, RequestException, \
    UserDoesntOwnUploadsException, UploadExistingUrlException, NotEnoughSpaceException, UploadNotExistingException
from ..decorators.serializers import upload_add_input, upload_add_output, upload_list_output, upload_space_used_output\
    , upload_delete_input, upload_delete_output

from flask_restplus import Resource
from flask_login import current_user

from .. import dbGIS as db
from ..models.uploads import Uploads

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
        # check if the user is connected
        if not current_user.is_authenticated:
            raise UserUnidentifiedException

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
        # raise exception if parameters are false
        if len(wrong_parameter) > 0:
            exception_message = ''
            for i in range(len(wrong_parameter)):
                exception_message += wrong_parameter[i]
                if i != len(wrong_parameter) - 1:
                    exception_message += ', '
            raise ParameterException(str(exception_message))

        # we need to check if the URL is already taken
        if Uploads.query.filter_by(url=url).first() is not None:
            raise UploadExistingUrlException

        # we need to check if there is enough disk space for the dataset
        used_size = calculate_total_space(current_user.uploads) + size
        if used_size > constants.USER_DISC_SPACE_AVAILABLE:
            raise NotEnoughSpaceException

        # add the upload on the db
        upload = Uploads(file_name=file_name, url=url, size=size, user_id=current_user.id)
        db.session.add(upload)
        db.session.commit()
        # output
        output = 'file '+file_name+' added for the user '+current_user.first_name
        return {
            "message": output
        }


@ns.route('/list')
@api.response(530, 'Request error')
@api.response(531, 'Missing parameter')
@api.response(537, 'User Unidentified')
class ListUploads(Resource):
    @api.marshal_with(upload_list_output)
    def get(self):
        """
        The method called to list the uploads of the connected user
        :return:
        """
        # check if the user is connected
        if not current_user.is_authenticated:
            raise UserUnidentifiedException

        # get the user uploads
        uploads = current_user.uploads

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
    def get(self):
        """
        The method called to see the space used by an user
        :return:
        """
        # check if the user is connected
        if not current_user.is_authenticated:
            raise UserUnidentifiedException

        # get the user uploads
        uploads = current_user.uploads
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
        # check if the user is connected
        if not current_user.is_authenticated:
            raise UserUnidentifiedException

        # Entries
        try:
            url = api.payload['url']
        except:
            raise ParameterException('url')

        # find upload to delete
        upload_to_delete = Uploads.query.filter_by(url=url).first()
        if upload_to_delete is None:
            raise UploadNotExistingException

        # check if the user can delete the
        if upload_to_delete.user_id != current_user.id:
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
