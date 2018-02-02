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
		wwtpHa = 'wwtp'

		result = []

		layersData = [['population', 'population_density', 'count', 'person', 'person/ha', 'cell', 
						PopulationDensityHa.__tablename__, PopulationDensityHa.__table_args__],
					['heat_consumption', 'heat_density', 'count', 'MWh', 'MWh/ha', 'cell', 
						HeatDensityHa.__tablename__, HeatDensityHa.__table_args__],
					['power', 'capacity', '', '', 'Person equivalent', '', 
						Wwtp.__tablename__, Wwtp.__table_args__]
				]

		for layer in layers:
			if layer == popDeHa or layer == heatDeHa:
				# get the level for the array
				if layer == popDeHa:
					n = 0;
				else:
					n = 1;

				# Custom query (multi selection)
				sql_query = \
					'WITH stat_pop AS (SELECT ('+ \
					'	((ST_SummaryStatsAgg('+ \
					'		ST_Clip('+ layersData[n][6] + '.rast, 1, '+ \
					'			st_transform(st_geomfromtext(\'' + \
									geometry + '\'::text,4326),' + str(LayersHectare.CRS) + '),false),true,0))).*) as stats ' + \
					'FROM' + \
					'	geo.' + layersData[n][6]  + \
					' WHERE' + \
					'	ST_Intersects('+ layersData[n][6] + '.rast,' + \
					'		st_transform(st_geomfromtext(\''+ geometry +'\'::text,4326),' + str(LayersHectare.CRS) + ')) ' 

				if layer == popDeHa:	
					sql_query += \
					'AND date = to_date(\''+ str(year) +'\',\'YYYY\')'
				
				sql_query += \
					') select' + \
					'	sum as population, (sum/count) as population_density, count as count_cell ' + \
					'FROM stat_pop' + \
					';'
				
				query = db.session.execute(sql_query).first()

				if query == None or len(query) < 3:
					result = []
				else:
					result.append({
						'name':layer,
						'values':[{
							'name': layersData[n][0],
							'value': str(query[0] or 0),
							'unit': layersData[n][3]
						},{
							'name': layersData[n][1],
							'value': str(query[1] or 0),
							'unit': layersData[n][4]
						},{
							'name': layersData[n][2],
							'value': str(query[2] or 0),
							'unit': layersData[n][5]
						}]
					})

			if layer == wwtpHa:
				n = 2;

				geometry = "SRID=4326;{}".format(geometry)

				query = db.session.query(func.sum(Wwtp.power), func.sum(Wwtp.capacity), Wwtp.unit). \
					filter(Wwtp.date == datetime.datetime.strptime(str(year), '%Y')). \
					filter(func.ST_Within(Wwtp.geom, func.ST_Transform(func.ST_GeomFromEWKT(geometry), Wwtp.CRS))). \
					group_by(Wwtp.unit).first()

				if query == None or len(query) < 3:
					result = []
				else:
					result.append({
						'name':layer,
						'values':[{
							'name': layersData[n][0],
							'value': str(query[0] or 0),
							'unit': str(query[2])
						}, {
							'name': layersData[n][1],
							'value': str(query[1] or 0),
							'unit': layersData[n][4]
						}]
					})


		return result