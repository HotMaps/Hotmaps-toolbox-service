from app import celery
import logging
import re

from flask_restplus import Resource
from app.decorators.serializers import  stats_layers_hectares_output,\
	stats_layers_nuts_input, stats_layers_nuts_output,\
	stats_layers_hectares_input, stats_list_nuts_input, stats_list_label_dataset
from app.decorators.restplus import api

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

nsStats = api.namespace('stats', description='Operations related to statistisdscs')
ns = nsStats


@ns.route('/layers/nuts-lau')
@api.response(404, 'No data found for that specific list of NUTS.')
class StatsLayersNutsInArea(Resource):
	@api.marshal_with(stats_layers_nuts_output)
	@api.expect(stats_layers_nuts_input)
	def post(self):
		"""
		Returns the statistics for specific layers, area and year
		:return:
		"""
		# Entrees
		print ('/layers/nuts-lau')
		
		if not api.payload['nuts']:
			return
		output, noDataLayers = LayersStats.run_stat(api.payload)
		# output
		return {
			"layers": output,
			"no_data_layers": noDataLayers,
			"no_table_layers": noDataLayers
		}


@ns.route('/layers/hectares')
@api.response(404, 'No data found for that specific area.')
class StatsLayersHectareMulti(Resource):
	@api.marshal_with(stats_layers_hectares_output)
	@api.expect(stats_layers_hectares_input)
	def post(self):
		"""
		Returns the statistics for specific layers, hectares and year
		:return:
		"""

		output, noDataLayers = LayersStats.run_stat(api.payload)

		#output
		return {
			"layers": output,
			"no_data_layers": noDataLayers,
			"no_table_layers": noDataLayers
		}







@ns.route('/energy-mix/nuts-lau')
@api.response(404, 'No data found for that specific list of NUTS.')
class StatsLayersNutsInArea(Resource):
	@api.marshal_with(stats_list_label_dataset)
	@api.expect(stats_list_nuts_input)
	def post(self):
		"""
		Returns the statistics for specific layers, area and year
		:return:
		"""
		# Entrees
		nuts = api.payload['nuts']
		res = ElectricityMix.getEnergyMixNutsLau(adapt_nuts_list(nuts))
		return res


		# Remove scale for each layer




@celery.task(name = 'energy_mix_nuts_lau')
def processGenerationMix(nuts):
	if not nuts:
		return
	res = ElectricityMix.getEnergyMixNutsLau(adapt_nuts_list(nuts))

	return res

