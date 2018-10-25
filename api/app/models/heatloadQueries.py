import datetime, logging
from app import constants
from app import dbGIS as db
from app import model
from . import generalData
from app import celery
#logging.basicConfig()
#logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

class HeatLoadProfile:
	@staticmethod
	@celery.task(name = 'heatloadprofile_nuts_lau')
	def heatloadprofile_nuts_lau(year, month, day, nuts): #/heat-load-profile/nuts-lau

		# Check the type of the query
		if month != 0 and day != 0:
			by = 'byDay'
		elif month != 0:
			by = 'byMonth'
		else:
			by = 'byYear'

		# Get the data
		queryData = generalData.createQueryDataLPNutsLau(year=year, month=month, day=day, nuts=nuts)

		# Construction of the query
		sql_query = queryData[by]['with'] + queryData[by]['time'] + queryData[by]['from'] + queryData[by]['select']

		# Execution of the query
		#query = db.session.execute(sql_query)

		query = model.query_geographic_database(sql_query)

		# Storing the results only if there is data
		output = []
		if by == 'byYear':
			for c, q in enumerate(query):
				if q[0]:
					output.append({
						'year': year,
						'month': q[3],
						'granularity': 'month',
						'unit': 'kW',
						'min': round(q[0], constants.NUMBER_DECIMAL_DATA),
						'max': round(q[1], constants.NUMBER_DECIMAL_DATA),
						'average': round(q[2], constants.NUMBER_DECIMAL_DATA)
						})
				else:
					output = []
		elif by == 'byMonth':
			for c, q in enumerate(query):
				if q[0]:
					output.append({
						'year': year,
						'month': month,
						'day': q[3],
						'granularity': 'day',
						'unit': 'kW',
						'min': round(q[0], constants.NUMBER_DECIMAL_DATA),
						'max': round(q[1], constants.NUMBER_DECIMAL_DATA),
						'average': round(q[2], constants.NUMBER_DECIMAL_DATA)
						})
				else:
					output = []
		else:
			for c, q in enumerate(query):
				if q[0]:
					output.append({
						'year': year,
						'month': month,
						'day': day,
						'hour_of_day': q[1],
						'granularity': 'hour',
						'unit': 'kW',
						'value': round(q[0], constants.NUMBER_DECIMAL_DATA)
						})
				else:
					output = []
		
		return {
			"values": output
		}


	@staticmethod
	@celery.task(name = 'heatloadprofile_hectares')
	def heatloadprofile_hectares(year, month, day, geometry): #/heat-load-profile/hectares

		# Check the type of the query
		if month != 0 and day != 0:
			by = 'byDay'
		elif month != 0:
			by = 'byMonth'
		else:
			by = 'byYear'
		
		# Get the data
		queryData = generalData.createQueryDataLPHectares(year=year, month=month, day=day, geometry=geometry)

		# Construction of the query
		sql_query = queryData[by]['with'] + queryData[by]['select']

		# Execution of the query
		#query = db.session.execute(sql_query)
		query = model.query_geographic_database(sql_query)

		# Storing the results only if there is data
		output = []
		if by == 'byYear':
			for c, q in enumerate(query):
				if q[0]:					
					output.append({
						'year': year,
						'month': q[3],
						'granularity': 'month',
						'unit': 'kW',
						'min': round(q[0], constants.NUMBER_DECIMAL_DATA),
						'max': round(q[1], constants.NUMBER_DECIMAL_DATA),
						'average': round(q[2], constants.NUMBER_DECIMAL_DATA)
						})
				else:
					output = []
		elif by == 'byMonth':
			for c, q in enumerate(query):
				if q[0]:
					output.append({
						'year': year,
						'month': month,
						'day': q[3],
						'granularity': 'day',
						'unit': 'kW',
						'min': round(q[0], constants.NUMBER_DECIMAL_DATA),
						'max': round(q[1], constants.NUMBER_DECIMAL_DATA),
						'average': round(q[2], constants.NUMBER_DECIMAL_DATA)
						})
				else:
					output = []
		else:
			for c, q in enumerate(query):
				if q[0]:
					output.append({
						'year': year,
						'month': month,
						'day': day,
						'hour_of_day': q[1],
						'granularity': 'hour',
						'unit': 'kW',
						'value': round(q[0], constants.NUMBER_DECIMAL_DATA)
						})
				else:
					output = []
		
		return {
			"values": output
		}

	@staticmethod
	def duration_curve_nuts_lau(year, nuts): #/heat-load-profile/duration-curve/nuts-lau

		# Get the query
		sql_query = generalData.createQueryDataDCNutsLau(year=year, nuts=nuts)

		# Execution of the query
		#query = db.session.execute(sql_query)

		query = model.query_geographic_database(sql_query)


		# Store query results in a list
		listAllValues = []
		for q in query:

			listAllValues.append(q[0])



		# Creation of points and sampling of the values only if there is data
		if listAllValues:
			finalListPoints = generalData.sampling_data(listAllValues)
		else:
			finalListPoints = []


		return finalListPoints

	@staticmethod
	def duration_curve_hectares(year, geometry): #/heat-load-profile/duration-curve/hectares

		# Get the query
		sql_query = generalData.createQueryDataDCHectares(year=year, geometry=geometry)

		# Execution of the query
		#query = db.session.execute(sql_query)
		query = model.query_geographic_database(sql_query)
		# Store query results in a list
		listAllValues = []
		for q in query:
			listAllValues.append(q[0])

		# Creation of points and sampling of the values only if there is data
		if listAllValues:
			finalListPoints = generalData.sampling_data(listAllValues)
		else:
			finalListPoints = []		

		return finalListPoints

