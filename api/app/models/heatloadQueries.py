import datetime, logging
from app import constants
from app import dbGIS as db
from app import model
from . import generalData
from app import celery
from .. import helper
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
		queryData = createQueryDataLPNutsLau(year=year, month=month, day=day, nuts=nuts)

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
		queryData = createQueryDataLPHectares(year=year, month=month, day=day, geometry=geometry)

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
		sql_query = createQueryDataDCNutsLau(year=year, nuts=nuts)

		# Execution of the query
		#query = db.session.execute(sql_query)

		query = model.query_geographic_database(sql_query)


		# Store query results in a list
		listAllValues = []
		for q in query:

			listAllValues.append(q[0])



		# Creation of points and sampling of the values only if there is data
		if listAllValues:
			finalListPoints = helper.sampling_data(listAllValues)
		else:
			finalListPoints = []


		return finalListPoints

	@staticmethod
	def duration_curve_hectares(year, geometry): #/heat-load-profile/duration-curve/hectares

		# Get the query
		sql_query = createQueryDataDCHectares(year=year, geometry=geometry)
		print(sql_query)
		# Execution of the query
		#query = db.session.execute(sql_query)
		query = model.query_geographic_database(sql_query)
		# Store query results in a list
		listAllValues = []
		for q in query:
			listAllValues.append(q[0])

		# Creation of points and sampling of the values only if there is data
		if listAllValues:
			finalListPoints = helper.sampling_data(listAllValues)
		else:
			finalListPoints = []		

		return finalListPoints

def createQueryDataLPHectares(year, month, day, geometry):
	withPart = "with subAreas as (SELECT ST_Intersection(ST_Transform(ST_GeomFromText(\'" + geometry +"\',4326),4258),nuts.geom) as soustracteGeom, " +\
						"nuts.gid " +\
						"FROM geo.nuts " +\
						"where ST_Intersects(nuts.geom,ST_Transform(ST_GeomFromText(\'" + geometry +"\',4326),4258)) " + \
						"AND STAT_LEVL_=2), " +\
					"statBySubAreas as (SELECT (ST_SummaryStatsAgg(ST_Clip(heat_tot_curr_density_tif.rast,1, " +\
						"ST_Transform(subAreas.soustracteGeom,3035),0,true),1,true)).* as stat, subAreas.gid " +\
						"FROM subAreas, geo.heat_tot_curr_density_tif " +\
						"WHERE ST_Intersects(heat_tot_curr_density_tif.rast,ST_Transform(subAreas.soustracteGeom,3035)) group by subAreas.gid), " +\
					"statLoadProfilBySubarea as (select stat.load_profile.nuts_id as load_profile_nutsid, stat.load_profile.value as val_load_profile, " +\
						"stat.time.month as month_of_year, " +\
						"stat.time.hour_of_year as hour_of_year, " +\
						"stat.time.day as day_of_month, " +\
						"stat.time.hour_of_day as hour_of_day, " +\
						"statBySubAreas.count as statCount, statBySubAreas.sum as statSum_HD " +\
						"from stat.load_profile " +\
						"left join statBySubAreas on statBySubAreas.gid = stat.load_profile.fk_nuts_gid " +\
						"inner join stat.time on stat.load_profile.fk_time_id = stat.time.id " +\
						"WHERE fk_nuts_gid is not null and fk_time_id is not null " +\
						"AND statBySubAreas.gid = stat.load_profile.fk_nuts_gid AND stat.time.year = " + str(year) + " " +\
						"order by stat.time.hour_of_year), " +\
					"totalLoadprofile as ( " +\
						"select sum(val_load_profile) as tot_load_profile,load_profile_nutsid " +\
						"from statLoadProfilBySubarea group by load_profile_nutsid), " +\
					"normalizedData as (select sum(val_load_profile/tot_load_profile*statSum_HD) as normalizedCalutation, " +\
						"hour_of_year, month_of_year, day_of_month, hour_of_day " +\
						"from statLoadProfilBySubarea " +\
						"inner join totalLoadprofile on statLoadProfilBySubarea.load_profile_nutsid = totalLoadprofile.load_profile_nutsid " +\
						"group by hour_of_year, month_of_year, hour_of_day, day_of_month " +\
						"order by hour_of_year) " +\
					"select "

	selectYear = "min(normalizedCalutation), max(normalizedCalutation), avg(normalizedCalutation), month_of_year " +\
					"from normalizedData " +\
					"group by month_of_year " +\
					"order by month_of_year"
	selectMonth = "min(normalizedCalutation), max(normalizedCalutation), avg(normalizedCalutation), day_of_month " +\
					"from normalizedData " +\
					"where month_of_year = " + str(month) + " " +\
					"group by day_of_month, month_of_year " +\
					"order by day_of_month"
	selectDay = "normalizedCalutation, hour_of_day " +\
					"from normalizedData " +\
					"where day_of_month = " + str(day) + " " +\
					"and month_of_year = " + str(month) + " " +\
					"group by normalizedCalutation, hour_of_day " +\
					"order by hour_of_day"

	# Dictionary with query data
	queryData = {'byYear':{'with':withPart, 'select':selectYear},
					'byMonth':{'with':withPart, 'select':selectMonth},
					'byDay':{'with':withPart, 'select':selectDay}}

	return queryData

# ALL QUERIES DATA FOR THE HEAT LOAD PROFILE BY NUTS
def createQueryDataLPNutsLau(year, month, day, nuts):

	withPart = "WITH nutsSelection as (select nuts_id FROM stat.heat_tot_curr_density_tif_nuts WHERE nuts_id IN ("+nuts+")), " +\
					"loadprofile as (SELECT sum(stat.load_profile.value) as valtot, stat.load_profile.nuts_id from stat.load_profile " +\
						"INNER JOIN nutsSelection on stat.load_profile.nuts_id = nutsSelection.nuts_id " +\
						"where stat.load_profile.nuts_id = nutsSelection.nuts_id " +\
						"group by  nutsSelection.nuts_id, stat.load_profile.nuts_id), " +\
					"heatdemand as (SELECT sum as HDtotal, stat.heat_tot_curr_density_tif_nuts.nuts_id from stat.heat_tot_curr_density_tif_nuts " +\
						"INNER JOIN nutsSelection on stat.heat_tot_curr_density_tif_nuts.nuts_id = nutsSelection.nuts_id " +\
						"where stat.heat_tot_curr_density_tif_nuts.nuts_id = nutsSelection.nuts_id), " +\
					"normalizedData as (SELECT avg(stat.load_profile.value/valtot*HDtotal) AS avg_1, min(stat.load_profile.value/valtot*HDtotal) AS min_1, " +\
						"max(stat.load_profile.value/valtot*HDtotal) AS max_1, sum(stat.load_profile.value/valtot*HDtotal) as sum_1, " +\
						"stat.time.month AS statmonth, stat.time.year AS statyear "

	timeMonth = ", stat.time.day AS statday "
	timeDay = ", stat.time.hour_of_day AS hour_of_day, stat.time.day AS statday "

	fromPart = "FROM stat.load_profile " +\
						"INNER JOIN nutsSelection on stat.load_profile.nuts_id = nutsSelection.nuts_id " +\
						"INNER JOIN loadprofile on stat.load_profile.nuts_id = loadprofile.nuts_id " +\
						"INNER JOIN heatdemand on stat.load_profile.nuts_id = heatdemand.nuts_id " +\
						"INNER JOIN geo.nuts ON geo.nuts.nuts_id = stat.load_profile.nuts_id " +\
						"INNER JOIN stat.time ON stat.time.id = stat.load_profile.fk_time_id "

	selectYear = "GROUP BY stat.load_profile.fk_nuts_gid, statmonth, statyear " +\
						"ORDER BY statmonth ASC) " +\
						"select sum(min_1), sum(max_1), sum(avg_1), statmonth from normalizedData " +\
						"group by statmonth " +\
						"order by statmonth;"
	selectMonth = "GROUP BY stat.load_profile.fk_nuts_gid, statday, statmonth, statyear " +\
						"ORDER BY statday ASC) " +\
						"select sum(min_1), sum(max_1), sum(avg_1), statday from normalizedData " +\
						"where statmonth = " + str(month) + " " +\
						"group by statday, statmonth " +\
						"order by statday;"
	selectDay = "GROUP BY stat.load_profile.fk_nuts_gid, hour_of_day, statday, statmonth, statyear " +\
						"ORDER BY hour_of_day ASC) " +\
						"select sum(sum_1), hour_of_day from normalizedData " +\
						"where statmonth = " + str(month) + " " +\
						"and statday = " + str(day) + " " +\
						"group by hour_of_day " +\
						"order by hour_of_day;"

	# Dictionary with query data
	queryData = {'byYear':{'with':withPart, 'time':'', 'from':fromPart, 'select':selectYear},
						'byMonth':{'with':withPart, 'time':timeMonth, 'from':fromPart, 'select':selectMonth},
						'byDay':{'with':withPart, 'time':timeDay, 'from':fromPart, 'select':selectDay}}



	return queryData

# ALL QUERIES DATA FOR THE DURATION CURVE BY NUTS
def createQueryDataDCNutsLau(year, nuts):
	sql_query =	"WITH nutsSelection as (select nuts_id FROM stat.heat_tot_curr_density_tif_nuts WHERE nuts_id IN ("+nuts+")), " +\
						"loadprofile as (SELECT sum(stat.load_profile.value) as valtot, stat.load_profile.nuts_id from stat.load_profile " +\
							"INNER JOIN nutsSelection on stat.load_profile.nuts_id = nutsSelection.nuts_id " +\
							"where stat.load_profile.nuts_id = nutsSelection.nuts_id group by nutsSelection.nuts_id, stat.load_profile.nuts_id), " +\
						"heatdemand as (SELECT sum as HDtotal, stat.heat_tot_curr_density_tif_nuts.nuts_id from stat.heat_tot_curr_density_tif_nuts " +\
							"INNER JOIN nutsSelection on stat.heat_tot_curr_density_tif_nuts.nuts_id = nutsSelection.nuts_id " +\
							"where stat.heat_tot_curr_density_tif_nuts.nuts_id = nutsSelection.nuts_id) " +\
						"SELECT sum(stat.load_profile.value/valtot*HDtotal) as val, stat.time.hour_of_year as hoy from stat.load_profile " +\
							"INNER JOIN nutsSelection on stat.load_profile.nuts_id = nutsSelection.nuts_id " +\
							"INNER JOIN stat.time on stat.load_profile.fk_time_id = stat.time.id " +\
							"INNER JOIN loadprofile on stat.load_profile.nuts_id = loadprofile.nuts_id " +\
							"INNER JOIN heatdemand on stat.load_profile.nuts_id = heatdemand.nuts_id " +\
							"WHERE stat.load_profile.nuts_id is not null and fk_time_id is not null " +\
							"AND stat.load_profile.nuts_id = nutsSelection.nuts_id " +\
							"GROUP BY hoy " +\
							"HAVING	COUNT(value)=COUNT(*) " +\
							"ORDER BY val DESC;"

	return sql_query

# ALL QUERIES DATA FOR THE DURATION CURVE BY HECTARES
def createQueryDataDCHectares(year, geometry):
	sql_query = "with subAreas as (SELECT ST_Intersection(ST_Transform(ST_GeomFromText(\'" + geometry +"\',4326),4258),nuts.geom) as soustracteGeom, " +\
							"nuts.gid " +\
							"FROM geo.nuts " +\
							"where ST_Intersects(nuts.geom,ST_Transform(ST_GeomFromText(\'" + geometry +"\',4326),4258)) " + \
							"AND STAT_LEVL_=2 ), " +\
						"statBySubAreas as (SELECT (ST_SummaryStatsAgg(ST_Clip(heat_tot_curr_density_tif.rast,1, " +\
							"ST_Transform(subAreas.soustracteGeom,3035),0,true),1,true)).* as stat, subAreas.gid " +\
							"FROM subAreas, geo.heat_tot_curr_density_tif " +\
							"WHERE ST_Intersects(heat_tot_curr_density_tif.rast,ST_Transform(subAreas.soustracteGeom,3035)) group by subAreas.gid), " +\
						"statLoadProfilBySubarea as (select stat.load_profile.nuts_id as load_profile_nutsid, stat.load_profile.value as val_load_profile, " +\
							"stat.time.month as month_of_year, " +\
							"stat.time.hour_of_year as hour_of_year, " +\
							"stat.time.day as day_of_month, " +\
							"stat.time.hour_of_day as hour_of_day, " +\
							"statBySubAreas.count as statCount, statBySubAreas.sum as statSum_HD " +\
							"from stat.load_profile " +\
							"left join statBySubAreas on statBySubAreas.gid = stat.load_profile.fk_nuts_gid " +\
							"inner join stat.time on stat.load_profile.fk_time_id = stat.time.id " +\
							"WHERE fk_nuts_gid is not null and fk_time_id is not null " +\
							"AND statBySubAreas.gid = stat.load_profile.fk_nuts_gid AND stat.time.year = " + str(year) + " " +\
							"order by stat.time.hour_of_year), " +\
						"totalLoadprofile as ( " +\
							"select sum(val_load_profile) as tot_load_profile,load_profile_nutsid " +\
							"from statLoadProfilBySubarea group by load_profile_nutsid) " +\
						"select sum(val_load_profile/tot_load_profile*statSum_HD) as normalizedCalutation,hour_of_year " +\
							"from statLoadProfilBySubarea " +\
							"inner join totalLoadprofile on statLoadProfilBySubarea.load_profile_nutsid = totalLoadprofile.load_profile_nutsid " +\
							"group by hour_of_year " +\
							"order by normalizedCalutation DESC;"

	return sql_query

