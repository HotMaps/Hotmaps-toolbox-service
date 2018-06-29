
from flask import request, current_app,jsonify
from app.decorators.restplus import api
from app.decorators.serializers import  compution_module_class, \
    input_computation_module, test_communication_cm, \
    compution_module_list, uploadfile
from app.decorators.exceptions import ValidationError
from app.model import register_calulation_module,getCMUrl, RasterManager
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

#TODO Add url to find  right computation module
UPLOAD_DIRECTORY = '/media/lesly/Data/project/api_uploaded_files'

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)






@ns.route('/user-interface/')
class ComputationModuleList(Resource):
    #@api.marshal_with(stats_layers_nuts_output)
    @api.marshal_with(compution_module_list)
    def post(self):
        """
        Returns the statistics for specific layers, area and year
        :return:
        """
        return {
            "list": ''}



@ns.route('/register/', methods=['POST'])
class ComputationModuleClass(Resource):
    # @api.expect(input_computation_module)
    #@api.expect(compution_module_class)
    def post(self):
        input = request.get_json()
        registerCM.delay(input)



@ns.route('/files/<string:filename>', methods=['GET'])
class getRasterfile(Resource):
    # @api.expect(input_computation_module)
    #@api.expect(compution_module_class)
    def get(self,filename):
        return send_from_directory(UPLOAD_DIRECTORY, filename, as_attachment=True)


@celery.task(name = 'registerCM')
def registerCM(input):
    print 'input', input
    register_calulation_module(input)

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
@ns.route('/compute/')
class ComputationModuleCompute(Resource):
   # @api.expect(input_computation_module)
    @api.expect(input_computation_module)
    def post(self):
        """
        Returns the statistics for specific layers, area and year
        :return:

        """
        data = request.get_json()
        cm_id = data["cm_id"]
    # 1. find the good computation module with the right url in the database from cm db  => generate url

        url_cm = celery_get_CM_url(cm_id)
        print url_cm
    #2. get parameters for clipping raster

        layersPayload = api.payload['layers']
        areas = api.payload['areas']
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
        base_url =  request.base_url.replace("compute","files")
        # 1.2.1  url for downloading raster
        url_download_raster = base_url + filename
        print url_download_raster
        # 1.2 build the parameters for the url

        # 2. if this is a raster clip of the raster or provide vector needed => generate link
        data = generate_payload_for_compute(data,url_download_raster,filename)
        print 'payload: ',data
        #res = requests.post(URL_CM + 'computation-module/compute/', data = api.payload)
        #print current_app.name
        app = current_app._get_current_object()
        with app.app_context():
             #app.app_context().push()
            res = computeCM.delay(url_cm, data)
            response = res.wait()

            print 'type response:',type(response)
            data= json.loads(response)
            tiff_url = data['tiff_url']
            file_path = savefile(filename,tiff_url)

            url_download_raster = base_url + filename
            print 'url_download_raster:',url_download_raster
            data['tiff_url'] = url_download_raster
            data['filename'] = filename
            print data
            print url_download_raster
            print 'tiff_url:',file_path
            return data


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





@celery.task(name = 'ComputeCM')
def computeCM(url_cm,data):
    headers = {'Content-Type':  'application/json'}
    print 'data ',data
    res = requests.post(str(url_cm)+'computation-module/compute/', data = data, headers=headers)
    reponse = res.text
    return reponse

