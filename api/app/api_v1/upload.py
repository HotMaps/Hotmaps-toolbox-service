import StringIO
import os

from flask import send_file
from .. import constants
from ..decorators.restplus import api
from ..decorators.restplus import UserUnidentifiedException, ParameterException, RequestException, \
    UserDoesntOwnUploadsException, UploadExistingUrlException, NotEnoughSpaceException, UploadNotExistingException, \
    HugeRequestException, NotEnoughPointsException
from ..decorators.serializers import upload_add_output, upload_list_input, upload_list_output,upload_delete_input, \
    upload_delete_output, \
    upload_export_nuts_input, upload_export_hectare_input, upload_download_input
from flask_restplus import Resource
from binascii import unhexlify
from .. import dbGIS as db
from ..models.uploads import Uploads
from ..models.user import User
import shapely.geometry as shapely_geom

from ..decorators.parsers import file_upload

nsUpload = api.namespace('upload', description='Operations related to file upload')
ns = nsUpload
NUTS_YEAR = "2013"
LAU_YEAR = NUTS_YEAR
UPLOAD_FOLDER = '/temp/Hotmaps/users/'

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

@ns.route('/add')
@api.response(530, 'Request error')
@api.response(531, 'Missing parameter')
@api.response(539, 'User Unidentified')
@api.response(541, 'Upload URL existing')
@api.response(542, 'Not Enough Space')
class AddUploads(Resource):
    @api.marshal_with(upload_add_output)
    @api.expect(file_upload)
    def post(self):
        """
        The method called to add an upload
        :return:
        """
        args = file_upload.parse_args()
        # Entries
        wrong_parameter = []
        try:
            token = args['token']
        except:
            wrong_parameter.append('token')
        try:
            file_name = args['file_name']
        except:
            wrong_parameter.append('file_name')
        try:
            tif_file = '%s%s' % (UPLOAD_FOLDER, file_name + ".tif")
        except Exception, e :
            wrong_parameter.append('file')
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
        url = UPLOAD_FOLDER + file_name
        # we need to check if the URL is already taken
        if Uploads.query.filter_by(url=url).first() is not None:
            raise UploadExistingUrlException
        # save the file on the file_system
        args['tif_file'].save(tif_file)

        # we check the size of our file
        size = float(os.path.getsize(url+".tif")) / 1000000

        try:
            # we need to check if there is enough disk space for the dataset
            used_size = calculate_total_space(user.uploads) + size
        except Exception, e:
            raise RequestException(str(e))
        if used_size > constants.USER_DISC_SPACE_AVAILABLE:
            raise NotEnoughSpaceException

        # add the upload on the db
        upload = Uploads(file_name=file_name, url=url, size=size, user_id=user.id)
        db.session.add(upload)
        db.session.commit()

        # output
        output = 'file '+file_name+' added for the user '+user.first_name
        return {
            "message": str(output)
        }


@ns.route('/list')
@api.response(530, 'Request error')
@api.response(531, 'Missing parameter')
@api.response(539, 'User Unidentified')
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


@ns.route('/remove_upload')
@api.response(530, 'Request error')
@api.response(531, 'Missing parameter')
@api.response(539, 'User Unidentified')
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
            file_name = api.payload['file_name']
        except:
            file_name = wrong_parameter.append('file_name')
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
        url = UPLOAD_FOLDER + file_name

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

        #delete the file
        os.remove(url + ".tif")
        # output
        return {
            "message": "Upload removed"
        }


@ns.route('/export/nuts')
@api.response(530, 'Request error')
@api.response(531, 'Missing Parameters')
@api.response(532, 'Request too big')
class ExportNuts(Resource):
    @api.expect(upload_export_nuts_input)
    def post(self):
        """
        The method called to export a given nuts
        :return:
        """
        # Entries
        wrong_parameter = []
        try:
            year = api.payload['year']
        except:
            wrong_parameter.append('year')
        try:
            layers = api.payload['layers']
        except:
            wrong_parameter.append('layers')
        try:
            nuts = api.payload['nuts']
        except:
            wrong_parameter.append('nuts')
        # raise exception if parameters are false
        if len(wrong_parameter) > 0:
            exception_message = ''
            for i in range(len(wrong_parameter)):
                exception_message += wrong_parameter[i]
                if i != len(wrong_parameter) - 1:
                    exception_message += ', '
            raise ParameterException(str(exception_message))
        # We must determine if it is a nuts or a lau
        if str(layers).endswith('lau2'):
            layer_type = 'lau'
            layer_name = layers[: -5]
        else:
            layer_type = 'nuts'
            layer_name = str(layers)[: -6]
            if str(layers)[-1] != '3':
                raise HugeRequestException

        # format the layer_name to contain only the name
        if layer_name.endswith('_tif'):
            layer_name = layer_name[:-4]
        # build request
        sql = "WITH buffer " \
            "AS " \
                "( SELECT ST_Buffer(ST_transform(" \
                    "(SELECT "
        # If there is more than one area selected, we need to make a union of the geometries
        if len(nuts) > 1:
            sql += "ST_UNION(geom) as geom"
        else:
            sql += "geom"
        try:
            # if it is a lau, we need to check the lau table, otherwise the nuts table
            if layer_type == 'lau':
                # We add the first lau id
                sql += " FROM public.lau WHERE comm_id = '" + nuts[0] + "'"
                # we add the rest of the lau id
                for nut in nuts[1:]:
                    sql += " OR comm_id = '" + nut + "'"
                sql += " AND date = '" + LAU_YEAR + "-01-01'"

            else:
                # We add the first nuts id
                sql += " FROM geo.nuts WHERE nuts_id = '"+nuts[0]+"'"
                # we add the rest of the nuts id
                for nut in nuts[1:]:
                    sql += " OR nuts_id = '" + nut + "'"
                sql += " AND year = '" + NUTS_YEAR + "-01-01'"

            sql += "), 3035 ), 0) AS buffer_geom) " \
                "SELECT encode(ST_AsTIFF(foo.rast, 'LZW'), 'hex') as tif " \
                "FROM " \
                    "(SELECT ST_Union(ST_Clip(rast, 1, buffer_geom, TRUE)) as rast " \
                    "FROM geo." + layer_name + ", buffer " \
                    "WHERE ST_Intersects(rast, buffer_geom)) AS foo;"  # TODO Manage also the date field
            hex_file = ''

            # execute request
        #try:
            result = db.engine.execute(sql)
        except Exception, e:
            raise RequestException(str(e))

        try:
            # write hex_file
            for row in result:
                hex_file += row['tif']
        except Exception, e:
            raise RequestException("The result is empty, please check your data")

        # decode hex_file
        hex_file_decoded = unhexlify(hex_file)

        # write string buffer
        strIO = StringIO.StringIO()
        strIO.write(hex_file_decoded)
        strIO.seek(0)

        # send the file to the client
        return send_file(strIO,
                         mimetype='image/TIFF',
                         attachment_filename="testing.tif",
                         as_attachment=True)


@ns.route('/export/hectare')
@api.response(530, 'Request error')
@api.response(531, 'Missing Parameters')
@api.response(532, 'Request too big')
class ExportHectare(Resource):
    @api.expect(upload_export_hectare_input)
    def post(self):
        """
        The method called to export a given hectares
        :return:
        """
        # Entries
        wrong_parameter = []
        try:
            year = api.payload['year']
        except:
            wrong_parameter.append('year')
        try:
            layers = api.payload['layers']
        except:
            wrong_parameter.append('layers')
        try:
            areas = api.payload['areas']
            for test_area in areas:
                try:
                    for test_point in test_area['points']:
                        try:
                            test_lng = test_point['lng']
                        except:
                            wrong_parameter.append('lng')
                        try:
                            test_lat = test_point['lat']
                        except:
                            wrong_parameter.append('lat')
                except:
                    wrong_parameter.append('points')
        except:
            wrong_parameter.append('areas')
        # raise exception if parameters are false
        if len(wrong_parameter) > 0:
            exception_message = ''
            for i in range(len(wrong_parameter)):
                exception_message += wrong_parameter[i]
                if i != len(wrong_parameter) - 1:
                    exception_message += ', '
            raise ParameterException(str(exception_message))

        if not str(layers).endswith('_ha'):
            raise RequestException("this is not a correct layer for an hectare selection !")
        # format the layer_name to contain only the name
        layer_name = layers[:-3]
        # build request
        polyArray = []
        # convert to polygon format for each polygon and store them in polyArray
        try:
            for polygon in areas:
                po = shapely_geom.Polygon([[p['lng'], p['lat']] for p in polygon['points']])
                polyArray.append(po)
        except:
            raise NotEnoughPointsException

        # convert array of polygon into multipolygon
        multipolygon = shapely_geom.MultiPolygon(polyArray)

        sql = "WITH buffer AS ( SELECT ST_Buffer( ST_Transform( ST_GeomFromText('"+str(multipolygon)+"', 4258) " \
                ", 3035), 0) AS buffer_geom) SELECT encode(ST_AsTIFF(foo.rast, 'LZW'), 'hex') as tif FROM " \
                "( SELECT ST_Union(ST_Clip(rast, 1, buffer_geom, TRUE)) as rast FROM geo." + layer_name + \
                ", buffer WHERE ST_Intersects(rast, buffer_geom)) AS foo;"  # TODO Manage also the date field

        hex_file = ''
        # execute request
        try:
            result = db.engine.execute(sql)
        except Exception, e:
            raise RequestException("Failure in the SQL Request")

        # write hex_file
        for row in result:
            hex_file += row['tif']

        # decode hex_file
        hex_file_decoded = unhexlify(hex_file)

        # write string buffer
        strIO = StringIO.StringIO()
        strIO.write(hex_file_decoded)
        strIO.seek(0)

        try:
            # send the file to the client
            return send_file(strIO,
                             mimetype='image/TIFF',
                             attachment_filename="testing.tif",
                             as_attachment=True)
        except Exception, e:
            raise RequestException(str(e))


@ns.route('/download')
@api.response(530, 'Request error')
@api.response(531, 'Missing Parameters')
@api.response(539, 'User Unidentified')
@api.response(540, 'User doesn\'t own the upload')
@api.response(543, 'Uploads doesn\'t exists')
class ExportNuts(Resource):
    @api.expect(upload_download_input)
    def post(self):
        '''
        This method will allow the user to download a selected dataset
        :return:
        '''
        # Entries
        wrong_parameter = []
        try:
            token = api.payload['token']
        except:
            wrong_parameter.append('token')
        try:
            file_name = api.payload['file_name']
        except:
            wrong_parameter.append('file_name')

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

        url = UPLOAD_FOLDER + file_name

        # find upload to delete
        upload = Uploads.query.filter_by(url=url).first()
        if upload is None:
            raise UploadNotExistingException

        # check if the user can delete the
        if upload.user_id != user.id:
            raise UserDoesntOwnUploadsException

        # send the file to the client
        return send_file(url +".tif",
                         mimetype='image/TIFF',
                         attachment_filename="testing.tif",
                         as_attachment=True)

def calculate_total_space(uploads):
    '''
    This method will calculate the amount of disc space taken by a list of uploads
    :param uploads:
    :return: the used disk space
    '''
    used_size = float(0)

    # sum of every size
    for upload in uploads:
        used_size += float(upload.size)

    return used_size

def allowed_file(filename):
    '''
    This method will check if the file is allowed
    :param filename:
    :return:
    '''
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS