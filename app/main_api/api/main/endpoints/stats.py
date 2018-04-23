import logging
import re
from flask import request
from flask_restplus import Resource
from main_api.api.main.serializers import stats_layers_area_input, stats_layers_output, stats_layers_hectares_output, stats_layers_nuts_input, stats_layers_nuts_output, stats_layer_point_input, stats_layers_area_nuts_input, stats_layers_hectares_input
from main_api.api.restplus import api
from main_api.models.nuts import Nuts, NutsRG01M
from main_api.models.lau import Lau
from main_api.models.statsQueries import LayersHectare
from main_api.models.statsQueries import LayersNutsLau
from sqlalchemy import func, BigInteger, TypeDecorator
from main_api.models import db
import datetime
import shapely.geometry as shapely_geom
from geojson import FeatureCollection, Feature
from geoalchemy2.shape import to_shape
from main_api import settings

from main_api.models import generalData



log = logging.getLogger(__name__)

ns = api.namespace('stats', description='Operations related to statistisdscs')


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
		year = api.payload['year']
		layersPayload = api.payload['layers']
		nuts = api.payload['nuts']

		# Stop execution if layers list or nuts list is empty 
		if not layersPayload or not nuts:
			return

		# Get type
		type = generalData.getTypeScale(layersPayload)		

		# Layers filtration and management
		if type == 'nuts':
			allLayersTable = generalData.createAllLayers(settings.LAYERS_REF_NUTS_TABLE)
			allLayers = generalData.createAllLayers(settings.LAYERS_REF_NUTS)

			noTableLayers = generalData.layers_filter(layersPayload, allLayersTable)
			noDataLayers = generalData.layers_filter(layersPayload, allLayers)

		elif type == 'lau':
			allLayersTable = generalData.createAllLayers(settings.LAYERS_REF_LAU_TABLE)
			allLayers = generalData.createAllLayers(settings.LAYERS_REF_LAU)

			noTableLayers = generalData.layers_filter(layersPayload, allLayersTable)
			noDataLayers = generalData.layers_filter(layersPayload, allLayers)
		else:
			return

		# Keep only existing layers
		layers = generalData.adapt_layers_list(layersPayload=layersPayload, type=type, allLayers=allLayers)

		output = []

		res = LayersNutsLau.stats_nuts_lau(nuts=generalData.adapt_nuts_list(nuts), year=year, layers=layers, type=type)
		output = res

		# compute heat consumption/person if both layers are selected
		pop_nuts_name = settings.POPULATION_TOT
		heat_nuts_name = settings.HEAT_DENSITY_TOT

		if pop_nuts_name in layers and heat_nuts_name in layers:
			generalData.computeConsPerPerson(pop_nuts_name, heat_nuts_name, output)

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

		# Stop execution if layers list or areas list is empty 
		if not layersPayload or not areas:
			return

		# Layers filtration and management
		allLayersTable = generalData.createAllLayers(settings.LAYERS_REF_HECTARES_TABLE)
		allLayers = generalData.createAllLayers(settings.LAYERS_REF_HECTARES)
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

		res = LayersHectare.stats_hectares(geometry=geom, year=year, layers=layers)
		output = res

		# compute heat consumption/person if both layers are selected
		pop1ha_name = settings.POPULATION_TOT
		hdm_name = settings.HEAT_DENSITY_TOT

		if pop1ha_name in layers and hdm_name in layers:
			generalData.computeConsPerPerson(pop1ha_name, hdm_name, output)

		# Remove scale for each layer
		noTableLayers = generalData.removeScaleLayers(noTableLayers, type='ha')
		noDataLayers = generalData.removeScaleLayers(noDataLayers, type='ha')

		#output
		return {
			"layers": output,
			"no_data_layers": noDataLayers,
			"no_table_layers": noTableLayers
		}