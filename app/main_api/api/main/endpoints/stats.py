import logging
import re
from flask import request
from flask_restplus import Resource
from main_api.api.main.serializers import stats_layers_area_input, stats_layers_output, stats_layers_hectares_output, stats_layers_nuts_input, stats_layers_nuts_output, stats_layer_point_input, stats_layers_area_nuts_input, stats_layers_hectares_input
from main_api.api.restplus import api
#from main_api.models.wwtp import Wwtp, WwtpNuts3, WwtpLau2, WwtpNuts2, WwtpNuts1, WwtpNuts0
#from main_api.models.heat_density_map import HeatDensityMap, HeatDensityHa, HeatDensityNuts3, HeatDensityLau2, HeatDensityNuts0, HeatDensityNuts1, HeatDensityNuts2
#from main_api.models.population_density import PopulationDensityHa, PopulationDensityNuts3, PopulationDensityLau2, PopulationDensityNuts2, PopulationDensityNuts1,PopulationDensityNuts0
from main_api.models.statsQueries import HeatDensityMapModel, HeatDensityHaModel, HeatDensityNuts3, HeatDensityLau2, HeatDensityNuts0, HeatDensityNuts1, \
HeatDensityNuts2, PopulationDensityHaModel, PopulationDensityNuts3, PopulationDensityLau2, PopulationDensityNuts2, PopulationDensityNuts1, \
PopulationDensityNuts0, Wwtp, WwtpNuts3, WwtpLau2, WwtpNuts2, WwtpNuts1, WwtpNuts0, \
GrassFloorAreaNuts3, GrassFloorAreaNuts2, GrassFloorAreaNuts1, GrassFloorAreaNuts0, GrassFloorAreaLau2, \
BuildingsVolumesTotNuts3, BuildingsVolumesTotNuts2, BuildingsVolumesTotNuts1, BuildingsVolumesTotNuts0, BuildingsVolumesTotLau2, \
BuildingsVolumesResNuts3, BuildingsVolumesResNuts2, BuildingsVolumesResNuts1, BuildingsVolumesResNuts0, BuildingsVolumesResLau2, \
BuildingsVolumesNonResNuts3, BuildingsVolumesNonResNuts2, BuildingsVolumesNonResNuts1, BuildingsVolumesNonResNuts0, BuildingsVolumesNonResLau2
from main_api.models.nuts import Nuts, NutsRG01M
from main_api.models.lau import Lau
from main_api.models.statsQueries import LayersHectare
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

layers_ref = {
	settings.WWTP: Wwtp,
	settings.WWTP + '_nuts3': WwtpNuts3,
	settings.WWTP + '_nuts2': WwtpNuts2,
	settings.WWTP + '_nuts1': WwtpNuts1,
	settings.WWTP + '_nuts0': WwtpNuts0,
	settings.WWTP + '_ha': Wwtp,
	settings.WWTP + '_lau2': WwtpLau2,
	settings.POPULATION_TOT: PopulationDensityNuts3,
	settings.POPULATION_TOT + '_nuts3': PopulationDensityNuts3,
	settings.POPULATION_TOT + '_nuts2': PopulationDensityNuts2,
	settings.POPULATION_TOT + '_nuts1': PopulationDensityNuts1,
	settings.POPULATION_TOT + '_nuts0': PopulationDensityNuts0,
	settings.POPULATION_TOT + '_ha': PopulationDensityHaModel,
	settings.POPULATION_TOT + '_lau2': PopulationDensityLau2,
	settings.HEAT_DENSITY_TOT: HeatDensityMapModel,
	settings.HEAT_DENSITY_TOT + '_ha': HeatDensityHaModel,
	settings.HEAT_DENSITY_TOT + '_nuts3': HeatDensityNuts3,
	settings.HEAT_DENSITY_TOT + '_nuts2': HeatDensityNuts2,
	settings.HEAT_DENSITY_TOT + '_nuts1': HeatDensityNuts1,
	settings.HEAT_DENSITY_TOT + '_nuts0': HeatDensityNuts0,
	settings.HEAT_DENSITY_TOT + '_lau2': HeatDensityLau2,
	settings.GRASS_FLOOR_AREA_TOT + '_ha': None,
	settings.GRASS_FLOOR_AREA_RES + '_ha': None,
	settings.GRASS_FLOOR_AREA_NON_RES + '_ha': None,
	settings.BUILDING_VOLUMES_TOT + '_ha': None,
	settings.BUILDING_VOLUMES_RES + '_ha': None,
	settings.BUILDING_VOLUMES_NON_RES + '_ha': None,
	settings.HEAT_DENSITY_RES + '_ha': None,
	settings.HEAT_DENSITY_NON_RES + '_ha': None,
	settings.GRASS_FLOOR_AREA_TOT + '_nuts3': GrassFloorAreaNuts3,
	settings.GRASS_FLOOR_AREA_TOT + '_nuts2': GrassFloorAreaNuts2,
	settings.GRASS_FLOOR_AREA_TOT + '_nuts1': GrassFloorAreaNuts1,
	settings.GRASS_FLOOR_AREA_TOT + '_nuts0': GrassFloorAreaNuts0,
	settings.GRASS_FLOOR_AREA_TOT + '_lau2': GrassFloorAreaLau2,
	settings.BUILDING_VOLUMES_TOT + '_nuts3': BuildingsVolumesTotNuts3,
	settings.BUILDING_VOLUMES_TOT + '_nuts2': BuildingsVolumesTotNuts2,
	settings.BUILDING_VOLUMES_TOT + '_nuts1': BuildingsVolumesTotNuts1,
	settings.BUILDING_VOLUMES_TOT + '_nuts0': BuildingsVolumesTotNuts0,
	settings.BUILDING_VOLUMES_TOT + '_lau2': BuildingsVolumesTotLau2,
	settings.BUILDING_VOLUMES_RES + '_nuts3': BuildingsVolumesResNuts3,
	settings.BUILDING_VOLUMES_RES + '_nuts2': BuildingsVolumesResNuts2,
	settings.BUILDING_VOLUMES_RES + '_nuts1': BuildingsVolumesResNuts1,
	settings.BUILDING_VOLUMES_RES + '_nuts0': BuildingsVolumesResNuts0,
	settings.BUILDING_VOLUMES_RES + '_lau2': BuildingsVolumesResLau2,
	settings.BUILDING_VOLUMES_NON_RES + '_nuts3': BuildingsVolumesNonResNuts3,
	settings.BUILDING_VOLUMES_NON_RES + '_nuts2': BuildingsVolumesNonResNuts2,
	settings.BUILDING_VOLUMES_NON_RES + '_nuts1': BuildingsVolumesNonResNuts1,
	settings.BUILDING_VOLUMES_NON_RES + '_nuts0': BuildingsVolumesNonResNuts0,
	settings.BUILDING_VOLUMES_NON_RES + '_lau2': BuildingsVolumesNonResLau2
	#settings.GEOTHERMAL_POTENTIAL + '_ha':None
}


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
		year = api.payload['year']
		layers = api.payload['layers']
		nuts = api.payload['nuts']

		# compute nuts level
		nuts_level = 0
		for n in nuts:
			if len(n)-2 > nuts_level:
				nuts_level = len(n)-2

		output = []

		# for each layer,
		# try to match layer name with layer class
		# run aggregate_for_selection method
		for layer in layers:
			try:
				a = layers_ref[layer]()
			except KeyError:
				continue
			output.append({
				'name': layer,
				'values': a.aggregate_for_nuts_selection(nuts=nuts, year=year)
			})

		# compute heat consumption/person if both layers are selected


		pop_nuts_name = settings.POPULATION_TOT + '_nuts3'
		heat_nuts_name = settings.HEAT_DENSITY_TOT + '_nuts3'

		if pop_nuts_name in layers and heat_nuts_name in layers:
			generalData.computeConsPerPerson(pop_nuts_name, heat_nuts_name, output)

		# compute heat consumption/person if both layers are selected
		pop_lau_name = settings.POPULATION_TOT + '_lau2'
		heat_lau_name = settings.HEAT_DENSITY_TOT + '_lau2'

		if pop_lau_name in layers and heat_lau_name in layers:
			generalData.computeConsPerPerson(pop_lau_name, heat_lau_name, output)

		# output
		return {
			"layers": output,
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

		# Keep only existing layers
		layers = []
		for layer in layersPayload:
			if layer in layers_ref:
				layers.append(layer)

		# Stop execution if layers list is empty 
		if not layers:
			return

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
		pop1ha_name = settings.POPULATION_TOT + '_ha'
		hdm_name = settings.HEAT_DENSITY_TOT + '_ha'

		if pop1ha_name in layers and hdm_name in layers:
			generalData.computeConsPerPerson(pop1ha_name, hdm_name, output)

		#output
		return {
			"layers": output,
		}