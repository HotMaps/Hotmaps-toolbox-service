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

class HeatDensityLau:

	@staticmethod
	def aggregate_for_nuts_selection(nuts, year, level): 
		query = db.session.query(
				func.sum(HeatDensityLauModel.sum),
				func.sum(HeatDensityLauModel.sum),
				func.sum(HeatDensityLauModel.count)
			). \
			join(Lau, HeatDensityLauModel.lau). \
			filter(Lau.comm_id.in_(nuts)).first()

		if query == None or len(query) < 3:
				return []
		if query[1] == None:
			return []
		if query[2] == None:
			return []

		average_ha =  Decimal(query[1])/Decimal(query[2])
		return [{
			'name': 'heat_consumption',
			'value': str(query[0] or 0),
			'unit': 'MWh'
		}, {
			'name': 'heat_density',
			'value': str(average_ha or 0),
			'unit': 'MWh/ha'
		}, {
			'name': 'count',
			'value': str(query[2] or 0),
			'unit': 'cell'
		}]

class HeatDensityNuts:

	@staticmethod
	def aggregate_for_nuts_selection(nuts, year, nuts_level):
		"""query = db.session.query(
				func.sum(HeatDensityNuts.sum),
				func.sum(HeatDensityNuts.sum),
				func.sum(HeatDensityNuts.count)
			). \
			join(NutsRG01M, HeatDensityNuts.nuts). \
			filter(HeatDensityNuts.date == datetime.datetime.strptime(str(year), '%Y')). \
			filter(NutsRG01M.stat_levl_ == nuts_level). \
			filter(NutsRG01M.nuts_id.in_(nuts)).first()"""
		query = db.session.query(
				func.sum(HeatDensityNutsModel.sum),
				func.sum(HeatDensityNutsModel.sum),
				func.sum(HeatDensityNutsModel.count)
			). \
			join(NutsRG01M, HeatDensityNutsModel.nuts). \
			filter(NutsRG01M.stat_levl_ == nuts_level). \
			filter(NutsRG01M.nuts_id.in_(nuts)).first()

		if query == None or len(query) < 3:
			return []
		if query[1] == None:
			return []
		if query[2] == None:
			return []



		average_ha =  Decimal(query[1])/Decimal(query[2])

		return [{
			'name': 'heat_consumption',
			'value': str(query[0] or 0),
			'unit': 'MWh'
		},{
			'name': 'heat_density',
			'value': str(average_ha or 0),
			'unit': 'MWh/ha'
		},{
			'name': 'count',
			'value': str(query[2] or 0),
			'unit': 'cell'
		}]

"""
	HeatDensityNuts classes for each nuts/lau level
"""
class HeatDensityLau2():
	@staticmethod
	def aggregate_for_nuts_selection(nuts, year):
		return HeatDensityLau.aggregate_for_nuts_selection(nuts=nuts, year=year, level=2)

class HeatDensityNuts3():
	@staticmethod
	def aggregate_for_nuts_selection(nuts, year):
		return HeatDensityNuts.aggregate_for_nuts_selection(nuts=nuts, year=year, nuts_level=3)

class HeatDensityNuts2():
	@staticmethod
	def aggregate_for_nuts_selection(nuts, year):
		return HeatDensityNuts.aggregate_for_nuts_selection(nuts=nuts, year=year, nuts_level=2)

class HeatDensityNuts1():
	@staticmethod
	def aggregate_for_nuts_selection(nuts, year):
		return HeatDensityNuts.aggregate_for_nuts_selection(nuts=nuts, year=year, nuts_level=1)

class HeatDensityNuts0():
	@staticmethod
	def aggregate_for_nuts_selection(nuts, year):
		return HeatDensityNuts.aggregate_for_nuts_selection(nuts=nuts, year=year, nuts_level=0)

class PopulationDensityLau:
	@staticmethod
	def aggregate_for_nuts_selection(nuts, year, level):
		query = db.session.query(
				func.sum(PopulationDensityLauModel.sum),
				func.sum(PopulationDensityLauModel.sum),
				func.sum(PopulationDensityLauModel.count)
			). \
			join(Lau, PopulationDensityLauModel.lau). \
			filter(Time.year == year). \
			filter(Time.granularity == 'year'). \
			filter(Lau.comm_id.in_(nuts)).first()

		if query == None or len(query) < 3:
				return []
		if query[1] == None:
			return []
		if query[2] == None:
			return []
		average_ha =  Decimal(query[1])/Decimal(query[2])
		return [{
			'name': 'population',
			'value': str(query[0] or 0),
			'unit': 'person'
		}, {
			'name': 'population_density',
			'value': str(average_ha or 0),
			'unit': 'person/ha'
		}, {
			'name': 'count',
			'value': str(query[2] or 0),
			'unit': 'cell'
		}]

class PopulationDensityNuts:
	@staticmethod
	def aggregate_for_nuts_selection(nuts, year, nuts_level):
		query = db.session.query(
			func.sum(PopulationDensityNutsModel.sum),
			func.sum(PopulationDensityNutsModel.sum),
			func.sum(PopulationDensityNutsModel.count)
		). \
			join(NutsRG01M, PopulationDensityNutsModel.nuts). \
			filter(NutsRG01M.stat_levl_ == nuts_level). \
			filter(NutsRG01M.nuts_id.in_(nuts)).first()

		if query == None or len(query) < 3:
				return []
		if query[1] == None:
			return []
		if query[2] == None:
			return []
		average_ha =  Decimal(query[1])/Decimal(query[2])
		return [{
			'name': 'population',
			'value': str(query[0] or 0),
			'unit': 'person'
		}, {
			'name': 'population_density',
			'value': str(average_ha or 0),
			'unit': 'person/ha'
		}, {
			'name': 'count',
			'value': str(query[2] or 0),
			'unit': 'cell'
		}]


"""
	PopulationDensityNuts classes for each nuts/lau level
"""
class PopulationDensityLau2():
	@staticmethod
	def aggregate_for_nuts_selection(nuts, year):
		return PopulationDensityLau.aggregate_for_nuts_selection(nuts=nuts, year=year, level=2)

class PopulationDensityNuts3():
	@staticmethod
	def aggregate_for_nuts_selection(nuts, year):
		return PopulationDensityNuts.aggregate_for_nuts_selection(nuts=nuts, year=year, nuts_level=3)

class PopulationDensityNuts2():
	@staticmethod
	def aggregate_for_nuts_selection(nuts, year):
		return PopulationDensityNuts.aggregate_for_nuts_selection(nuts=nuts, year=year, nuts_level=2)

class PopulationDensityNuts1():
	@staticmethod
	def aggregate_for_nuts_selection(nuts, year):
		return PopulationDensityNuts.aggregate_for_nuts_selection(nuts=nuts, year=year, nuts_level=1)

class PopulationDensityNuts0():
	@staticmethod
	def aggregate_for_nuts_selection(nuts, year):
		return PopulationDensityNuts.aggregate_for_nuts_selection(nuts=nuts, year=year, nuts_level=0)

class Wwtp:
	@staticmethod
	def aggregate_for_nuts_selection(nuts, year, type, level):
		if type == 'lau':
			try:
				# create subquery to get lau geometries inside
				nuts_geom_query = db.session.query(func.ST_Union(Lau.geom).label('nuts_geom')). \
					filter(Lau.comm_id.in_(nuts)). \
					subquery('nuts_geom_query')
			except KeyError:
				return []
		elif type  == 'nuts':
			try:
				# create subquery to get nuts geometries inside
				nuts_geom_query = db.session.query(func.ST_Union(Nuts.geom).label('nuts_geom')). \
					filter(Nuts.stat_levl_ == level). \
					filter(Nuts.nuts_id.in_(nuts)). \
					subquery('nuts_geom_query')
			except KeyError:
				return []
		else:
			return []

		query = db.session.query(func.sum(WwtpModel.power), func.sum(WwtpModel.capacity), WwtpModel.unit). \
			filter(WwtpModel.date == datetime.datetime.strptime(str(year), '%Y')). \
			filter(func.ST_Within(WwtpModel.geom, func.ST_Transform(nuts_geom_query.c.nuts_geom, WwtpModel.CRS))). \
			group_by(WwtpModel.unit).first()

		if query == None or len(query) < 3:
			return []

		return [{
			'name': 'power',
			'value': str(query[0] or 0),
			'unit': str(query[2])
		}, {
			'name': 'capacity',
			'value': str(query[1] or 0),
			'unit': 'Person equivalent'
		}]

"""
	WwtpNuts classes for each nuts/lau level
"""
class WwtpLau2():
	@staticmethod
	def aggregate_for_nuts_selection(nuts, year):
		return Wwtp.aggregate_for_nuts_selection(nuts=nuts, year=year, type='lau', level=2)

class WwtpNuts3():
	@staticmethod
	def aggregate_for_nuts_selection(nuts, year):
		return Wwtp.aggregate_for_nuts_selection(nuts=nuts, year=year, type='nuts', level=3)

class WwtpNuts2():
	@staticmethod
	def aggregate_for_nuts_selection(nuts, year):
		return Wwtp.aggregate_for_nuts_selection(nuts=nuts, year=year, type='nuts', level=2)

class WwtpNuts1():
	@staticmethod
	def aggregate_for_nuts_selection(nuts, year):
		return Wwtp.aggregate_for_nuts_selection(nuts=nuts, year=year, type='nuts', level=1)

class WwtpNuts0():
	@staticmethod
	def aggregate_for_nuts_selection(nuts, year):
		return Wwtp.aggregate_for_nuts_selection(nuts=nuts, year=year, type='nuts', level=0)


class LayersHectare:

	@staticmethod
	def stats_hectares(geometry, year, layers): #/stats/layers/hectares

		# Get the data
		layersQueryData = generalData.createQueryDataStatsHectares(geometry=geometry, year=year)
		layersData = generalData.layersData

		# Get the number of layers
		#layers = sorted(layers)
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

			# Storing the results
			
			if query == None or len(query) < 2:
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

		