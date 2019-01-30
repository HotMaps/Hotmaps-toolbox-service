from app import celery
import logging
import re

from flask_restplus import Resource
from app.decorators.serializers import  stats_layers_hectares_output,\
	stats_layers_nuts_input, stats_layers_nuts_output,\
	stats_layers_hectares_input, stats_list_nuts_input, stats_list_label_dataset
from app.decorators.restplus import api
from app.decorators.exceptions import HugeRequestException, IntersectionException, NotEnoughPointsException, ParameterException, RequestException

from app.models.statsQueries import ElectricityMix
from app.models.statsQueries import LayersStats


from app.models.indicators import layersData
import shapely.geometry as shapely_geom

from app import constants

from app.models import generalData
from app.helper import find_key_in_dict, getValuesFromName, retrieveCrossIndicator, createAllLayers,\
	getTypeScale, adapt_layers_list, adapt_nuts_list, removeScaleLayers, layers_filter, getTypeScale
import app
import json
from app.model import check_table_existe




log = logging.getLogger(__name__)

nsStats = api.namespace('stats', description='Operations related to statistics')
ns = nsStats


@ns.route('/layers/nuts-lau')
@api.response(404, 'No data found for that specific list of NUTS.')
@api.response(530, 'Request Error')
@api.response(531, 'Missing parameter.')
class StatsLayersNutsInArea(Resource):
	@api.marshal_with(stats_layers_nuts_output)
	@api.expect(stats_layers_nuts_input)
	def post(self):
		"""
		Returns the statistics for specific layers, area and year
		:return:
		"""
		#try:
		# Entries
		wrong_parameter = [];
		try:
			year = api.payload['year']
		except:
			wrong_parameter.append('year')
		try:
			layersPayload = api.payload['layers']
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
			raise ParameterException(exception_message + '')

		# Stop execution if layers list or nuts list is empty
		if not layersPayload or not nuts:
			return

		# Get type


		output, noDataLayers = LayersStats.run_stat(api.payload)
		# output
		return {
			"layers": output,
			"no_data_layers": noDataLayers,
			"no_table_layers": noDataLayers
		}


@ns.route('/layers/hectares')
@api.response(0, 'Request too big')
@api.response(404, 'No data found for that specific area.')
@api.response(530, 'Request error.')
@api.response(531, 'Missing parameter.')
@api.response(533, 'SQL error.')
#@api.response(534, 'Not enough points error.')
class StatsLayersHectareMulti(Resource):
	@api.marshal_with(stats_layers_hectares_output)
	@api.expect(stats_layers_hectares_input)
	def post(self):
		"""
		Returns the statistics for specific layers, hectares and year
		:return:
		"""
		#try:
		# Entries
		wrong_parameter = [];
		layersPayload = api.payload['layers']
		try:
			year = api.payload['year']
		except:
			wrong_parameter.append('year')
		try:
			layersPayload = api.payload['layers']
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
				if (i != len(wrong_parameter) - 1):
					exception_message += ', '
			raise ParameterException(str(exception_message))





		output, noDataLayers = LayersStats.run_stat(api.payload)
		#print ("output hectare ",output)

		#output
		return {
			"layers": output,
			"no_data_layers": noDataLayers,
			"no_table_layers": noDataLayers
		}







@ns.route('/energy-mix/nuts-lau')
@api.response(0, 'Request too big')
@api.response(404, 'No data found for that specific list of NUTS.')
@api.response(530, 'Request error.')
@api.response(531, 'Missing parameter.')
class StatsLayersNutsInArea(Resource):
	@api.marshal_with(stats_list_label_dataset)
	@api.expect(stats_list_nuts_input)
	def post(self):
		"""
		Returns the statistics for specific layers, area and year
		:return:
		"""
		# Entries
		wrong_parameter = [];
		try:
			nuts = api.payload['nuts']
		except:
			wrong_parameter.append('nuts')

		# raise exception if parameters are false
		if len(wrong_parameter) > 0:
			exception_message = ''
			for i in range(len(wrong_parameter)):
				exception_message += wrong_parameter[i]
				if (i != len(wrong_parameter) - 1):
					exception_message += ', '
			raise ParameterException(str(exception_message))

		res = ElectricityMix.getEnergyMixNutsLau(adapt_nuts_list(nuts))
		return res


		# Remove scale for each layer




@celery.task(name = 'energy_mix_nuts_lau')
def processGenerationMix(nuts):
	if not nuts:
		return
	res = ElectricityMix.getEnergyMixNutsLau(adapt_nuts_list(nuts))

	return res

