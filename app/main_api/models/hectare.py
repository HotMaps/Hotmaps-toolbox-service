import datetime
from main_api.models import db
from sqlalchemy import func

from main_api.models.wwtp import Wwtp
from main_api.models.heat_density_map import HeatDensityHa
from main_api.models.population_density import PopulationDensityHa

class LayersHectare():

	CRS = 3035

	@staticmethod
	def aggregate_for_selection(geometry, year, layers):
		popDeHa = 'population_density_ha'
		heatDeHa = 'heat_density_ha'
		wwtpHa = 'wwtp_ha'

		result = []

		# ALL DATA FOR LAYERS
		layersData = {
			heatDeHa:{'tablename':HeatDensityHa.__tablename__,
					'resultsType':1,
					'resultsName':{
						0:'heat_consumption', 1:'heat_density', 2:'count_cell_heat'},
					'resultsUnit':{
						0:'MWh', 1:'MWh/ha', 2:'cell'}
					},
			popDeHa:{'tablename':PopulationDensityHa.__tablename__,
					'resultsType':1,
					'resultsName':{
						0:'population', 1:'population_density', 2:'count_cell_pop'},
					'resultsUnit':{ 
						0:'person', 1:'person/ha', 2:'cell'}
					},
			wwtpHa:{'tablename':Wwtp.__tablename__,
					'resultsType':2,
					'resultsName':{
						0:'power', 1:'capacity'},
					'resultsUnit':{
						0:'kW', 1:'Person equivalent'}
					}
		}

		# ALL DATA FOR QUERY
		# 'with' parts
		withPop = 'stat_pop AS ( SELECT (' + \
			'	((ST_SummaryStatsAgg(' + \
			'		ST_Clip('+ layersData[popDeHa]['tablename'] + '.rast, 1, ' + \
			'			st_transform(st_geomfromtext(\'' + \
							geometry + '\'::text,4326),' + str(LayersHectare.CRS) + '),false),true,0))).*) as stats ' + \
			'FROM' + \
			'	geo.'+ layersData[popDeHa]['tablename'] + \
			' WHERE' + \
			'	ST_Intersects('+ layersData[popDeHa]['tablename'] + '.rast,' + \
			'		st_transform(st_geomfromtext(\''+ geometry +'\'::text,4326),' + str(LayersHectare.CRS) + ')) ' + \
			'AND date = to_date(\''+ str(year) +'\',\'YYYY\')) '

		withHeat = ' stat_heat AS ( SELECT (' + \
			'		((ST_SummaryStatsAgg(ST_Clip('+ layersData[heatDeHa]['tablename'] + '.rast, 1, ' + \
			'			st_transform(st_geomfromtext(\''+ \
							geometry +'\'::text,4326),' + str(LayersHectare.CRS) + '),false),true,0))).*) as stats ' + \
			'FROM' + \
			'	geo.'+ layersData[heatDeHa]['tablename'] + \
			' WHERE' + \
			'	ST_Intersects('+ layersData[heatDeHa]['tablename'] + '.rast,' + \
			'		st_transform(st_geomfromtext(\''+ geometry +'\'::text,4326),' + str(LayersHectare.CRS) + ')) ' + \
			'AND date = to_date(\''+ str(year) +'\',\'YYYY\')) '

		withWwtp = ' stat_wwtp AS (SELECT ' + \
			'		count(*) as nbWwtp, sum(capacity) as capacityPerson, sum(power) as power ' + \
			'FROM' + \
			'	geo.'+ layersData[wwtpHa]['tablename'] + ' tbl_wwtp' + \
			' WHERE' + \
			'	ST_Within(tbl_wwtp.geom,st_transform(st_geomfromtext(\''+ geometry +'\'::text,4326),' + str(LayersHectare.CRS) + ')) ' + \
			'AND date = to_date(\''+ str(year) +'\',\'YYYY\')) '

		# 'select' parts
		selectPop = 'stat_pop.sum as population, (stat_pop.sum/stat_pop.count) as population_density, stat_pop.count as count_cell_pop '
		selectHeat = 'stat_heat.sum as heat_consumption, (stat_heat.sum/stat_heat.count) as heat_density, stat_heat.count as count_cell_heat '
		selectWwtp = 'stat_wwtp.capacityPerson as capacity, stat_wwtp.power as power '

		# 'from' parts
		fromPop = 'stat_pop'
		fromHeat = 'stat_heat'
		fromWwtp = 'stat_wwtp'

		# Dictionary with query data
		layersQueryData = {heatDeHa:{'with':withHeat, 'select':selectHeat, 'from':fromHeat},
							popDeHa:{'with':withPop, 'select':selectPop, 'from':fromPop},
							wwtpHa:{'with':withWwtp, 'select':selectWwtp, 'from':fromWwtp}}

		# Sort the layers list and get the number of layers
		#layers = sorted(layers)
		nbLayers = len(layers)

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

		