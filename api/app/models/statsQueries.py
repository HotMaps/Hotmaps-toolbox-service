import datetime
from .. import helper
from app import dbGIS as db
from app import constants
from decimal import *
from app.models.indicators import layersData, ELECRICITY_MIX
from app import celery
from . import generalData
from app import model

import logging
log = logging.getLogger(__name__)

class LayersStats:

	@staticmethod
	def run_stat(payload):
		
		year = payload['year']
		print ('year ',year)
		layersPayload = payload['layers']
		print ('layersPayload ',layersPayload)
		scale_level = payload['scale_level']
		print ('scale_level ',scale_level)

		#must sanitize this

		selection_areas = ''
		is_hectare = False
		noDataLayers=[]
		layers=[]
		output=[]

		if scale_level in constants.NUTS_LAU_VALUES:
			selection_areas = payload['nuts']

		elif scale_level == constants.hectare_name:
			selection_areas = payload['areas']
			geom = helper.areas_to_geom(selection_areas)
			is_hectare=True

		for c, layer in enumerate(layersPayload):
			if layersPayload[c] in layersData:
				layers.append(layersPayload[c])
			else: 
				noDataLayers.append(layersPayload[c])

		
		if is_hectare:
			output = LayersStats.get_stats(selection_areas=geom, year=year, layers=layers,scale_level=scale_level, is_hectare=is_hectare)
		else:
			nuts = ''.join("'"+str(nu)+"'," for nu in selection_areas)[:-1]
			output = LayersStats.get_stats(selection_areas=nuts, year=year, layers=layers, scale_level=scale_level, is_hectare=False)

		return output, noDataLayers

	@staticmethod
	def get_stats(year, layers, selection_areas, is_hectare, scale_level):
		# Get the number of layers
		result = []
		# Check if there is at least one layer
		if layers:
			# Construction of the query 
			sql_query = ''
			sql_with = ' WITH '
			sql_select = ' SELECT '
			sql_from = ' FROM '
			for layer in layers:

				if len(layersData[layer]['indicators']) != 0 and scale_level in layersData[layer]['data_lvl']:
					if is_hectare:
						sql_with += generalData.constructWithPartEachLayerHectare(geometry=selection_areas, year=year, layer=layer, scale_level=scale_level) + ','
					else:
						sql_with += generalData.constructWithPartEachLayerNutsLau(layer=layer, nuts=selection_areas, year=year, scale_level=scale_level) + ','

					for indicator in layersData[layer]['indicators']:
						if 'table_column' in indicator:
							sql_select += layer+indicator['indicator_id']+','
						elif indicator['reference_tablename_indicator_id_1'] in layers and indicator['reference_tablename_indicator_id_2'] in layers:
								sql_select+= indicator['reference_tablename_indicator_id_1']+indicator['reference_indicator_id_1']+' '+indicator['operator']+' '+indicator['reference_tablename_indicator_id_2']+indicator['reference_indicator_id_2']+','
					sql_from += layersData[layer]['from_indicator_name']+','

			
			
			# Combine string to a single query
			sql_with = sql_with[:-1]
			sql_select = sql_select[:-1]
			sql_from = sql_from[:-1]
			sql_query = sql_with + sql_select + sql_from + ';'

			
			# Run the query
			query_geographic_database_first = model.query_geographic_database_first(sql_query)

			# Storing the results only if there is data
			count_indic=0
			for layer in layers:
				values = []
				for indicator in layersData[layer]['indicators']:
					if ('table_column' not in indicator and (indicator['reference_tablename_indicator_id_1'] not in layers or indicator['reference_tablename_indicator_id_2'] not in layers)) or scale_level not in layersData[layer]['data_lvl']:
						continue
					currentValue = query_geographic_database_first[count_indic]
					count_indic += 1

					if currentValue == None:
						currentValue = 0


					if 'factor' in indicator:
						currentValue = float(currentValue)* float(indicator['factor'])


					try:
						values.append({
							'name':layer +'_'+indicator['indicator_id'],
							'value':currentValue,
							'unit':indicator['unit']
						})
					except KeyError: # Special case we retrieve only one value for an hectare
						pass
				result.append({
					'name':layer,
					'values':values
				})

		return result


class ElectricityMix:

	@staticmethod

	def getEnergyMixNutsLau(nuts):

		sql_query = "WITH energy_total as (SELECT sum(electricity_generation) as value FROM " + ELECRICITY_MIX + " WHERE nuts0_code IN ("+nuts+") )" + \
					"SELECT DISTINCT energy_carrier, SUM(electricity_generation * 100 /energy_total.value)  FROM " + ELECRICITY_MIX + " ,energy_total WHERE nuts0_code IN ("+nuts+")  GROUP BY energy_carrier ORDER BY energy_carrier ASC" ;



		query = model.query_geographic_database(sql_query)

		labels = []
		data = []
		backgroundColor = []

		for c, l in enumerate(query):

			labels.append(l[0])
			data.append(helper.roundValue(l[1]))
			backgroundColor.append(helper.getGenerationMixColor(l[0]))
		datasets = {
			'data' : data,
			'label': '%',
			'backgroundColor': backgroundColor
		}

		result = {
			'labels':labels,
			'datasets':datasets
		}
		return result

