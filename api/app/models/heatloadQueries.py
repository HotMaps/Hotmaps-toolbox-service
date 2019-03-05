
from app import constants
from app import model
from app import celery
from .. import helper
#logging.basicConfig()
#logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

class HeatLoadProfile:
	@staticmethod
	@celery.task(name = 'heatloadprofile_nuts_lau')
	def heatloadprofile_nuts_lau(year, month, day, nuts, nuts_level): #/heat-load-profile/nuts-lau
		request_type=''
		# Check the type of the query
		if month != 0 and day != 0:
			request_type = 'day'
		elif month != 0:
			request_type = 'month'
		else:
			request_type = 'year'

		# Get the data
		query = createQueryDataLPNutsLau(year=year, month=month, day=day, nuts=nuts,request_type=request_type, nuts_level=nuts_level)

		# Construction of the query
		# Execution of the query
		#query = db.session.execute(sql_query)

		res = model.query_geographic_database(query)
		# Storing the results only if there is data
		output = []
		
		for c, q in enumerate(res):
			if q[0]:
				data={}
				if request_type == 'year':
					data = {
						'year': year,'month': q[4],'granularity': 'month','unit': 'kW','min': round(q[0], constants.NUMBER_DECIMAL_DATA),
						'max': round(q[1], constants.NUMBER_DECIMAL_DATA),'average': round(q[2], constants.NUMBER_DECIMAL_DATA)
					}
				elif request_type == 'month':
					data = {
						'year': year,'month': month,'day': q[4],'granularity': 'day','unit': 'kW','min': round(q[0], constants.NUMBER_DECIMAL_DATA),
							'max': round(q[1], constants.NUMBER_DECIMAL_DATA),
							'average': round(q[2], constants.NUMBER_DECIMAL_DATA)
					}
				elif request_type == 'day':
					data = {
						'year': year,'month': month,'day': day,'hour_of_day': q[4],'granularity': 'hour',
						'unit': 'kW','value': round(q[3], constants.NUMBER_DECIMAL_DATA)
					}
				output.append(data)
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
	def duration_curve_nuts_lau(year, nuts, nuts_level): #/heat-load-profile/duration-curve/nuts-lau

		# Get the query
		sql_query = createQueryDataDCNutsLau(year=year, nuts=nuts, nuts_level=nuts_level)

		# Execution of the query
		#query = db.session.execute(sql_query)

		query = model.query_geographic_database(sql_query)


		# Store query results in a list
		listAllValues = []
		points = []
		for n, q in enumerate(query):
			#listAllValues.append(q[0])
			points.append({
				'X':n+1,
				'Y':float(q[0])
			})
	

		newList = points[0:len(points)-1:10]
		return newList

	@staticmethod
	def duration_curve_hectares(year, geometry): #/heat-load-profile/duration-curve/hectares

		# Get the query
		sql_query = createQueryDataDCHectares(year=year, geometry=geometry)

		query = model.query_geographic_database(sql_query)
		listAllValues = []
		for n, q in enumerate(query):
			listAllValues.append({
				'X':n+1,
				'Y':q[0]
			})

		listAllValues = listAllValues[0:len(listAllValues)-1:10]
	

		return listAllValues

def createQueryDataLPHectares(year, month, day, geometry):
	withPart = "with geomInput AS (SELECT ST_Transform(ST_GeomFromText('"+geometry+"',4326),4258) AS geometry), " + \
			   "nuts2 AS (SELECT nuts.geom, nuts.gid FROM geo.nuts WHERE nuts.year = '2010-01-01' AND nuts.stat_levl_ = 2)," + \
			   "subAreas as (SELECT ST_Transform(ST_Intersection(geomInput.geometry ,nuts2.geom),3035) as soustracteGeom, " +\
						"nuts2.gid " +\
						"FROM nuts2, geomInput " +\
						"where ST_Intersects(nuts2.geom,geomInput.geometry)), " + \
					"statBySubAreas as (SELECT (ST_SummaryStatsAgg(ST_Clip(heat_tot_curr_density.rast,1, subAreas.soustracteGeom,0,true),1,true)).* as stat, subAreas.gid " +\
						"FROM subAreas, geo.heat_tot_curr_density, geomInput " +\
						"WHERE ST_Intersects(heat_tot_curr_density.rast,subAreas.soustracteGeom) group by subAreas.gid), " +\
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
def createQueryDataLPNutsLau(year, month, day, nuts, request_type, nuts_level, query_type="heatload"):
	where_request=''
	nutsSelectionQuery=''
	scale_schema = 'geo'
	hd_nuts_select= ''
	from_clause_lp = 'stat.load_profile'

	if request_type=='year':
		time_columns = "stat.time.month AS statmonth,stat.time.year AS statyear"
		group_by_time_columns="statmonth,statyear"
	elif request_type == 'month':
		time_columns = "stat.time.day AS statday,stat.time.month AS statmonth,stat.time.year AS statyear"
		group_by_time_columns=" statday, statmonth, statyear"
		where_request="where statmonth = " + str(month)
	elif request_type == 'day':
		time_columns = "stat.time.hour_of_day as hour_of_day, stat.time.day AS statday,stat.time.month AS statmonth,stat.time.year AS statyear"
		group_by_time_columns="hour_of_day, statday, statmonth, statyear"
		where_request="where statmonth = " + str(month) + " and statday = " + str(day)
	if nuts_level == 'LAU 2':
		scale_level_table='lau'
		scale_id = 'comm_id'
	else:
		scale_level_table='nuts'
		scale_id = 'nuts_id'

	hd_table = "stat.heat_tot_curr_density_"+scale_level_table
	where_clause_hd = hd_table+"."+scale_id+" in ("+nuts+")"

	from_hd = hd_table

	if nuts_level in constants.scale_level_loadprofile_aggreagtion:
		nutsSelectionQuery = helper.get_nuts_query_selection(nuts,scale_level_table, scale_id)

		where_clause_lp = "stat.load_profile.nuts_id = nutsSelection.nuts2_id"
		from_clause_lp += ',nutsSelection'
		hd_nuts_select = "nutsSelection.nuts2_id"
		from_hd += ', nutsSelection'
		where_clause_hd = hd_table+"."+scale_id+" = nutsSelection.scale_id"

	elif nuts_level == 'NUTS 2':
		where_clause_lp = "stat.load_profile.nuts_id in ("+nuts+")"
		where_clause_hd = hd_table+"."+scale_id+" in ("+nuts+")"
		hd_nuts_select = hd_table + '.nuts_id'
	
	query_lp = """loadprofile as (
		SELECT sum(stat.load_profile.value) as valtot, stat.load_profile.nuts_id
		from """+from_clause_lp+"""
		where """+where_clause_lp+"""
		group by stat.load_profile.nuts_id
	), """

	query_hd = """heatdemand as (
		SELECT sum(sum) as HDtotal,"""+hd_nuts_select+""" as nuts2_id
		from """+from_hd+"""
		where """+where_clause_hd+"""
		group by """+hd_nuts_select+"""
	), """

	select_normalized = ''
	groupby_normalized = ''
	query_select=''
	if query_type == 'duration_curve':
		select_normalized = 'sum(stat.load_profile.value/valtot*HDtotal) as val, stat.time.hour_of_year as hoy'
		groupby_normalized = "stat.load_profile.fk_nuts_gid,stat.time.hour_of_year HAVING COUNT(value) = COUNT(*)"
		query_select = "select sum(val) as values, hoy from normalizedData  group by hoy order by values DESC"

	
	elif query_type == 'heatload':
		select_normalized = "avg(stat.load_profile.value / valtot * HDtotal) AS avg_1,min(stat.load_profile.value / valtot * HDtotal) AS min_1, max(stat.load_profile.value / valtot * HDtotal) AS max_1, sum(stat.load_profile.value / valtot * HDtotal) as sum_1,"+time_columns
		groupby_normalized = " stat.load_profile.fk_nuts_gid, """+group_by_time_columns
		query_select="""select sum(min_1), sum(max_1), sum(avg_1), sum(sum_1), """+group_by_time_columns
		query_select+=""" from normalizedData """
		query_select+=where_request+""" group by """+group_by_time_columns+""" order by """+group_by_time_columns



	query_normalized = """normalizedData as (
		SELECT """+select_normalized+"""
		FROM """+from_clause_lp+""", heatdemand hd, loadprofile lp, stat.time
		where  """+where_clause_lp+""" 
			and stat.load_profile.nuts_id is not null and 
			stat.load_profile.fk_time_id is not null and 
			stat.time.id = stat.load_profile.fk_time_id and 
			stat.load_profile.nuts_id = hd.nuts2_id and 
			stat.load_profile.nuts_id = lp.nuts_id 
		group by """+groupby_normalized+""")"""
	
	
	query = 'with ' + nutsSelectionQuery + query_lp + query_hd + query_normalized + query_select
	return query

# ALL QUERIES DATA FOR THE DURATION CURVE BY NUTS
def createQueryDataDCNutsLau(year, nuts, nuts_level):
	sql_query = createQueryDataLPNutsLau(year,None,None,nuts,'year',nuts_level,'duration_curve')
	return sql_query

# ALL QUERIES DATA FOR THE DURATION CURVE BY HECTARES
def createQueryDataDCHectares(year, geometry):
	sql_query = "with geomInput AS (SELECT ST_Transform(ST_GeomFromText('"+geometry+"',4326),4258) AS geometry), " + \
			   "nuts2 AS (SELECT nuts.geom, nuts.gid FROM geo.nuts WHERE nuts.year = '2010-01-01' AND nuts.stat_levl_ = 2)," + \
			   "subAreas as (SELECT ST_Transform(ST_Intersection(geomInput.geometry ,nuts2.geom),3035) as soustracteGeom, " + \
			   "nuts2.gid " + \
			   "FROM nuts2, geomInput " + \
			   "where ST_Intersects(nuts2.geom,geomInput.geometry)), " + \
			   "statBySubAreas as (SELECT (ST_SummaryStatsAgg(ST_Clip(heat_tot_curr_density.rast,1, " +\
				"subAreas.soustracteGeom,0,true),1,true)).* as stat, subAreas.gid " +\
				"FROM subAreas, geo.heat_tot_curr_density " +\
				"WHERE ST_Intersects(heat_tot_curr_density.rast,subAreas.soustracteGeom) group by subAreas.gid), " +\
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
	print(sql_query)
	return sql_query

