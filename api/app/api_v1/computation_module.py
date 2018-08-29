from celery.task.control import revoke
from flask import request, current_app,jsonify,redirect, \
    url_for,Response
from app.decorators.restplus import api
from app.decorators.serializers import  compution_module_class, \
    input_computation_module, test_communication_cm, \
    compution_module_list, uploadfile, cm_id_input
from app.decorators.exceptions import ValidationError
from app.model import register_calulation_module,getCMUrl, RasterManager,getUI,getCMList,getLayerNeeded
from werkzeug.utils import secure_filename
from app import constants
nsCM = api.namespace('cm', description='Operations related to statistisdscs')

ns = nsCM
from flask_restplus import Resource
from app import celery
import requests
import pika
import ast
import os
import json
from flask import send_from_directory
import shapely.geometry as shapely_geom
import socket
from app import CalculationModuleRpcClient
from app import helper

import logging

from celery import Celery
from celery.task import periodic_task
from datetime import timedelta
from os import environ

import stat
#TODO Add url to find  right computation module
UPLOAD_DIRECTORY = '/var/tmp'

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)
    os.chmod(UPLOAD_DIRECTORY, 0o644)






@ns.route('/list')
class ComputationModuleList(Resource):
    #@api.marshal_with(stats_layers_nuts_output)
    def post(self):
        """
        Returns the list of the available calculation module
        :return:
        """
        return getCMList()



@ns.route('/user-interface/', methods=['POST'])
@api.expect(cm_id_input)
class ComputationModuleClass(Resource):
    def post(self):
        """
       Returns the user interface of a specifique calculation module
       :return:
       """
        input = request.get_json()
        cm_id = input["cm_id"]
        return getUI(cm_id)


@ns.route('/register/', methods=['POST'])
class ComputationModuleClass(Resource):
    def post(self):
        """
       Register a calculation module
       :return:
       """
        print ('HTAPI will register cm')
        input = request.get_json()
        register_calulation_module(input)
        return json.dumps(input)



@ns.route('/files/<string:filename>', methods=['GET'])
class getRasterfile(Resource):
    def get(self,filename):
        """
         dowload a file from the main web service
         :return:
         """
        return send_from_directory(UPLOAD_DIRECTORY, filename, as_attachment=True)





@ns.route('/tiles/<string:directory>/<int:z>/<int:x>/<int:y>/', methods=['GET'])
class getRasterTile(Resource):
    def get(self,directory,z,x,y):

        """
         download a file from the main web service
         :return:
             """
        tile_filename = UPLOAD_DIRECTORY +'/'+directory+"/%d/%d/%d.png" % (z,x,y)
        if not os.path.exists(tile_filename):
            if not os.path.exists(os.path.dirname(tile_filename)):
                os.makedirs(os.path.dirname(tile_filename))

        return Response(open(tile_filename).read(), mimetype='image/png')

def retrieve_asyncronous_tiles(directory,z,x,y):


    """
     download a file from the main web service
     :return:
         """
    tile_filename = UPLOAD_DIRECTORY +'/'+directory+"/%d/%d/%d.png" % (z,x,y)
    if not os.path.exists(tile_filename):
        if not os.path.exists(os.path.dirname(tile_filename)):
            os.makedirs(os.path.dirname(tile_filename))

    return Response( open(tile_filename).read(), mimetype='image/png')



#@celery.task(name = 'registerCM')
def registerCM(input):
    register_calulation_module(input)
    return input



@celery.task(name = 'task-celery_get_CM_url')
def celery_get_CM_url(cm_id):
    return getCMUrl(cm_id)


    #return {}, 201, {'Location': cm.get_url()}

def transformGeo(geometry):
   return 'st_transform(st_geomfromtext(\''+ geometry +'\'::text,4326),' + str(constants.CRS) + ')'

def savefile(filename,url):
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        path = os.path.join(UPLOAD_DIRECTORY, filename)
        with open(path, 'wb') as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)
    return path

#@celery.task(bind=True)
@celery.task(name = 'Compute-async')
def computeTask(data,payload,base_url,cm_id,layerneed):

    """
    Returns the statistics for specific layers, area and year
    :return:

    """

    layer_needed = ast.literal_eval(layerneed)


    for layer in layer_needed:
        print(layer)


    print ("layerneed ",layer_needed)
    print ("layerneed ",type(layer_needed))
    #2. get parameters for clipping raster
    areas = payload['areas']
    if areas is not None:
        # we will be working on hectare level
        pass
    else:
        nuts = api.payload['nuts']
        # we will be working on a nuts
        pass
    #TODO add this part in an helper
    polyArray = []
    # convert to polygon format for each polygon and store them in polyArray
    for polygon in areas:
        po = shapely_geom.Polygon([[p['lng'], p['lat']] for p in polygon['points']])
        polyArray.append(po)
    # convert array of polygon into multipolygon
    multipolygon = shapely_geom.MultiPolygon(polyArray)
    #geom = "SRID=4326;{}".format(multipolygon.wkt)

    geom = multipolygon.wkt



    # Clip the raster from the database
    #filename = RasterManager.getRasterID(layersPayload[0],transformGeo(geom),UPLOAD_DIRECTORY)
    #for test
    #filename = str(uuid.uuid4()) + '.tif'


    filename = RasterManager.getRasterID('heat_tot_curr_density',transformGeo(geom),UPLOAD_DIRECTORY)
    #savefile(filename,"http://geoserver.hotmaps.hevs.ch/geoserver/hotmaps/wcs?SERVICE=WCS&VERSION=1.0.0 &REQUEST=GetCoverage&COVERAGE=hotmaps:heat_tot_curr_density_tif&CRS=EPSG:4326&RESPONSE_CRS=EPSG:3035&BBOX= http://geoserver.hotmaps.hevs.ch/geoserver/hotmaps/wcs?SERVICE=WCS&VERSION=1.0.0 &REQUEST=GetCoverage&COVERAGE=hotmaps:heat_tot_curr_density_tif&CRS=EPSG:4326&RESPONSE_CRS=EPSG:3035&BBOX=0.6365421639742981,47.50190979433006,0.6378718985257021,47.50280810960713&WIDTH=500&HEIGHT=500&FORMAT=GeoTIFF&WIDTH=500&HEIGHT=500&FORMAT=GeoTIFF")
    # 1.2.1  url for downloading raster
    url_download_raster = base_url + filename
    # 1.2 build the parameters for the url

    # 2. if this is a raster clip of the raster or provide vector needed => generate link
    data = generate_payload_for_compute(data,url_download_raster,filename)
    #res = requests.post(URL_CM + 'computation-module/compute/', data = api.payload)
    #print current_app.name

    #app.app_context().push()
    # send the result
    calculation_module_rpc = CalculationModuleRpcClient()
    response = calculation_module_rpc.call(cm_id,data)
    data_output = json.loads(response)

    tiff_url = data_output["tiff_url"]


    url_download_raster, file_path_input, directory_for_tiles = generateTiles(filename,tiff_url,base_url)

    data_output['tile_directory'] = base_url.replace('files', 'tiles') + directory_for_tiles
    ## use in the external of the network
    #data_output['tile_directory'] = 'http://api.hotmapsdev.hevs.ch/api/cm/tiles/' + directory_for_tiles
    data_output['filename'] = filename
    return data_output

def generateTiles(filename,tiff_url,base_url):
    file_path_input = savefile(filename,tiff_url)
    directory_for_tiles = filename.replace('.tif', '')
    intermediate_raster = helper.generate_geotif_name(UPLOAD_DIRECTORY)
    tile_path = UPLOAD_DIRECTORY+'/' + directory_for_tiles
    access_rights = 0o755

    try:
        os.mkdir(tile_path, access_rights)
    except OSError:
        print ("Creation of the directory %s failed" % tile_path)
    else:
        print ("Successfully created the directory %s" % tile_path)


    com_string = "gdal_translate -of GTiff -expand rgba {} {} && app/models/gdal2tiles.py --profile=mercator -z 0-13   {} {}".format(file_path_input,intermediate_raster,intermediate_raster,tile_path)
    #com_string = "python app/api_v1/gdal2tiles-multiprocess.py -l -p mercator -z 1-15 -w none  {} {}".format(file_path,tile_path)
    os.system(com_string)

    # gdal2tiles.generate_tiles(intermediate_raster, tile_path, np_processes=12, zoom='7-9')
    url_download_raster = base_url + filename
    return url_download_raster, file_path_input, directory_for_tiles


def generate_payload_for_compute(data,urls,filename):
    inputs = data["inputs"]
    data_output = {}
    for parameters in inputs:
        data_output.update({
            parameters['input_parameter_name']: parameters['input_value']
        })
    data_output.update({
       'url_file': urls,
       'filename':filename
    })
    data = json.dumps(data_output)
    return data



@ns.route('/compute-async/', methods=['POST'])
@api.expect(input_computation_module)
class ComputationModuleClass(Resource):
    def post(self):
        """
         retrieve a request from the from end
         :return:
         """
        app = current_app._get_current_object()
        data = request.get_json()
        payload = api.payload
        ip = socket.gethostbyname(socket.gethostname())
        base_url = 'http://'+ str(ip) +':'+str(constants.PORT)+'/api/cm/files/'
        cm_id = data["cm_id"]
         # 1. find the good computation module with the right url in the database from cm db  => generate url



        #2 inputs layers from the CM
        layerneed = getLayerNeeded(cm_id)
        with app.app_context():
            task = computeTask.delay(data,payload,base_url,cm_id,layerneed)
            return {'status_id': task.id}




@ns.route('/status/<string:task_id>', methods=['GET'])
class ComputationTaskStatus(Resource):
    def get(self,task_id):
        response = None
        task = computeTask.AsyncResult(task_id)

        if task.state == 'PENDING':
             response = {
                 'state': task.state,
                 'current': 0,
                 'total': 1,
                 'status': 'Pending...'
                     }
        elif task.state != 'FAILURE':
             response = {
                 'state': task.state,
                 'current': task.info.get('current', 0),
                 'total': task.info.get('total', 1),
                 'status': task.info
             }




             """import ipdb; ipdb.set_trace()
             if 'result' in task.info:
                response['result'] = task.info['result']
                print 'result',  task.info.get('status', '')"""

        else:
        # something went wrong in the background job
             response = {
                 'state': task.state,
                 'current': 1,
                 'total': 1,
                 'status': task.info,  # this is the exception raised
             }
        return response



@ns.route('/delete/<string:task_id>', methods=['DELETE'])
class DeleteTask(Resource):
    def delete(self,task_id):
    # get file stored in the api directory
        return revoke(task_id, terminate=True)

