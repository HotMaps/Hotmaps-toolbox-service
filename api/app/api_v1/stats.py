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



import shapely.geometry as shapely_geom

from app import constants

from app.models import generalData
from app.helper import find_key_in_dict, getValuesFromName, retrieveCrossIndicator, createAllLayers,\
	getTypeScale, adapt_layers_list, adapt_nuts_list, removeScaleLayers, layers_filter, getTypeScale
import app

import json


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
		year = api.payload['year']
		layersPayload = api.payload['layers']
		nuts = api.payload['nuts']
		# Stop execution if layers list or nuts list is empty 
		if not layersPayload or not nuts:
			return

		# Get type
		type = getTypeScale(layersPayload)		

		# Layers filtration and management
		if type == 'nuts':
			allLayersTable = createAllLayers(constants.LAYERS_REF_NUTS_TABLE)
			allLayers = createAllLayers(constants.LAYERS_REF_NUTS)

			noTableLayers = layers_filter(layersPayload, allLayersTable)
			noDataLayers = layers_filter(layersPayload, allLayers)
			
		elif type == 'lau':
			allLayersTable = createAllLayers(constants.LAYERS_REF_LAU_TABLE)
			allLayers = createAllLayers(constants.LAYERS_REF_LAU)

			noTableLayers = layers_filter(layersPayload, allLayersTable)
			noDataLayers = layers_filter(layersPayload, allLayers)
		else:
			return

		# Keep only existing layers
		
		layers = adapt_layers_list(layersPayload=layersPayload, type=type, allLayers=allLayers)
		output = []
		res = LayersStats.stats_nuts_lau.delay(nuts=adapt_nuts_list(nuts), year=year, layers=layers, type=type)
		output = res.get()


		# compute Cross indicators if both layers are selected
		pop1ha_name = constants.POPULATION_TOT
		hdm_name = constants.HEAT_DENSITY_TOT
		heat_curr_non_res_name = constants.HEAT_DENSITY_NON_RES
		heat_curr_res_name = constants.HEAT_DENSITY_RES


		retrieveCrossIndicator(pop1ha_name, heat_curr_non_res_name, layers, output)
		retrieveCrossIndicator(pop1ha_name, heat_curr_res_name, layers, output)
		retrieveCrossIndicator(pop1ha_name, hdm_name, layers, output)

		# Remove scale for each layer
		noTableLayers = removeScaleLayers(noTableLayers, type)
		noDataLayers = removeScaleLayers(noDataLayers, type)

		# output
		return {
			"layers": output,
			"no_data_layers": noDataLayers,
			"no_table_layers": noTableLayers
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
		# Entrees
		year = api.payload['year']
		layersPayload = api.payload['layers']        
		areas = api.payload['areas']


		# Layers filtration and management
		allLayersTable = createAllLayers(constants.LAYERS_REF_HECTARES_TABLE)
		allLayers = createAllLayers(constants.LAYERS_REF_HECTARES)
		noTableLayers = layers_filter(layersPayload, allLayersTable)
		noDataLayers = layers_filter(layersPayload, allLayers)

		# Keep only existing layers
		layers = adapt_layers_list(layersPayload=layersPayload, type='ha', allLayers=allLayers)

		polyArray = []
		output = []

		# convert to polygon format for each polygon and store them in polyArray
		for polygon in areas:
			po = shapely_geom.Polygon([[p['lng'], p['lat']] for p in polygon['points']])
			polyArray.append(po)


		# convert array of polygon into multipolygon
		multipolygon = shapely_geom.MultiPolygon(polyArray)

		#geom = "SRID=4326;{}".format(multipolygon.wkt)
		geom = multipolygon.wkt

		res = LayersStats.stats_hectares.delay(geometry=geom, year=year, layers=layers)
		output = res.get()

		# compute heat consumption/person if both layers are selected
		pop1ha_name = constants.POPULATION_TOT
		hdm_name = constants.HEAT_DENSITY_TOT
		heat_curr_non_res_name = constants.HEAT_DENSITY_NON_RES
		heat_curr_res_name = constants.HEAT_DENSITY_RES
		gfa_tot_curr_density_name = constants.GRASS_FLOOR_AREA_TOT


		retrieveCrossIndicator(pop1ha_name, heat_curr_non_res_name, layers, output)
		retrieveCrossIndicator(pop1ha_name, heat_curr_res_name, layers, output)
		retrieveCrossIndicator(pop1ha_name, hdm_name, layers, output)
		retrieveCrossIndicator(gfa_tot_curr_density_name, hdm_name, layers, output)

		# Remove scale for each layer
		noTableLayers = removeScaleLayers(noTableLayers, type='ha')
		noDataLayers = removeScaleLayers(noDataLayers, type='ha')

		#output
		return {
			"layers": output,
			"no_data_layers": noDataLayers,
			"no_table_layers": noTableLayers
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

