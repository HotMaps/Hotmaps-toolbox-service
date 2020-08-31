from app import celery
import logging
import re
import os.path
import pandas as pd
import numpy as np
from osgeo import gdal

from flask_restplus import Resource
from app.decorators.serializers import  stats_layers_hectares_output,\
	stats_layers_nuts_input, stats_layers_nuts_output,\
	stats_layers_hectares_input, stats_list_nuts_input, stats_list_label_dataset,stats_layer_personnal_layer_input
from app.decorators.restplus import api
from app.decorators.exceptions import HugeRequestException, IntersectionException, NotEnoughPointsException, ParameterException, RequestException
from ..models.user import User

from app.models.statsQueries import ElectricityMix
from app.models.statsQueries import LayersStats
from app.api_v1.upload import Uploads

from app.models.indicators import layersData
import shapely.geometry as shapely_geom

from .. import constants

from app.models import generalData, indicators
from app.models.indicators import HEATDEMAND_FACTOR
from app.helper import find_key_in_dict, getValuesFromName, retrieveCrossIndicator, createAllLayers,\
	getTypeScale, adapt_layers_list, adapt_nuts_list, removeScaleLayers, layers_filter, getTypeScale, get_result_formatted, generate_geotif_name, area_to_geom, \
	write_wkt_csv, generate_csv_name,projection_4326_to_3035
import app
import json
from app.model import check_table_existe, prepare_clip_personal_layer
from app import model
from ..decorators.timeout import return_on_timeout_endpoint




log = logging.getLogger(__name__)

nsStats = api.namespace('stats', description='Operations related to statistics')
ns = nsStats


@ns.route('/layers/nuts-lau')
@api.response(404, 'No data found for that specific list of NUTS.')
@api.response(530, 'Request Error')
@api.response(531, 'Missing parameter.')
class StatsLayersNutsInArea(Resource):
	@return_on_timeout_endpoint()
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
			'layers': output,
			'no_data_layers': noDataLayers,
			'no_table_layers': noDataLayers
		}


@ns.route('/layers/hectares')
@api.response(0, 'Request too big')
@api.response(404, 'No data found for that specific area.')
@api.response(530, 'Request error.')
@api.response(531, 'Missing parameter.')
@api.response(533, 'SQL error.')
#@api.response(534, 'Not enough points error.')
class StatsLayersHectareMulti(Resource):
	@return_on_timeout_endpoint()
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
			'layers': output,
			'no_data_layers': noDataLayers,
			'no_table_layers': noDataLayers
		}







@ns.route('/energy-mix/nuts-lau')
@api.response(0, 'Request too big')
@api.response(404, 'No data found for that specific list of NUTS.')
@api.response(530, 'Request error.')
@api.response(531, 'Missing parameter.')
class StatsLayersNutsInArea(Resource):
	@return_on_timeout_endpoint()
	@api.marshal_with(stats_list_label_dataset)
	@api.expect(stats_list_nuts_input)
	def post(self):
		"""
		Returns the statistics for specific layers, area and year
		:return:
		"""
		# Entries
		wrong_parameter = []
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

@ns.route('/personnal-layers')
class StatsPersonalLayers(Resource):
	@return_on_timeout_endpoint()
	@api.marshal_with(stats_layers_nuts_output)
	@api.expect(stats_layer_personnal_layer_input)
	def post(self):
		noDataLayer=[]
		result=[]
		areas = api.payload['areas']

		# if api.payload['scale_level'] == 'hectare':
		# 	areas = area_to_geom(api.payload['areas'])
		# 	cutline_input = write_wkt_csv(generate_csv_name(constants.UPLOAD_DIRECTORY), areas) # TODO: Projection to 3035 if raster
		# else:
		# 	cutline_input = model.get_shapefile_from_selection(api.payload['scale_level'], areas, constants.UPLOAD_DIRECTORY, '4326')
		for pay in api.payload['layers']:
			values=[]
			data_file_name=''
			token = pay['user_token']
			layer_id = pay['id']
			layer_type = pay['layer_id']
			layer_name = pay['layer_name']
			user = User.verify_auth_token(token)
			upload = Uploads.query.filter_by(id=layer_id).first()

			upload_url = upload.url
			if layer_name.endswith('.tif'):
				cutline_input = model.get_cutline_input(areas, api.payload['scale_level'], 'raster')
				filename_tif = generate_geotif_name(constants.UPLOAD_DIRECTORY)
				args = app.helper.commands_in_array('gdalwarp -dstnodata 0 -cutline {} -crop_to_cutline -of GTiff {} {} -tr 100 100 -co COMPRESS=DEFLATE'.format(cutline_input, upload_url, filename_tif))
				app.helper.run_command(args)
				if os.path.isfile(filename_tif):
					ds = gdal.Open(filename_tif)
					arr = ds.GetRasterBand(1).ReadAsArray()
					df = pd.DataFrame(arr)
				else:
					noDataLayer.append(layer_name)
					continue
				values = self.set_indicators_in_array(df, layer_type)
			elif layer_name.endswith('.csv'):
				cutline_input = model.get_cutline_input(areas, api.payload['scale_level'], 'vector')

				geojson = str(upload_url[:-3]) + 'json'
				if os.path.isfile(geojson):
					# take geojson file instead (csv can not be clip), TODO: this on "prepare_clip_personal_layer" function?
					upload_url = geojson

				cmd_cutline, output_csv = prepare_clip_personal_layer(cutline_input, upload_url)
				app.helper.run_command(app.helper.commands_in_array(cmd_cutline))
				if os.path.isfile(output_csv):
					df = pd.read_csv(output_csv)
					if api.payload['scale_level'] != constants.hectare_name.lower() and 'code' in df:
						# Cannot clip with multipoliygons, TODO: no need to cut the csv with a shapefile for this
						df = df[df['code'].isin(areas)]

					for ind in indicators.layersData[layer_type]['indicators']:
						try:
							value = df[ind['table_column']].sum()
							if 'agg_method' in ind and ind['agg_method'] == 'mean':
								value /= len(areas)

							if 'factor' in ind:  # Decimal * float => rise error
								value = float(value) * float(ind['factor'])

							values.append(get_result_formatted(layer_type+'_'+ind['table_column'], str(value), ind['unit']))
						except:
							noDataLayer.append(layer_name)
				else:
					noDataLayer.append(layer_name)
					continue
			else:
				noDataLayer.append(layer_name)
				continue

			result.append({
				'name': layer_name,
				'values': values
			})

		return {
				'layers': result,
				'no_data_layers': noDataLayer,
				'no_table_layers': noDataLayer
			}

	@staticmethod
	def set_indicators_in_array(df, layer_name):
		values=[]
		# Set result in variables
		df=df[df!=0]
		counted_cells = df.count().sum()
		sum_tif = 0
		min_tif = 0
		max_tif = 0
		density_tif = 0
		if counted_cells != 0:
			sum_tif = df.sum().sum()
			min_tif = df.min().min()
			max_tif = df.max().max()
			density_tif = sum_tif/counted_cells
		#print(max_tif,counted_cells,min_tif,max_tif)
		# Assign indicator to results
		values.append(get_indicators_from_result('sum', layer_name, sum_tif))
		values.append(get_indicators_from_result('count', layer_name, counted_cells))
		values.append(get_indicators_from_result('min', layer_name, min_tif))
		values.append(get_indicators_from_result('max', layer_name, max_tif))
		values.append(get_indicators_from_result('mean', layer_name, density_tif))
		return values


def get_indicators_from_result(id,layer,result):
	filtered_indicators = list(filter(lambda x: 'table_column' in x and x['table_column'] == id, indicators.layersData[layer]['indicators']))
	unit = layer + '_unit_' + id
	value = result
	name = layer + '_' + id
	if len(filtered_indicators)>=1:
		name = layer + '_' + filtered_indicators[0]['indicator_id']
		if 'unit' in filtered_indicators[0]: unit = filtered_indicators[0]['unit']
		if 'factor' in filtered_indicators[0]: value = result*filtered_indicators[0]['factor']
	return get_result_formatted(name,str(value),unit)
	

def get_unit(id, layer):
	filtered_indicators = list(filter(lambda x: 'table_column' in x and x['table_column'] == id,indicators.layersData[layer]['indicators']))
	try:
		return list(filter(lambda x: 'table_column' in x and x['table_column'] == id,indicators.layersData[layer]['indicators']))[0]['unit']
	except IndexError:
		return layer + '_unit_' + id
def get_businness_id(id, layer):
	filtered_indicators = list(filter(lambda x: 'table_column' in x and x['table_column'] == id,indicators.layersData[layer]['indicators']))
	try:
		return layer + '_' + filtered_indicators[0]['indicator_id']
	except IndexError:
		return layer + '_' + id

@celery.task(name = 'energy_mix_nuts_lau')
def processGenerationMix(nuts):
	if not nuts:
		return
	res = ElectricityMix.getEnergyMixNutsLau(adapt_nuts_list(nuts))

	return res
