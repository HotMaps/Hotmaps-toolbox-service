from app import celery
import logging
import re

from flask_restplus import Resource
from app.decorators.serializers import  stats_layers_hectares_output,\
	stats_layers_nuts_input, stats_layers_nuts_output,\
	stats_layers_hectares_input, stats_list_nuts_input, stats_list_label_dataset
from app.decorators.restplus import api
from app.decorators.exceptions import HugeRequestException, IntersectionException, NotEnoughPointsException, ParameterException, RequestException

from app.models.statsQueries import LayersHectare
from app.models.statsQueries import ElectricityMix
from app.models.statsQueries import LayersNutsLau


import shapely.geometry as shapely_geom

from app import constants

from app.models import generalData
from app.helper import find_key_in_dict, getValuesFromName, retrieveCrossIndicator
import app


import json


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
				if (i != len(wrong_parameter) - 1):
					exception_message += ', '
			raise ParameterException(exception_message + '')

		# Stop execution if layers list or nuts list is empty
		if not layersPayload or not nuts:
			return

		# Get type
		type = generalData.getTypeScale(layersPayload)

		# Layers filtration and management
		if type == 'nuts':
			allLayersTable = generalData.createAllLayers(constants.LAYERS_REF_NUTS_TABLE)
			allLayers = generalData.createAllLayers(constants.LAYERS_REF_NUTS)

			noTableLayers = generalData.layers_filter(layersPayload, allLayersTable)
			noDataLayers = generalData.layers_filter(layersPayload, allLayers)

		elif type == 'lau':
			allLayersTable = generalData.createAllLayers(constants.LAYERS_REF_LAU_TABLE)
			allLayers = generalData.createAllLayers(constants.LAYERS_REF_LAU)

			noTableLayers = generalData.layers_filter(layersPayload, allLayersTable)
			noDataLayers = generalData.layers_filter(layersPayload, allLayers)
		else:
			return

		# Keep only existing layers
		layers = generalData.adapt_layers_list(layersPayload=layersPayload, type=type, allLayers=allLayers)

		output = []

		res = LayersNutsLau.stats_nuts_lau.delay(nuts=generalData.adapt_nuts_list(nuts), year=year, layers=layers, type=type)
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
		noTableLayers = generalData.removeScaleLayers(noTableLayers, type)
		noDataLayers = generalData.removeScaleLayers(noDataLayers, type)

		# output
		return {
			"layers": output,
			"no_data_layers": noDataLayers,
			"no_table_layers": noTableLayers
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



		# Layers filtration and management
		allLayersTable = generalData.createAllLayers(constants.LAYERS_REF_HECTARES_TABLE)
		allLayers = generalData.createAllLayers(constants.LAYERS_REF_HECTARES)
		noTableLayers = generalData.layers_filter(layersPayload, allLayersTable)
		noDataLayers = generalData.layers_filter(layersPayload, allLayers)

		# Keep only existing layers
		layers = generalData.adapt_layers_list(layersPayload=layersPayload, type='ha', allLayers=allLayers)

		polyArray = []
		output = []

		# convert to polygon format for each polygon and store them in polyArray
		try:
			for polygon in areas:
				po = shapely_geom.Polygon([[p['lng'], p['lat']] for p in polygon['points']])
				polyArray.append(po)
		except:
			raise NotEnoughPointsException

		# convert array of polygon into multipolygon
		multipolygon = shapely_geom.MultiPolygon(polyArray)

		#geom = "SRID=4326;{}".format(multipolygon.wkt)
		geom = multipolygon.wkt
		try:
            res = LayersHectare.stats_hectares.delay(geometry=geom, year=year, layers=layers)
            output = res.get()
        except:
            raise IntersectionException()
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
		noTableLayers = generalData.removeScaleLayers(noTableLayers, type='ha')
		noDataLayers = generalData.removeScaleLayers(noDataLayers, type='ha')

		#output
		return {
			"layers": output,
			"no_data_layers": noDataLayers,
			"no_table_layers": noTableLayers
		}


@celery.task(name = 'layer_hectare')
def indicatorsHectares(year,layersPayload,areas):
	if not layersPayload or not areas:
		return

		# Layers filtration and management
	allLayersTable = generalData.createAllLayers(constants.LAYERS_REF_HECTARES_TABLE)
	allLayers = generalData.createAllLayers(constants.LAYERS_REF_HECTARES)
	noTableLayers = generalData.layers_filter(layersPayload, allLayersTable)
	noDataLayers = generalData.layers_filter(layersPayload, allLayers)

	# Keep only existing layers
	layers = generalData.adapt_layers_list(layersPayload=layersPayload, type='ha', allLayers=allLayers)

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

	try:
		res = LayersHectare.stats_hectares(geometry=geom, year=year, layers=layers)
	except:
		raise IntersectionException
	output = res

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
	noTableLayers = generalData.removeScaleLayers(noTableLayers, type='ha')
	noDataLayers = generalData.removeScaleLayers(noDataLayers, type='ha')

	return output, noTableLayers, noDataLayers


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

		res = ElectricityMix.getEnergyMixNutsLau(generalData.adapt_nuts_list(nuts))
		return res


		# Remove scale for each layer




@celery.task(name = 'energy_mix_nuts_lau')
def processGenerationMix(nuts):
	if not nuts:
		return
	res = ElectricityMix.getEnergyMixNutsLau(generalData.adapt_nuts_list(nuts))

	return res

