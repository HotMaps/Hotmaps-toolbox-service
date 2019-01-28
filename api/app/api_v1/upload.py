import StringIO
import os
import shutil
import shapely.geometry as shapely_geom
import uuid
from flask_restplus import Resource
from binascii import unhexlify
from flask import send_file
from app import celery
from ..decorators.restplus import api
from ..decorators.restplus import UserUnidentifiedException, ParameterException, RequestException, \
    UserDoesntOwnUploadsException, UploadExistingUrlException, UploadNotExistingException, \
    HugeRequestException, NotEnoughPointsException
from ..decorators.serializers import upload_add_output, upload_list_input, upload_list_output,upload_delete_input, \
    upload_delete_output, upload_export_csv_nuts_input, upload_export_csv_hectare_input, \
    upload_export_raster_nuts_input, upload_export_raster_hectare_input, upload_download_input
from .. import dbGIS as db
from ..models.uploads import Uploads, generate_tiles, allowed_file, check_map_size, calculate_total_space
from ..models.user import User
from ..decorators.parsers import file_upload

nsUpload = api.namespace('upload', description='Operations related to file upload')
ns = nsUpload
NUTS_YEAR = "2013"
LAU_YEAR = NUTS_YEAR
USER_UPLOAD_FOLDER = '/var/hotmaps/users/'


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
            name = args['name']
        except:
            wrong_parameter.append('name')
        try:
            file_name = args['file'].filename
        except Exception, e:
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

        # Set up the path
        user_folder = USER_UPLOAD_FOLDER + str(user.id)
        upload_uuid = str(uuid.uuid4())
        upload_folder = user_folder + '/' + upload_uuid

        # if the user does not own a repository, we create one
        if not os.path.isdir(user_folder):
            os.makedirs(user_folder)

        # we need to check if the name is already taken for the user
        if Uploads.query.filter_by(name=name).first() is not None:
            raise UploadExistingUrlException

        # we check if the file extension is valid
        if not allowed_file(file_name):
            raise RequestException("Please select a tif or csv file !")

        user_currently_used_space = calculate_total_space(user.uploads)

        if file_name.endswith('.tif'):
            url = upload_folder + '/grey.tif'
        else:
            url = upload_folder + '/data.csv'

        upload = Uploads(name=name, url=url, size=-1, layer=layer, user_id=user.id, uuid=upload_uuid,
                         is_generated=10)
        db.session.add(upload)
        db.session.commit()

        os.makedirs(upload_folder)

        # save the file on the file_system
        args['file'].save(url)
        if file_name.endswith('.tif'):
            generate_tiles.delay(upload_folder, url, layer, upload_uuid, user_currently_used_space)
        else:
            check_map_size(upload_folder, user_currently_used_space, upload_uuid)

        # output
        output = 'file ' + name + ' added for the user ' + user.first_name
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

        # output
        return {
            "uploads": uploads
        }


@ns.route('/remove_upload')
@api.response(530, 'Request error')
@api.response(531, 'Missing parameter')
@api.response(539, 'User Unidentified')
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

        # delete the upload
        db.session.delete(upload_to_delete)
        db.session.commit()

        # delete the file
        shutil.rmtree(folder_url)

        # output
        return {
            "message": "Upload removed"
        }


@celery.task(name='generate_tiles_file_upload')
@ns.route('/export/raster/nuts')
@api.response(530, 'Request error')
@api.response(531, 'Missing Parameters')
@api.response(532, 'Request too big')
class ExportRasterNuts(Resource):
    @api.expect(upload_export_raster_nuts_input)
    def post(self):
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
        if str(layers).endswith('lau2'):
            layer_type = 'lau'
            layer_name = layers[: -5]
            id_type = 'comm_id'
            layer_date = LAU_YEAR
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
        sql += " FROM geo." + layer_type + " WHERE " + id_type + " = '" + nuts[0] + "'"
        # we add the rest of the nuts/lau id
        for nut in nuts[1:]:
            sql += " OR " + id_type + " = '" + nut + "'"
        sql += " AND year = '" + layer_date + "-01-01'"

        sql += "), 3035 ), 0) AS buffer_geom) " \
            "SELECT encode(ST_AsTIFF(foo.rast, 'LZW'), 'hex') as tif " \
            "FROM " \
                "(SELECT ST_Union(ST_Clip(rast, 1, buffer_geom, TRUE)) as rast " \
                "FROM geo." + layer_name + ", buffer " \
                "WHERE ST_Intersects(rast, buffer_geom)) AS foo;"  # TODO Manage also the date field
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
        except Exception, e:
            raise RequestException("There is no result for this selection")

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


@celery.task(name='generate_tiles_file_upload')
@ns.route('/export/raster/hectare')
@api.response(530, 'Request error')
@api.response(531, 'Missing Parameters')
@api.response(532, 'Request too big')
class ExportRasterHectare(Resource):
    @api.expect(upload_export_raster_hectare_input)
    def post(self):
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

        sql = "WITH buffer AS ( SELECT ST_Buffer( ST_Transform( ST_GeomFromText('"+str(multipolygon)+"', 4258) " \
                ", 3035), 0) AS buffer_geom) SELECT encode(ST_AsTIFF(foo.rast, 'LZW'), 'hex') as tif FROM " \
                "( SELECT ST_Union(ST_Clip(rast, 1, buffer_geom, TRUE)) as rast FROM geo." + layer_name + \
                ", buffer WHERE ST_Intersects(rast, buffer_geom)) AS foo;"  # TODO Manage also the date field

        hex_file = ''
        # execute request
        try:
            result = db.engine.execute(sql)
        except Exception:
            raise RequestException(result)

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


@celery.task(name='generate_tiles_file_upload')
@ns.route('/export/csv/nuts')
@api.response(530, 'Request error')
@api.response(531, 'Missing Parameters')
@api.response(532, 'Request too big')
class ExportCsvNuts(Resource):
    @api.expect(upload_export_csv_nuts_input)
    def post(self):
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

        # We must determine if it is a nuts or a lau
        if str(layers).endswith('lau2'):
            layer_type = 'lau'
            layer_name = layers[: -5]
            id_type = 'comm_id'
            layer_date = LAU_YEAR
        else:
            layer_type = 'nuts'
            layer_name = str(layers)[: -6]
            id_type = 'nuts_id'
            layer_date = NUTS_YEAR
            if not str(layers).endswith('nuts3'):
                raise HugeRequestException

        sql = "SELECT * FROM " + schema + "." + layer_name + " WHERE date = '" + year + "-01-01' AND ST_Within(" \
              + schema + "." + layer_name + ".geometry, st_transform((SELECT geom from geo." \
              + layer_type + " where " + id_type + " = '" + nuts[0] + "'"

        # we add the rest of the lau id
        for nut in nuts[1:]:
            sql += " OR " + id_type + " = '" + nut + "'"

        sql += " and year = '" + layer_date + "-01-01'), 3035))"

        # execute request
        try:
            result = db.engine.execute(sql)
        except Exception, e:
            raise RequestException(sql)

        # write csv_file
        number_of_columns = len(result._metadata.keys)
        csv_file = ''
        for header in result._metadata.keys[:-1]:
            csv_file += header + ', '

        csv_file += result._metadata.keys[number_of_columns - 1] + '\r\n'
        rowcount = 0
        for row in result:
            rowcount += 1
            for attribute in row[:-1]:
                    csv_file += str(attribute) + ', '
            csv_file += str(row[number_of_columns - 1]) + '\r\n'

        # if the result is empty, we raise an error
        if rowcount is 0:
            raise RequestException('There is no result for this selection')

        # write string buffer
        strIO = StringIO.StringIO()
        strIO.write(csv_file)
        strIO.seek(0)

        # send the file to the client
        return send_file(strIO,
                         mimetype='text/csv',
                         attachment_filename="testing.csv",
                         as_attachment=True)


@celery.task(name='generate_tiles_file_upload')
@ns.route('/export/csv/hectare')
@api.response(530, 'Request error')
@api.response(531, 'Missing Parameters')
@api.response(532, 'Request too big')
class ExportCsvHectare(Resource):
    @api.expect(upload_export_csv_hectare_input)
    def post(self):
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

        sql = "SELECT * FROM " + schema + "." + layer_name + " WHERE date = '" + year + "-01-01' AND ST_Within(" \
              + schema + "." + layer_name + ".geometry, st_transform(st_geomfromtext('" + str(multipolygon) \
              + "', 4258), 3035)) "

        # execute request
        try:
            result = db.engine.execute(sql)
        except Exception, e:
            raise RequestException(sql) #Failure in the SQL Request

        # write csv_file
        number_of_columns = len(result._metadata.keys)
        csv_file = ''
        for header in result._metadata.keys[:-1]:
            csv_file += header + ', '
        rowcount = 0
        csv_file += result._metadata.keys[number_of_columns - 1] + '\r\n'
        for row in result:
            rowcount += 1
            for attribute in row[:-1]:
                    csv_file += str(attribute) + ', '
            csv_file += str(row[number_of_columns - 1]) + '\r\n'

        # if the result is empty, we raise an error
        if rowcount is 0:
            raise RequestException('There is no result for this selection')

        # write string buffer>
        strIO = StringIO.StringIO()
        strIO.write(csv_file)
        strIO.seek(0)

        # send the file to the client
        return send_file(strIO,
                         mimetype='text/csv',
                         attachment_filename="testing.csv",
                         as_attachment=True)


@ns.route('/download')
@api.response(530, 'Request error')
@api.response(531, 'Missing Parameters')
@api.response(539, 'User Unidentified')
@api.response(540, 'User doesn\'t own the upload')
@api.response(543, 'Uploads doesn\'t exists')
class Download(Resource):
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

        url = USER_UPLOAD_FOLDER + str(user.id) + '/' + str(upload.uuid) + '/grey.tif'

        if url.endswith('.tif'):
            mimetype = 'image/TIFF'
        elif url.endswith('.csv'):
            mimetype = 'text/csv'

        # send the file to the client
        return send_file(url,
                         mimetype=mimetype,
                         attachment_filename=upload.name+'.tif',
                         as_attachment=True)


