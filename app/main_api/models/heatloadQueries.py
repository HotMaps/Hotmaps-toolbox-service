import datetime, logging
from main_api import settings
from main_api.models import db

import generalData

#logging.basicConfig()
#logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

class HeatLoadProfile:
	@staticmethod
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
		query = db.session.execute(sql_query)

		# Storing the results
		output = []
		if by == 'byYear':
			for c, q in enumerate(query):
				output.append({
					'year': year,
					'month': q[3],
					'granularity': 'month',
					'unit': 'kW',
					'min': round(q[0], settings.NUMBER_DECIMAL_DATA),
					'max': round(q[1], settings.NUMBER_DECIMAL_DATA),
					'average': round(q[2], settings.NUMBER_DECIMAL_DATA)
					})
		elif by == 'byMonth':
			for c, q in enumerate(query):
				output.append({
					'year': year,
					'month': month,
					'day': q[3],
					'granularity': 'day',
					'unit': 'kW',
					'min': round(q[0], settings.NUMBER_DECIMAL_DATA),
					'max': round(q[1], settings.NUMBER_DECIMAL_DATA),
					'average': round(q[2], settings.NUMBER_DECIMAL_DATA)
					})
		else:
			for c, q in enumerate(query):
				output.append({
					'year': year,
					'month': month,
					'day': day,
					'hour_of_day': q[1],
					'granularity': 'hour',
					'unit': 'kW',
					'value': round(q[0], settings.NUMBER_DECIMAL_DATA)
					})
		
		return {
			"values": output
		}


	@staticmethod
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
		query = db.session.execute(sql_query)

		# Storing the results
		output = []
		if by == 'byYear':
			for c, q in enumerate(query):
				output.append({
					'year': year,
					'month': q[3],
					'granularity': 'month',
					'unit': 'kW',
					'min': round(q[0], settings.NUMBER_DECIMAL_DATA),
					'max': round(q[1], settings.NUMBER_DECIMAL_DATA),
					'average': round(q[2], settings.NUMBER_DECIMAL_DATA)
					})
		elif by == 'byMonth':
			for c, q in enumerate(query):
				output.append({
					'year': year,
					'month': month,
					'day': q[3],
					'granularity': 'day',
					'unit': 'kW',
					'min': round(q[0], settings.NUMBER_DECIMAL_DATA),
					'max': round(q[1], settings.NUMBER_DECIMAL_DATA),
					'average': round(q[2], settings.NUMBER_DECIMAL_DATA)
					})
		else:
			for c, q in enumerate(query):
				output.append({
					'year': year,
					'month': month,
					'day': day,
					'hour_of_day': q[1],
					'granularity': 'hour',
					'unit': 'kW',
					'value': round(q[0], settings.NUMBER_DECIMAL_DATA)
					})

		
		return {
			"values": output
		}

	@staticmethod
	def duration_curve_nuts_lau(year, nuts): #/heat-load-profile/duration-curve/nuts-lau

		# Get the query
		sql_query = generalData.createQueryDataDCNutsLau(year=year, nuts=nuts)

		# Execution of the query
		query = db.session.execute(sql_query)

		# Store query results in a list
		listAllValues = []
		for q in query:
			listAllValues.append(q[0])

		# Creation of points and sampling of the values
		finalListPoints = generalData.sampling_data(listAllValues)

		return finalListPoints

	@staticmethod
	def duration_curve_hectares(year, geometry): #/heat-load-profile/duration-curve/hectares

		# Get the query
		sql_query = generalData.createQueryDataDCHectares(year=year, geometry=geometry)

		# Execution of the query
		query = db.session.execute(sql_query)

		# Store query results in a list
		listAllValues = []
		for q in query:
			listAllValues.append(q[0])

		# Creation of points and sampling of the values
		finalListPoints = generalData.sampling_data(listAllValues)

		return finalListPoints

