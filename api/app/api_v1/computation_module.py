
from flask import request, current_app
from app.decorators.restplus import api
from app.decorators.serializers import  compution_module_class, \
    input_computation_module, test_communication_cm, \
    compution_module_list
from app.model import register_calulation_module,getCMUrl

nsCM = api.namespace('cm', description='Operations related to statistisdscs')
ns = nsCM
from flask_restplus import Resource
from app import celery
import requests

#TODO Add url to find  right computation module
URL_CM = 'http://127.0.0.1:5001/'
list_of_computation_module  = [

    {'id': 1,
     'cm_name': 'Computational_module_1',
     'category': 'Buildings',
      'layers_needed': ['heat_tot_curr_density']
     },
    {'id': 2, 'cm_name': 'Computational_module_2', 'category': 'Buildings','layers_needed': ['heat_tot_curr_density']},

    {'id': 3, 'cm_name': 'Computational_module_3', 'category': 'R.E.S. Potential','layers_needed': ['heat_tot_curr_density']},
    {'id': 4, 'cm_name': 'Computational_module_4', 'category': 'R.E.S. Potential','layers_needed': ['heat_tot_curr_density']},
    {'id': 5, 'cm_name': 'Computational_module_5', 'category': 'Climate','layers_needed': ['heat_tot_curr_density']},
    {'id': 6, 'cm_name': 'Computational_module_6', 'category': 'Climate','layers_needed': ['heat_tot_curr_density']},
    {'id': 7, 'cm_name': 'Computational_module_7', 'category': 'Climate','layers_needed': ['heat_tot_curr_density']},
    {'id': 8, 'cm_name': 'Computational_module_8', 'category': 'Industry','layers_needed': ['heat_tot_curr_density']},
    {'id': 9, 'cm_name': 'Computational_module_9', 'category': 'Industry','layers_needed': ['heat_tot_curr_density']},

];
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
            "list": list_of_computation_module}


@ns.route('/register/', methods=['POST'])
class ComputationModuleClass(Resource):
    # @api.expect(input_computation_module)
    #@api.expect(compution_module_class)
    def post(self):
        input = request.get_json()
        registerCM.delay(input)



@celery.task(name = 'registerCM')
def registerCM(input):
    print 'input', input
    register_calulation_module(input)

@celery.task(name = 'getCMUrl')
def getCMUrl(cm_id):
    return getCMUrl(cm_id)


    #return {}, 201, {'Location': cm.get_url()}

@ns.route('/compute/')
class ComputationModuleCompute(Resource):
   # @api.expect(input_computation_module)
    @api.expect(input_computation_module)
    @api.marshal_with(test_communication_cm)
    def post(self):
        """
        Returns the statistics for specific layers, area and year
        :return:

        """
        print 'request {}'.format(request.get_json())
        data = request.get_json()
        cm_id = data["cm_id"]
        # 1. find the good computation module with the right url in the database from cm db  => generate url

        url_cm = getCMUrl(cm_id)


        # 2. if this is a raster clip of the raster or provide vector needed => generate link

        data = api.payload
        #res = requests.post(URL_CM + 'computation-module/compute/', data = api.payload)
        print current_app.name
        app = current_app._get_current_object()
        #with app.app_context():


            #app.app_context().push()
        res = computeCM.delay(url_cm, data)
        response = res.wait()
        print 'response:',response
        return response
        #print 'res:',res
        #print response
        #print 'response from server:',response.text
        #return response.text



@celery.task(name = 'getComputationModule-URL')
def getUrlFromDB():
    url = 'http://127.0.0.1:5001/'
    return url

@celery.task(name = 'ComputeCM')
def computeCM(url,data):
    res = requests.post(url + 'computation-module/compute/', data = data)
    reponse = res.text
    return reponse



