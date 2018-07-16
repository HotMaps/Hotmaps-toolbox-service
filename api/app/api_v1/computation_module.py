
from flask import request, current_app,jsonify,redirect, \
    url_for
from app.decorators.restplus import api
from app.decorators.serializers import  compution_module_class, \
    input_computation_module, test_communication_cm, \
    compution_module_list, uploadfile, cm_id_input
from app.decorators.exceptions import ValidationError
from app.model import register_calulation_module,getCMUrl, RasterManager,getUI,getCMList
from werkzeug.utils import secure_filename
from app import constants
nsCM = api.namespace('cm', description='Operations related to statistisdscs')
ns = nsCM
from flask_restplus import Resource
from app import celery
import requests
import os
import json
from flask import send_from_directory
import shapely.geometry as shapely_geom
import socket
import stat

#TODO Add url to find  right computation module
UPLOAD_DIRECTORY = '/var/hotmaps/api_files_uploaded'

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)
    os.chmod(UPLOAD_DIRECTORY, 0777)



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
        input = request.get_json()
        registerCM.delay(input)
        print input
        return json.dumps(input)



@ns.route('/files/<string:filename>', methods=['GET'])
class getRasterfile(Resource):
    def get(self,filename):
        """
         dowload a file from the main web service
         :return:
         """
        return send_from_directory(UPLOAD_DIRECTORY, filename, as_attachment=True)


@celery.task(name = 'registerCM')
def registerCM(input):
    print 'input', input
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
def computeTask(data,payload,base_url):

    """
    Returns the statistics for specific layers, area and year
    :return:

    """
    #data = request.get_json()
    #app = current_app._get_current_object()
    #with app.app_context():

    print 'base url ', base_url
    cm_id = data["cm_id"]
    # 1. find the good computation module with the right url in the database from cm db  => generate url

    url_cm = celery_get_CM_url(cm_id)
    print url_cm
    #2. get parameters for clipping raster

    layersPayload = payload['layers']
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
    print 'geom ', geom
    # Clip the raster from the database
    filename = RasterManager.getRasterID(layersPayload[0],transformGeo(geom),UPLOAD_DIRECTORY)

    # 1.2.1  url for downloading raster
    url_download_raster = base_url + filename
    print url_download_raster
    # 1.2 build the parameters for the url

    # 2. if this is a raster clip of the raster or provide vector needed => generate link
    data = generate_payload_for_compute(data,url_download_raster,filename)
    print 'payload: ',data
    #res = requests.post(URL_CM + 'computation-module/compute/', data = api.payload)
    #print current_app.name

    #app.app_context().push()
    res = computeCM(url_cm, data)
    response = res

    print 'type response:',type(response)
    print ' response:',response
    data_output = json.loads(response)

    print ' data:',data_output
    tiff_url = data_output["tiff_url"]
    file_path = savefile(filename,tiff_url)
    print file_path
  #  com_string = "gdal_translate -of GTIFF -srcwin " + str(i)+ ", " + str(j) + ", " + str(tile_size_x) + ", " + str(tile_size_y) + " " + str(in_path) + str(input_filename) + " " + str(out_path) + str(output_filename) + str(i) + "_" + str(j) + ".tif"
   # os.system(com_string)

    url_download_raster = base_url + filename
    print 'url_download_raster:',url_download_raster
    data_output['tiff_url'] = url_download_raster
    data_output['filename'] = filename
    print data_output
    print url_download_raster
    print 'tiff_url:',file_path
    return data_output


def generate_payload_for_compute(data,url,filename):
    inputs = data["inputs"]
    data_output = {}
    for parameters in inputs:
        data_output.update({
            parameters['input_parameter_name']: parameters['input_value']
        })
    data_output.update({
       'url_file': url,
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
        print 'ip ', ip
        base_url = 'http://'+ str(ip) +':'+str(constants.PORT)+'/api/cm/files/'
        #print 'compute base url2 ', base_url_main
        #print 'base_url', base_url


        #print data

        with app.app_context():
            task = computeTask.delay(data,payload,base_url)
            return {'id': task.id}


#@celery.task(name = 'ComputeCM')
def computeCM(url_cm,data):
    headers = {'Content-Type':  'application/json'}
    print 'data ',data
    res = requests.post(str(url_cm)+'computation-module/compute/', data = data, headers=headers)
    reponse = res.text
    return reponse




@ns.route('/status/<string:task_id>', methods=['GET'])
class ComputationTaskStatus(Resource):
    def get(self,task_id):
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
                'status': task.info.get('status', '')
            }
        if 'result' in task.info:
            response['result'] = task.info['result']
        else:
        # something went wrong in the background job
            response = {
                'state': task.state,
                'current': 1,
                'total': 1,
                'status': str(task.info),  # this is the exception raised
            }
        return response


