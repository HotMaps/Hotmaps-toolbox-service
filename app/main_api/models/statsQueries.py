import datetime
from main_api.models import db
from main_api import settings
from sqlalchemy import func
from decimal import *

from main_api.models.wwtp import WwtpModel
from main_api.models.heat_density_map import HeatDensityMapModel, HeatDensityHaModel, HeatDensityLauModel, HeatDensityNutsModel
from main_api.models.population_density import PopulationDensityHaModel, PopulationDensityLauModel, PopulationDensityNutsModel
from main_api.models.nuts import Nuts, NutsRG01M
from main_api.models.lau import Lau
import generalData

#import logging
#logging.basicConfig()
#logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


class LayersNutsLau: 
	@staticmethod
	def stats_nuts_lau(nuts, year, layers, type): #/stats/layers/hectares

		# Get the data
		layersQueryData = generalData.createQueryDataStatsNutsLau(nuts=nuts, year=year, type=type)
		layersData = generalData.layersData
		
		# Get the number of layers
		nbLayers = len(layers)

		result = []

		# Check if there is at least one layer
		if layers:
			# Construction of the query 
			sql_query = 'WITH '

			for c, layer in enumerate(layers):
				sql_query += layersQueryData[layer]['with']
				# Add a comma when the query needs one	
				if nbLayers > 1 and c < nbLayers-1:
					sql_query += ', '

			sql_query += 'SELECT '

			for c, layer in enumerate(layers):
				sql_query += layersQueryData[layer]['select']
				# Add a comma when the query needs one
				if nbLayers > 1 and c < nbLayers-1:
					sql_query += ', '

			sql_query += 'FROM '

			for c, layer in enumerate(layers):
				sql_query += layersQueryData[layer]['from']
				# Add a comma when the query needs one
				if nbLayers > 1 and c < nbLayers-1:
					sql_query += ', '	
				
			sql_query += ';'
			print(sql_query)

			# Execution of the query
			query = db.session.execute(sql_query).first()

			# Storing the results only if there is data			
			if query[0] == None:
				result = []
			else:
				for layer in layers:
					values = []
					for c, l in enumerate(layersData[layer]['resultsName']):
						values.append({
								'name':layersData[layer]['resultsName'][c],
								'value':str(query[layersData[layer]['resultsName'][c]]),
								'unit':layersData[layer]['resultsUnit'][c]
							})

					result.append({
							'name':layer,
							'values':values
						})
		
		return result

class LayersHectare:

	@staticmethod
	def stats_hectares(geometry, year, layers): #/stats/layers/hectares

		# Get the data
		layersQueryData = generalData.createQueryDataStatsHectares(geometry=geometry, year=year)
		layersData = generalData.layersData

		# Get the number of layers
		nbLayers = len(layers)

		result = []

		# Check if there is at least one layer
		if layers:
			# Construction of the query 
			sql_query = 'WITH '

			for c, layer in enumerate(layers):
				sql_query += layersQueryData[layer]['with']
				# Add a comma when the query needs one	
				if nbLayers > 1 and c < nbLayers-1:
					sql_query += ', '

			sql_query += 'SELECT '

			for c, layer in enumerate(layers):
				sql_query += layersQueryData[layer]['select']
				# Add a comma when the query needs one
				if nbLayers > 1 and c < nbLayers-1:
					sql_query += ', '

			sql_query += 'FROM '

			for c, layer in enumerate(layers):
				sql_query += layersQueryData[layer]['from']
				# Add a comma when the query needs one
				if nbLayers > 1 and c < nbLayers-1:
					sql_query += ', '	
				
			sql_query += ';'

			# Execution of the query
			query = db.session.execute(sql_query).first()

			# Storing the results only if there is data
			if query[0] == None:
				result = []
			else:
				for layer in layers:
					values = []
					for c, l in enumerate(layersData[layer]['resultsName']):
						values.append({
								'name':layersData[layer]['resultsName'][c],
								'value':str(query[layersData[layer]['resultsName'][c]]),
								'unit':layersData[layer]['resultsUnit'][c]
							})

					result.append({
							'name':layer,
							'values':values
						})

		
		return result

		