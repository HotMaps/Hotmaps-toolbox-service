from celery.task.control import revoke
from flask import request, current_app,jsonify,redirect, \
    url_for,Response
from app.decorators.restplus import api
from app.decorators.serializers import compution_module_class, \
    input_computation_module, test_communication_cm, \
    compution_module_list, uploadfile, cm_id_input

from app.model import register_calulation_module,getUI,getCMList,commands_in_array, run_command


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
from flask import send_from_directory


from app import CalculationModuleRpcClient



#TODO Add url to find  right computation module
UPLOAD_DIRECTORY = '/var/tmp'
DATASET_DIRECTORY = '/var/hotmaps/repositories/'

try:
    args = commands_in_array("chmod +x app/helper/gdal2tiles-multiprocess.py")
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
        cm_id = input["cm_id"]
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
        tile_filename = UPLOAD_DIRECTORY +'/'+directory+"/%d/%d/%d.png" % (z,x,y)
        if not os.path.exists(tile_filename):
            if not os.path.exists(os.path.dirname(tile_filename)):
                os.makedirs(os.path.dirname(tile_filename))
        try:
            return Response(open(tile_filename).read(), mimetype='image/png')
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
def computeTask(data,payload,cm_id):

    """
    :param data:
    :param payload:
    :param cm_id:
    :return:Rdeturns the calculation of a calculation module
    """
    inputs_vector_selection = None

    #****************** RETRIVE INPUT DATA ***************************************************'
    #transforme stringify array to json
    layer_needed = payload['layers_needed']
    type_layer_needed = payload['type_layer_needed']
    vectors_needed = payload['vectors_needed']
    #retriving scale level 3 possiblity hectare,nuts, lau
    scalevalue = data['scalevalue']
    if scalevalue == 'hectare':
        #****************** BEGIN RASTER CLIP FOR HECTAR ***************************************************
        areas = payload['areas']
        geom =  helper.area_to_geom(areas)
        inputs_raster_selection = model.get_raster_from_csv(DATASET_DIRECTORY ,geom,layer_needed, type_layer_needed, UPLOAD_DIRECTORY)
        inputs_vector_selection = model.retrieve_vector_data_for_calculation_module(vectors_needed, scalevalue, geom)
        #print ('inputs_raster_selection',inputs_raster_selection)
        #****************** FINISH RASTER CLIP FOR HECTAR ***************************************************'
    else:
        #****************** BEGIN RASTER CLIP FOR NUTS OR LAU ***************************************************'
        id_list = payload['nuts']
        shapefile_path = model.get_shapefile_from_selection(scalevalue,id_list,UPLOAD_DIRECTORY)
        inputs_raster_selection = model.clip_raster_from_shapefile(DATASET_DIRECTORY ,shapefile_path,layer_needed, type_layer_needed, UPLOAD_DIRECTORY)
        if vectors_needed != None:
            inputs_vector_selection = model.retrieve_vector_data_for_calculation_module(vectors_needed, scalevalue, id_list)
        #****************** FINISH RASTER CLIP FOR NUTS  OR LAU ***************************************************
    data = generate_payload_for_compute(data,inputs_raster_selection,inputs_vector_selection)


    # send the result to the right CM
    #****************** WILL SEND PAYLOAD TO CM WITH ID {} ***************************************************'.format(cm_id))
    calculation_module_rpc = CalculationModuleRpcClient()
    response = calculation_module_rpc.call(cm_id,data.encode('utf-8'))
    #'****************** RETRIVED RESULT FROM CM WITH ID {} ***************************************************'.format(cm_id))
    data_output = json.loads(response)
    helper.test_display(data_output)
    #****************** WILL GENERATE TILES ***************************************************'.format(cm_id))
    try:
        print ('time to generate tilexs generateTiles')
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

    print ('data_output',json.dumps(data_output))
    return data_output

def generateTiles(raster_layers):
    print ('generateTiles')
    print ('raster_layers',raster_layers)
    for layers in raster_layers:
        print ('in the loop')
        file_path_input = layers['path']
        directory_for_tiles = file_path_input.replace('.tif', '')
        intermediate_raster = helper.generate_geotif_name(UPLOAD_DIRECTORY)
        tile_path = directory_for_tiles
        access_rights = 0o755
        try:
            os.mkdir(tile_path, access_rights)
            print ('tile_path',tile_path)

        except OSError:
            pass
            print ("Creation of the directory %s failed" % tile_path)
        else:
            pass
        #import sys
        #sys.append('app/helper/')
        args_gdal = commands_in_array("gdal_translate -of GTiff -expand rgba {} {} -co COMPRESS=DEFLATE ".format(file_path_input, intermediate_raster))
        args_pyth = commands_in_array("python app/helper/gdal2tiles.py -d -p 'mercator' -w 'leaflet' -r 'near' -z 4-11 {} {}".format(intermediate_raster, tile_path))
        run_command(args_gdal)
        run_command(args_pyth)
        #com_string = "gdal_translate -of GTiff -expand rgba {} {} -co COMPRESS=DEFLATE && python app/helper/gdal2tiles.py -d -p 'mercator' -w 'leaflet' -r 'near' -z 4-11 {} {} ".format(file_path_input,intermediate_raster,intermediate_raster,tile_path)
        #os.system(com_string)
        #os.system(com_string)
        directory_for_tiles = directory_for_tiles.replace(UPLOAD_DIRECTORY+'/', '')
        layers['path'] = directory_for_tiles
        print ('path', directory_for_tiles)

    print ('finished generate Tiles')
    return file_path_input, directory_for_tiles

def generate_shape(vector_layers):
    for layers in vector_layers:
        file_path_input = layers['path']
    return file_path_input, file_path_input

def generate_payload_for_compute(data,inputs_raster_selection,inputs_vector_selection):
    inputs = data["inputs"]
    inputs_parameter_selection = {}
    data_output = {}
    for parameters in inputs:
        inputs_parameter_selection.update({
         parameters['input_parameter_name']: parameters['input_value']
        })
    data_output.update({
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
        cm_id = data["cm_id"]
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

