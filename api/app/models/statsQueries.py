import datetime
from .. import helper
from app import dbGIS as db
from app import constants
from decimal import *

from app import celery
from . import generalData
from app import model

import logging
log = logging.getLogger(__name__)

class LayersStats:

	
	@staticmethod
	def get_stats(year, layers, layersQueryData, isHectare=False):
		# Get the number of layers
		nbLayers = len(layers)

		result = []

		# Check if there is at least one layer
		if layers:
			# Construction of the query 
			sql_query = ''
			sql_with = ' WITH '
			sql_select = ' SELECT '
			sql_from = ' FROM '
			for c, layer in enumerate(layersQueryData):
				sql_with += layersQueryData[layer]['with']					
				for indicator in layersQueryData[layer]['indicators']:
					if 'select' in indicator:
						sql_select += layer+indicator['name']+','
					else:
						sql_select+= indicator['val1']+' '+indicator['operator']+' '+indicator['val2']+','
				sql_from += layersQueryData[layer]['from_indicator_name']
				if nbLayers > 1 and c < nbLayers-1:
					sql_with += ', '
					sql_from += ', '
			sql_select = sql_select[:-1]
			sql_query = sql_with + sql_select + sql_from + ';'
			print(sql_query)
			query_geographic_database_first = model.query_geographic_database_first(sql_query)

			# Storing the results only if there is data
			count_indic=0
			for layer in layersQueryData:
				values = []
				for indicator in layersQueryData[layer]['indicators']:
					currentValue = query_geographic_database_first[count_indic]
					count_indic += 1

					if currentValue == None:
						currentValue = 0


					try:
						values.append({
							'name':layer +'_'+indicator['name'],
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
	
	@staticmethod
	#@celery.task(name = 'stats_hectares')
	def stats_hectares(geometry, year, layers): #/stats/layers/hectares
		# Get the data
		layersQueryData = {}
		for layer in layers:
			layersQueryData[layer] = generalData.createQueryDataStatsHectares(layer=layer,geometry=geometry, year=year)
			
		return LayersStats.get_stats(year,layers, layersQueryData,isHectare=True)

	@staticmethod
	@celery.task(name = 'stats_nuts_lau')
	def stats_nuts_lau(nuts, year, layers, type): #/stats/layers/nuts-lau
		# Get the data
		layersQueryData = {}
		for layer in layers:
			layersQueryData[layer] = generalData.createQueryDataStatsNutsLau(layer=layer, nuts=nuts, year=year, type=type)
		return LayersStats.get_stats(year,layers, layersQueryData)


class ElectricityMix:

	@staticmethod

	def getEnergyMixNutsLau(nuts):

		sql_query = "WITH energy_total as (SELECT sum(electricity_generation) as value FROM " + constants.ELECRICITY_MIX + " WHERE nuts0_code IN ("+nuts+") )" + \
					"SELECT DISTINCT energy_carrier, SUM(electricity_generation * 100 /energy_total.value)  FROM " + constants.ELECRICITY_MIX + " ,energy_total WHERE nuts0_code IN ("+nuts+")  GROUP BY energy_carrier ORDER BY energy_carrier ASC" ;



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

