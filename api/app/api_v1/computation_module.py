from celery.task.control import revoke
from flask import request, current_app,jsonify,redirect, \
    url_for,Response
from app.decorators.restplus import api
from app.decorators.serializers import  compution_module_class, \
    input_computation_module, test_communication_cm, \
    compution_module_list, uploadfile, cm_id_input

from app.model import register_calulation_module,getCMUrl,getUI,getCMList,getLayerNeeded


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

com_string = "chmod +x app/helper/gdal2tiles-multiprocess.py"

os.system(com_string)

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

        print ('user-interface',getUI(cm_id))
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



def registerCM(input):
    register_calulation_module(input)
    return input



@celery.task(name = 'task-celery_get_CM_url')
def celery_get_CM_url(cm_id):
    return getCMUrl(cm_id)






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
def computeTask(data,payload,cm_id,layerneed):

    """
    Rdeturns the calculation of a calculation module
    :return:

    """
    inputs_raster_selection = None
    inputs_parameter_selection = None
    inputs_vector_selection = None



    print ('****************** RETRIVE INPUT DATA ***************************************************')
    #transforme stringify array to json
    print ('layer_needed', payload)
    #layer_needed = helper.unicode_array_to_string(layerneed)

    layer_needed = payload['layers_needed']

    vectors_needed = model.get_vectors_needed(cm_id)




    print ('layer_needed_inside', layer_needed)


    # retriving scale level 3 possiblity hectare,nuts, lau

    scalevalue = data['scalevalue']
    if scalevalue == 'hectare':
        print ('****************** BEGIN RASTER CLIP FOR HECTAR ***************************************************')
        areas = payload['areas']
        geom =  helper.area_to_geom(areas)
        #get the rasters selected
        inputs_raster_selection = model.get_raster_from_csv(DATASET_DIRECTORY ,geom,layer_needed, UPLOAD_DIRECTORY)

        inputs_vector_selection = model.retrieve_vector_data_for_calculation_module(vectors_needed, scalevalue, geom)
        #get the vectors selected

        print ('inputs_raster_selection',inputs_raster_selection)
        print ('****************** FINISH RASTER CLIP FOR HECTAR ***************************************************')

        # we will be working on hectare level

    else:
        print ('****************** BEGIN RASTER CLIP FOR NUTS OR LAU ***************************************************')
        id_list = payload['nuts']
        shapefile_path = model.get_shapefile_from_selection(scalevalue,id_list,UPLOAD_DIRECTORY)
        inputs_raster_selection = model.clip_raster_from_shapefile(DATASET_DIRECTORY ,shapefile_path,layer_needed, UPLOAD_DIRECTORY)
        if vectors_needed != None:
            inputs_vector_selection = model.retrieve_vector_data_for_calculation_module(vectors_needed, scalevalue, id_list)
        print ('****************** FINISH RASTER CLIP FOR NUTS  OR LAU ***************************************************')

        # we will be working on a nuts

    data = generate_payload_for_compute(data,inputs_raster_selection,inputs_vector_selection)


    # send the result to the right CM
    print ('****************** WILL SEND PAYLOAD TO CM WITH ID {} ***************************************************'.format(cm_id))
    calculation_module_rpc = CalculationModuleRpcClient()
    response = calculation_module_rpc.call(cm_id,data.encode('utf-8'))
    print ('****************** RETRIVED RESULT FROM CM WITH ID {} ***************************************************'.format(cm_id))
    data_output = json.loads(response)
    helper.test_display(data_output)
    print ('****************** WILL GENERATE TILES ***************************************************'.format(cm_id))
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





def generateTiles(raster_layers):

    for layers in raster_layers:
        file_path_input = layers['path']
        directory_for_tiles = file_path_input.replace('.tif', '')

        intermediate_raster = helper.generate_geotif_name(UPLOAD_DIRECTORY)
        tile_path = directory_for_tiles
        access_rights = 0o755

        try:
            os.mkdir(tile_path, access_rights)
        except OSError:
            print ("Creation of the directory %s failed" % tile_path)
        else:
            print ("Successfully created the directory %s" % tile_path)


        com_string = "gdal_translate -of GTiff -expand rgba {} {} -co COMPRESS=DEFLATE && python app/helper/gdal2tiles.py -d -p 'mercator' -w 'leaflet' -r 'near' -z 4-11 {} {} ".format(file_path_input,intermediate_raster,intermediate_raster,tile_path)

        #com_string = "gdal_translate -of GTiff -expand rgba {} {} -co COMPRESS=DEFLATE && python app/helper/gdal2tiles-multiprocess.py -d -p 'mercator' -r 'near' -n -l -z 4-13 {} {} ".format(file_path_input,intermediate_raster,intermediate_raster,tile_path)

        os.system(com_string)
        directory_for_tiles = directory_for_tiles.replace(UPLOAD_DIRECTORY+'/', '')
        layers['path'] = directory_for_tiles

        # gdal2tiles.generate_tiles(intermediate_raster, tile_path, np_processes=12, zoom='7-9')

    return file_path_input, directory_for_tiles

    #com_string = "gdal_translate -of GTiff -expand rgba {} {} -co COMPRESS=DEFLATE && python app/helper/gdal2tiles-multiprocess.py -d -p 'mercator' -r 'near' -n -l -z 4-13 {} {} ".format(file_path_input,intermediate_raster,intermediate_raster,tile_path)

def generate_shape(vector_layers):
    for layers in vector_layers:
        file_path_input = layers['path']
        print ('file_path_input',file_path_input)


    return file_path_input, file_path_input


def generate_payload_for_compute(data,inputs_raster_selection,inputs_vector_selection):
    inputs = data["inputs"]
    print ('inputs', inputs)
    inputs_parameter_selection = {}
    data_output = {}
    for parameters in inputs:
        print ('parameters[input_parameter_name]',parameters['input_parameter_name'])
        print ('parameters[input_parameter_name]',parameters['input_value'])
        inputs_parameter_selection.update({
         parameters['input_parameter_name']: parameters['input_value']
        })


    data_output.update({
        'inputs_parameter_selection':inputs_parameter_selection,
        'inputs_raster_selection':inputs_raster_selection,
        'inputs_vector_selection':inputs_vector_selection
    })
    print ('data_output',data_output)
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
        print ('HTAPI will compute cm')
        app = current_app._get_current_object()
        data = request.get_json()
        payload = api.payload['payload']
        cm_id = data["cm_id"]
        #2 inputs layers from the CM
        layerneed = getLayerNeeded(cm_id)
        with app.app_context():
            task = computeTask.delay(data,payload,cm_id,layerneed)
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

