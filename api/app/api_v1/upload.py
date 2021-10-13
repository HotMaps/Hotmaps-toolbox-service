import os
import shutil
import uuid
from binascii import unhexlify
from io import BytesIO

import shapely.geometry as shapely_geom
from app import celery
from app.constants import USER_UPLOAD_FOLDER, UPLOAD_BASE_NAME, UPLOAD_DIRECTORY, NUTS_YEAR, LAU_YEAR
from flask import send_file
from flask_restx import Resource

from .. import dbGIS as db
from ..decorators.parsers import file_upload
from ..decorators.restplus import UserUnidentifiedException, ParameterException, RequestException, \
    UserDoesntOwnUploadsException, UploadNotExistingException, \
    HugeRequestException, NotEnoughPointsException, UploadFileNotExistingException
from ..decorators.restplus import api
from ..decorators.serializers import upload_add_output, upload_list_input, upload_list_output, upload_delete_input, \
    upload_delete_output, upload_export_csv_nuts_input, upload_export_csv_hectare_input, \
    upload_export_raster_nuts_input, upload_export_raster_hectare_input, upload_download_input, \
    upload_export_cm_layer_input
from ..model import get_csv_from_nuts, get_csv_from_hectare
from ..models.uploads import Uploads, generate_tiles, allowed_file, generate_geojson, calculate_total_space
from ..models.user import User
from ..decorators.timeout import return_on_timeout_endpoint

nsUpload = api.namespace('upload', description='Operations related to file upload')
ns = nsUpload


@ns.route('/add')
@api.response(530, 'Request error')
@api.response(531, 'Missing parameter')
@api.response(539, 'User Unidentified')
@api.response(542, 'Not Enough Space')
class AddUploads(Resource):
    @return_on_timeout_endpoint()
    @api.marshal_with(upload_add_output)
    @api.expect(file_upload)
    @celery.task(name='upload add')
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
            name = args['name']
        except:
            wrong_parameter.append('name')
        try:
            shared = args['shared']
        except:
            wrong_parameter.append('shared')
        try:
            layer_type = args['layer_type']
        except:
            wrong_parameter.append('layer_type')
        try:
            file_name = args['file'].filename
        except:
            wrong_parameter.append('file')
        try:
            layer = args['layer']
        except:
            if file_name.endswith('.tif'):
                wrong_parameter.append('layer')

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

        # Isolate the mail domain from the email of the connected user
        tmp = user.email
        user.emailServer = tmp.split("@")[1]

        # Set up the path
        user_folder = USER_UPLOAD_FOLDER + str(user.id)
        upload_uuid = str(uuid.uuid4())
        upload_folder = user_folder + '/' + upload_uuid

        # if the user does not own a repository, we create one
        if not os.path.isdir(user_folder):
            os.makedirs(user_folder)

        # we check if the file extension is valid
        if not allowed_file(file_name):
            raise RequestException("Please select a tif or csv file !")

        user_currently_used_space = calculate_total_space(user.uploads)

        if file_name.endswith('.tif'):
            url = upload_folder + '/' + UPLOAD_BASE_NAME
        else:
            url = upload_folder + '/data.csv'

        upload = Uploads(name=name, url=url, layer=layer, layer_type=layer_type, shared=shared, size=0.0, user_id=user.id,
                         uuid=upload_uuid, is_generated=1, mail_domain=user.emailServer)
        db.session.add(upload)
        db.session.commit()

        os.makedirs(upload_folder)

        # save the file on the file_system
        args['file'].save(url)
        if file_name.endswith('.tif'):
            generate_tiles.delay(upload_folder, url, layer_type, upload_uuid, user_currently_used_space)
        else:
            generate_geojson.delay(upload_folder, layer_type, upload_uuid, user_currently_used_space)

        # output
        output = 'file ' + name + ' added for the user ' + user.first_name
        return {
            "message": str(output)
        }


@ns.route('/tiles/<string:token>/<string:upload_id>/<int:z>/<int:x>/<int:y>')
@api.response(530, 'Request error')
@api.response(531, 'Missing parameter')
@api.response(539, 'User Unidentified')
@api.response(543, 'Uploads doesn\'t exists')
class TilesUploads(Resource):
    @return_on_timeout_endpoint()
    def get(self, token, upload_id, z, x, y):
        """
        The method called to get the tiles of an upload
        :return:
        """

        upload = Uploads.query.filter_by(id=upload_id).first()
        if upload is None:
            raise UploadNotExistingException

        if upload.shared == 'false':
            user = User.verify_auth_token(token)
            if user is None:
                raise UserUnidentifiedException
            if upload.user_id != user.id:
                raise UserDoesntOwnUploadsException
            folder_url = USER_UPLOAD_FOLDER + str(user.id) + '/' + str(upload.uuid)

        if upload.shared == 'true':
            folder_url = USER_UPLOAD_FOLDER + str(upload.user_id) + '/' + str(upload.uuid)

        tile_filename = folder_url+"/tiles/%d/%d/%d.png" % (z, x, y)

        if not os.path.exists(tile_filename):
            return
        # send the file to the client
        return send_file(tile_filename, mimetype='image/png')


@ns.route('/csv/<string:token>/<string:upload_id>')
@api.response(530, 'Request error')
@api.response(531, 'Missing parameter')
@api.response(539, 'User Unidentified')
@api.response(543, 'Uploads doesn\'t exists')
class ReadCsv(Resource):
    @return_on_timeout_endpoint()
    def get(self, token, upload_id):
        """
        The method called to get the csv of an upload
        :return:
        """

        upload = Uploads.query.filter_by(id=upload_id).first()
        if upload is None:
            raise UploadNotExistingException

        if upload.shared == 'false':
            user = User.verify_auth_token(token)
            if user is None:
                raise UserUnidentifiedException
            if upload.user_id != user.id:
                raise UserDoesntOwnUploadsException
            folder_url = USER_UPLOAD_FOLDER + str(user.id) + '/' + str(upload.uuid)

        if upload.shared == 'true':
            folder_url = USER_UPLOAD_FOLDER + str(upload.user_id) + '/' + str(upload.uuid)

        geoJSON = folder_url+"/data.json"

        if not os.path.exists(geoJSON):
            raise RequestException("No csv Existing")
        # send the file to the client
        return send_file(geoJSON, mimetype='application/json')


@ns.route('/list')
@api.response(530, 'Request error')
@api.response(531, 'Missing parameter')
@api.response(539, 'User Unidentified')
class ListUploads(Resource):
    @return_on_timeout_endpoint()
    @api.marshal_with(upload_list_output)
    @api.expect(upload_list_input)
    @celery.task(name='upload listing')
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

        uploads = self.get_uploads(token)

        # output
        return {
            "uploads": uploads
        }

    @staticmethod
    def get_uploads(token=None):
        # check token
        user = User.verify_auth_token(token)
        if user is None:
            raise UserUnidentifiedException

        # get the user uploads
        return user.uploads


@ns.route('/listshare')
@api.response(530, 'Request error')
@api.response(531, 'Missing parameter')
@api.response(539, 'User Unidentified')
class ListShare(Resource):
    @return_on_timeout_endpoint()
    @api.marshal_with(upload_list_output)
    @api.expect(upload_list_input)
    @celery.task(name='share listing')
    def post(self):
        """
        The method called to list the uploads shared
        :return:
        """
        # Entries
        try:
            token = api.payload['token']
        except:
            raise ParameterException('token')

        uploads = self.get_uploads(token)

        # output
        return {
            "uploads": uploads
        }

    @staticmethod
    def get_uploads(token=None):
        # check token
        user = User.verify_auth_token(token)
        if user is None:
            raise UserUnidentifiedException

        # Isolate the mail domain from the email of the connected user
        tmp = user.email
        user.emailServer = tmp.split("@")[1]

        # get the shared uploads from the same company (mail domain)
        return Uploads.query.filter_by(shared='true', mail_domain=user.emailServer).all()


@ns.route('/delete')
@api.response(530, 'Request error')
@api.response(531, 'Missing parameter')
@api.response(539, 'User Unidentified')
@api.response(541, 'Upload File doesn\'t exists')
@api.response(543, 'Uploads doesn\'t exists')
class DeleteUploads(Resource):
    @return_on_timeout_endpoint()
    @api.marshal_with(upload_delete_output)
    @api.expect(upload_delete_input)
    @celery.task(name='upload deletion')
    def delete(self):
        """
        The method called to delete an upload
        :return:
        """
        # Entries
        wrong_parameter = []
        try:
            id = api.payload['id']
        except:
            wrong_parameter.append('id')
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
        upload_to_delete = Uploads.query.filter_by(id=id).first()
        if upload_to_delete is None:
            raise UploadNotExistingException

        # check if the user can delete the
        if upload_to_delete.user_id != user.id:
            raise UserDoesntOwnUploadsException

        folder_url = USER_UPLOAD_FOLDER + str(user.id) + '/' + str(upload_to_delete.uuid)

        if os.path.exists(folder_url):
            # delete the file
            shutil.rmtree(folder_url)
        # Force DB deletion
        elif not ("force" in api.payload and api.payload["force"]):
            raise UploadFileNotExistingException("blah")

        # delete the upload
        db.session.delete(upload_to_delete)
        db.session.commit()

        # output
        return {
            "message": "Upload deleted"
        }


@ns.route('/export/cmLayer')
@api.response(530, 'Request error')
@api.response(531, 'Missing Parameters')
@api.response(541, 'Upload File doesn\'t exists')
class ExportCMLayer(Resource):
    @return_on_timeout_endpoint()
    @api.expect(upload_export_cm_layer_input)
    @celery.task(name='upload export cm layer')
    def post(self=None):
        """
        The method called to export cm layer
        :return:
        """
        wrong_parameter = []
        try:
            uuid = api.payload['uuid']
        except:
            wrong_parameter.append('uuid')
        try:
            type = api.payload['type']
        except:
            wrong_parameter.append('type')

        if len(wrong_parameter) > 0:
            exception_message = ', '.join(wrong_parameter)
            raise ParameterException(str(exception_message))

        if type == 'vector':
            path_to_file = UPLOAD_DIRECTORY + '/' + uuid
            mimetype = 'application/zip'
        else:
            file_type = '.tif'
            mimetype = 'image/TIF'
            path_to_file = UPLOAD_DIRECTORY + '/' + uuid + file_type

        if not os.path.exists(path_to_file):
            raise UploadFileNotExistingException(uuid)

        # send the file to the client
        return send_file(path_to_file,
                         mimetype=mimetype)


@ns.route('/export/raster/nuts')
@api.response(530, 'Request error')
@api.response(531, 'Missing Parameters')
@api.response(532, 'Request too big')
class ExportRasterNuts(Resource):
    @return_on_timeout_endpoint()
    @api.expect(upload_export_raster_nuts_input)
    @celery.task(name='upload export raster nuts')
    def post(self=None):
        """
        The method called to export a list of given nuts into a raster
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

        schema = "geo"
        dateCol = "year"

        if str(layers).endswith('lau2'):
            layer_type = 'lau'
            layer_name = layers[: -5]
            id_type = 'comm_id'
            layer_date = LAU_YEAR
            schema = "public"
            dateCol = "date"
        else:
            layer_type = 'nuts'
            layer_name = str(layers)[: -6]
            id_type = 'nuts_id'
            layer_date = NUTS_YEAR
            if not str(layers).endswith('nuts3'):
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

        # We add the first nuts/lau id
        sql += " FROM " + schema + "." + layer_type + " WHERE " + id_type + " = '" + nuts[0] + "'"
        # we add the rest of the nuts/lau id
        for nut in nuts[1:]:
            sql += " OR " + id_type + " = '" + nut + "'"

        # TODO Postpone Manage also the date field
        sql += """AND {2} = '{0}-01-01'), 3035 ), 0) AS buffer_geom) SELECT encode(ST_AsTIFF(foo.rast, 'LZW'), 'hex') as tif FROM (SELECT ST_Union(ST_Clip(rast, 1, buffer_geom, TRUE)) as rast FROM (SELECT ST_Union(rast) as rast, ST_Union(buffer_geom) as buffer_geom FROM geo.{1}, buffer WHERE ST_Intersects(rast, buffer_geom)) as rast WHERE ST_Intersects(rast, buffer_geom)) AS foo;""".format(layer_date, layer_name, dateCol)

        hex_file = ''

        # execute request
        try:
            result = db.engine.execute(sql)
        except:
            raise RequestException("Problem with your SQL query")
        try:
            # write hex_file
            for row in result:
                hex_file += row['tif']
        except Exception as e:
            raise RequestException("There is no result for this selection")

        # decode hex_file

        hex_file_decoded = unhexlify(hex_file)

        # write string buffer
        bt_io = BytesIO()
        bt_io.write(hex_file_decoded)
        bt_io.seek(0)

        # send the file to the client
        return send_file(bt_io,
                         mimetype='image/TIF',
                         attachment_filename="hotmaps.tif",
                         as_attachment=True)


@ns.route('/export/raster/hectare')
@api.response(530, 'Request error')
@api.response(531, 'Missing Parameters')
@api.response(532, 'Request too big')
class ExportRasterHectare(Resource):
    @return_on_timeout_endpoint()
    @api.expect(upload_export_raster_hectare_input)
    @celery.task(name='upload export raster hectare')
    def post(self=None):
        """
        The method called to export a list of given hectares into a raster
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

        # TODO Postpone Manage also the date field
        sql = """WITH buffer AS ( SELECT ST_Buffer( ST_Transform( ST_GeomFromText('{0}', 4258) , 3035), 0) AS buffer_geom) SELECT encode(ST_AsTIFF(foo.rast, 'LZW'), 'hex') as tif FROM ( SELECT ST_Union(ST_Clip(rast, 1, buffer_geom, TRUE)) as rast FROM ( SELECT ST_Union(rast) as rast, ST_Union(buffer_geom) as buffer_geom FROM geo.{1}, buffer WHERE ST_Intersects(rast, buffer_geom)) AS raster) AS foo;""".format(str(multipolygon), layer_name)


        hex_file = ''
        # execute request
        try:
            result = db.engine.execute(sql)
        except Exception:
            raise RequestException("Problem with your SQL query")

        rowcount = 0
        # write hex_file
        for row in result:
            rowcount += 1
            hex_file += row['tif']

        # if the result is empty, we raise an error
        if rowcount is 0:
            raise RequestException('There is no result for this selection')

        # decode hex_file

        hex_file_decoded = unhexlify(hex_file)

        # write string buffer
        #str_io = StringIO.StringIO() patch py3
        bt_io = BytesIO()
        bt_io.write(hex_file_decoded)
        bt_io.seek(0)

        # send the file to the client
        return send_file(bt_io,
                         mimetype='image/TIF',
                         attachment_filename="hotmaps.tif",
                         as_attachment=True)


@ns.route('/export/csv/nuts')
@api.response(530, 'Request error')
@api.response(531, 'Missing Parameters')
@api.response(532, 'Request too big')
class ExportCsvNuts(Resource):
    @return_on_timeout_endpoint()
    @api.expect(upload_export_csv_nuts_input)
    @celery.task(name='upload export csv nuts')
    def post(self=None):
        """
        The method called to export a given list of nuts into a csv
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
        try:
            schema = api.payload['schema']
        except:
            schema = 'geo'

        # raise exception if parameters are false
        if len(wrong_parameter) > 0:
            exception_message = ''
            for i in range(len(wrong_parameter)):
                exception_message += wrong_parameter[i]
                if i != len(wrong_parameter) - 1:
                    exception_message += ', '
            raise ParameterException(str(exception_message))
        csv_result = get_csv_from_nuts(layers=layers, nuts=nuts, schema=schema, year=year)

        # send the file to the client
        return send_file(csv_result,
                         mimetype='text/csv',
                         attachment_filename="hotmaps.csv",
                         as_attachment=True)


@ns.route('/export/csv/hectare')
@api.response(530, 'Request error')
@api.response(531, 'Missing Parameters')
@api.response(532, 'Request too big')
class ExportCsvHectare(Resource):
    @return_on_timeout_endpoint()
    @api.expect(upload_export_csv_hectare_input)
    @celery.task(name='upload export csv hectare')
    def post(self=None):
        """
        The method called to export a given list of hectares into a csv
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
            schema = api.payload['schema']
        except:
            schema = 'geo'
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

        csv_result = get_csv_from_hectare(areas=areas, layers=layers, schema=schema, year=year)

        # send the file to the client
        return send_file(csv_result,
                         mimetype='text/csv',
                         attachment_filename="hotmaps.csv",
                         as_attachment=True)


@ns.route('/download')
@api.response(530, 'Request error')
@api.response(531, 'Missing Parameters')
@api.response(539, 'User Unidentified')
@api.response(540, 'User doesn\'t own the upload')
@api.response(541, 'Upload File doesn\'t exists')
@api.response(543, 'Uploads doesn\'t exists')
class Download(Resource):
    @return_on_timeout_endpoint()
    @api.expect(upload_download_input)
    @celery.task(name='upload download')
    def post(self=None):
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

        # find upload
        upload = Uploads.query.filter_by(id=id).first()
        if upload is None:
            raise UploadNotExistingException

        # check if the user own the upload
        if upload.user_id != user.id:
            raise UserDoesntOwnUploadsException

        url = USER_UPLOAD_FOLDER + str(user.id) + '/' + str(upload.uuid)

        if os.path.exists(url + '/' + UPLOAD_BASE_NAME):
            url += '/'+UPLOAD_BASE_NAME
            extension = '.tif'
            mimetype = 'image/TIFF'
        elif os.path.exists(url + '/data.csv'):
            url += '/data.csv'
            extension = '.csv'
            mimetype = 'text/csv'
        else:
            raise UploadFileNotExistingException

        # send the file to the client
        return send_file(url,
                         mimetype=mimetype,
                         attachment_filename=upload.name + extension,
                         as_attachment=True)


