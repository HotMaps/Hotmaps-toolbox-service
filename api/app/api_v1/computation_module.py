from celery.task.control import revoke

import signal
from flask import request, current_app,jsonify,redirect, \
    url_for,Response
from app.decorators.restplus import api
from app.decorators.serializers import compution_module_class, \
    input_computation_module, test_communication_cm, \
    compution_module_list, uploadfile, cm_id_input

from app.model import register_calulation_module,getUI,getCMList
from ..helper import commands_in_array, run_command

from ..models.user import User
from app import model

from app import helper
nsCM = api.namespace('cm', description='Operations related to statistisdscs')

ns = nsCM
from flask_restplus import Resource
from app import celery
import requests

from app.decorators.exceptions import ValidationError, ComputationalModuleError

import os
import json
from flask import send_from_directory, send_file
from app.constants import UPLOAD_DIRECTORY, DATASET_DIRECTORY

from app import CalculationModuleRpcClient
from ..decorators.timeout import timeout_signal_handler
from ..constants import DEFAULT_TIMEOUT


#TODO Add url to find  right computation module

try:
    args = commands_in_array('chmod +x app/helper/gdal2tiles-multiprocess.py')
    run_command(args)
except WindowsError:
    pass
#os.system(com_string)

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)
    os.chmod(UPLOAD_DIRECTORY, 0o644)

if not os.path.exists(DATASET_DIRECTORY):
    os.makedirs(DATASET_DIRECTORY)
    os.chmod(DATASET_DIRECTORY, 0o777)


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
        cm_id = input['cm_id']
        return getUI(cm_id)

@ns.route('/register/', methods=['POST'])
class ComputationModuleClass(Resource):
    def post(self):
        """
       Register a calculation module
       :return:
       """
        #print ('HTAPI will register cm')
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



        tile_filename = UPLOAD_DIRECTORY +'/'+directory+'/%d/%d/%d.png' % (z,x,y)
        if not os.path.exists(tile_filename):
            if not os.path.exists(os.path.dirname(tile_filename)):
                os.makedirs(os.path.dirname(tile_filename))
        try:
            return send_file(tile_filename, mimetype='image/png')
            #return Response(open(tile_filename).read())
        except:
            return None

def registerCM(input):
    register_calulation_module(input)
    return input

def savefile(filename,url):
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        path = os.path.join(UPLOAD_DIRECTORY, filename)
        with open(path, 'wb') as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)
    return path

@celery.task(name = 'Compute-async')
def computeTask(data, payload, cm_id):

    """
    :param data:
    :param payload:
    :param cm_id:
    :return:Rdeturns the calculation of a calculation module
    """
    signal.signal(signal.SIGALRM, timeout_signal_handler)
    signal.alarm(DEFAULT_TIMEOUT)
    try:

        #****************** RETRIVE INPUT DATA ***************************************************'
        #transforme stringify array to json
        layer_needed = [l for l in payload['layers_needed'] if l['data_type']=='raster']
        type_layer_needed = payload['type_layer_needed']
        vectors_needed = [l for l in payload['layers_needed'] if l['data_type']=='vector']
        #retriving scale level 3 possiblity hectare,nuts, lau
        scalevalue = data['scalevalue']
        nuts_within = None
        inputs_vector_selection = None
        areas = payload['areas']

        if scalevalue == 'hectare':
            #****************** BEGIN RASTER CLIP FOR HECTAR ***************************************************
            geom =  helper.area_to_geom(areas)

            nuts_within = model.nuts_within_the_selection(geom)

            inputs_raster_selection = model.get_raster_from_csv(geom, layer_needed, UPLOAD_DIRECTORY)
            inputs_vector_selection = model.retrieve_vector_data_for_calculation_module(vectors_needed, scalevalue, areas)
            #nut2_nuts3_area =
            #print ('inputs_raster_selection',inputs_raster_selection)
            #****************** FINISH RASTER CLIP FOR HECTAR ***************************************************'
        else:
            #****************** BEGIN RASTER CLIP FOR NUTS OR LAU ***************************************************'
            scale = scalevalue[:-1]
            # id_list = payload['areas']
            nuts_within = model.nuts2_within_the_selection_nuts_lau(scale,areas)
            shapefile_path = model.get_shapefile_from_selection(scale, areas, UPLOAD_DIRECTORY)
            inputs_raster_selection = model.clip_raster_from_shapefile(shapefile_path, layer_needed, UPLOAD_DIRECTORY)
            if vectors_needed != None:
                inputs_vector_selection = model.retrieve_vector_data_for_calculation_module(vectors_needed, scalevalue, areas)
            #****************** FINISH RASTER CLIP FOR NUTS  OR LAU ***************************************************
        print(inputs_raster_selection, inputs_vector_selection)
        data = generate_payload_for_compute(data,inputs_raster_selection,inputs_vector_selection,nuts_within)

        # send the result to the right CM
        #****************** WILL SEND PAYLOAD TO CM WITH ID {} ***************************************************'.format(cm_id))
        calculation_module_rpc = CalculationModuleRpcClient()
        response = calculation_module_rpc.call(cm_id,data.encode('utf-8'))
        response = response.decode('utf-8')

        data_output = json.loads(response)
        #'****************** RETRIVED RESULT FROM CM WITH ID {} ***************************************************'.format(cm_id))

        helper.test_display(data_output)
        #****************** WILL GENERATE TILES ***************************************************'.format(cm_id))
        try:

            for indicator in data_output['result']['indicator'] :
                indicator['value'] = str(indicator['value'])
        except:
            pass

        try:

            if data_output['result']['raster_layers'] is not None and len(data_output['result']['raster_layers'])>0:
                raster_layers = data_output['result']['raster_layers']
                generateTiles(raster_layers)
        except:
            # no raster_layers
            pass
        try:
            if data_output['result']['vector_layers'] is not None and len(data_output['result']['vector_layers'])>0:
                vector_layers = data_output['result']['vector_layers']
        except:
            # no vector_layers
            pass

        return data_output
    except TimeoutError:
        return None

def generateTiles(raster_layers):


    for layers in raster_layers:

        layer_type = layers['type']
        file_path_input = layers['path']
        directory_for_tiles = file_path_input.replace('.tif', '')
        file_path_output = helper.generate_geotif_name(UPLOAD_DIRECTORY)
        tile_path = directory_for_tiles
        access_rights = 0o755
        try:
            os.mkdir(tile_path, access_rights)


        except OSError:
            pass
            print ('Creation of the directory %s failed' % tile_path)
        else:
            pass

        if layer_type == 'custom':
            #convert tif file into geotif file
            args_gdal = commands_in_array('gdal_translate -of GTiff -expand rgba {} {} -co COMPRESS=DEFLATE '.format(file_path_input, file_path_output))
            run_command(args_gdal)
        else:
            helper.colorize(layer_type, file_path_input, file_path_output)

        args_tiles = commands_in_array("python3 app/helper/gdal2tiles.py -p 'mercator' -s 'EPSG:3035' -w 'leaflet' -r 'average' -z '4-11' {} {} ".format(file_path_output, tile_path))
        run_command(args_tiles)

        directory_for_tiles = directory_for_tiles.replace(UPLOAD_DIRECTORY+'/', '')
        layers['path'] = directory_for_tiles



    return file_path_input, directory_for_tiles

def generate_shape(vector_layers):
    for layers in vector_layers:
        file_path_input = layers['path']
    return file_path_input, file_path_input

def generate_payload_for_compute(data,inputs_raster_selection,inputs_vector_selection,nuts):
    inputs = data['inputs']
    inputs_parameter_selection = {}
    data_output = {}
    for parameters in inputs:
        inputs_parameter_selection.update({
         parameters['input_parameter_name']: parameters['input_value']
        })
    data_output.update({
        'nuts':nuts,
        'inputs_parameter_selection':inputs_parameter_selection,
        'inputs_raster_selection':inputs_raster_selection,
        'inputs_vector_selection':inputs_vector_selection
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
        payload = api.payload['payload']
        cm_id = data['cm_id']
        #2 inputs layers from the CM
        with app.app_context():
            task = computeTask.delay(data,payload,cm_id)
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
        return revoke(task_id, terminate=True)
