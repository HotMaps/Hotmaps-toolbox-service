from main_api import settings

popDeHa = settings.POPULATION_TOT + '_ha'
heatDeHa = settings.HEAT_DENSITY_TOT + '_ha'
wwtpHa = settings.WWTP + '_ha'

CRS = 3035

# ALL DATA FOR THE STATS BY LAYERS
layersData = {
	heatDeHa:{'tablename':'heat_tot_curr_density',
			'resultsName':{
				0:'heat_consumption', 1:'heat_density', 2:'count_cell_heat'},
			'resultsUnit':{
				0:'MWh', 1:'MWh/ha', 2:'cell'}
			},
	popDeHa:{'tablename':'pop_tot_curr_density',
			'resultsName':{
				0:'population', 1:'population_density', 2:'count_cell_pop'},
			'resultsUnit':{ 
				0:'person', 1:'person/ha', 2:'cell'}
			},
	wwtpHa:{'tablename':'wwtp',
			'resultsName':{
				0:'power', 1:'capacity'},
			'resultsUnit':{
				0:'kW', 1:'Person equivalent'}
			}
}

# ALL QUERIES DATA FOR THE STATS BY LAYERS 
def createQueryDataStatsHectares(geometry, year):
	withPop = ''
	withHeat = ''
	withWwtp = ''

	# 'with' parts
	withPop = 'stat_pop AS ( SELECT (' + \
		'	((ST_SummaryStatsAgg(' + \
		'		ST_Clip('+ layersData[popDeHa]['tablename'] + '.rast, 1, ' + \
		'			st_transform(st_geomfromtext(\'' + \
						geometry + '\'::text,4326),' + str(CRS) + '),false),true,0))).*) as stats ' + \
		'FROM' + \
		'	geo.'+ layersData[popDeHa]['tablename'] + \
		' WHERE' + \
		'	ST_Intersects('+ layersData[popDeHa]['tablename'] + '.rast,' + \
		'		st_transform(st_geomfromtext(\''+ geometry +'\'::text,4326),' + str(CRS) + ')) ' + \
		'AND date = to_date(\''+ str(year) +'\',\'YYYY\')) '

	withHeat = ' stat_heat AS ( SELECT (' + \
		'		((ST_SummaryStatsAgg(ST_Clip('+ layersData[heatDeHa]['tablename'] + '.rast, 1, ' + \
		'			st_transform(st_geomfromtext(\''+ \
						geometry +'\'::text,4326),' + str(CRS) + '),false),true,0))).*) as stats ' + \
		'FROM' + \
		'	geo.'+ layersData[heatDeHa]['tablename'] + \
		' WHERE' + \
		'	ST_Intersects('+ layersData[heatDeHa]['tablename'] + '.rast,' + \
		'		st_transform(st_geomfromtext(\''+ geometry +'\'::text,4326),' + str(CRS) + ')) ' + \
		'AND date = to_date(\''+ str(year) +'\',\'YYYY\')) '

	withWwtp = ' stat_wwtp AS (SELECT ' + \
		'		count(*) as nbWwtp, sum(capacity) as capacityPerson, sum(power) as power ' + \
		'FROM' + \
		'	geo.'+ layersData[wwtpHa]['tablename'] + ' tbl_wwtp' + \
		' WHERE' + \
		'	ST_Within(tbl_wwtp.geom,st_transform(st_geomfromtext(\''+ geometry +'\'::text,4326),' + str(CRS) + ')) ' + \
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

	return layersQueryData

# ALL QUERIES DATA FOR THE HEAT LOAD PROFILE BY HECTARES 
def createQueryDataLPHectares(year, month, day, geometry):
	withPart = "with subAreas as (SELECT ST_Intersection(ST_Transform(ST_GeomFromText(\'" + geometry +"\',4326),4258),nuts.geom) as soustracteGeom, " +\
						"nuts.gid " +\
						"FROM geo.nuts " +\
						"where ST_Intersects(nuts.geom,ST_Transform(ST_GeomFromText(\'" + geometry +"\',4326),4258)) " + \
						"AND STAT_LEVL_=2 AND year = to_date('" + str(year) + "','YYYY')), " +\
					"statBySubAreas as (SELECT (ST_SummaryStatsAgg(ST_Clip(heat_tot_curr_density.rast,1, " +\
						"ST_Transform(subAreas.soustracteGeom,3035),0,true),1,true)).* as stat, subAreas.gid " +\
						"FROM subAreas, geo.heat_tot_curr_density " +\
						"WHERE ST_Intersects(heat_tot_curr_density.rast,ST_Transform(subAreas.soustracteGeom,3035)) group by subAreas.gid), " +\
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
	withPart = "WITH nutsSelection as (select nuts_id FROM stat.heat_tot_curr_density_nuts_test WHERE nuts_id IN ("+nuts+")), " +\
					"loadprofile as (SELECT sum(stat.load_profile.value) as valtot, stat.load_profile.nuts_id from stat.load_profile " +\
						"INNER JOIN nutsSelection on stat.load_profile.nuts_id = nutsSelection.nuts_id " +\
						"where stat.load_profile.nuts_id = nutsSelection.nuts_id " +\
						"group by  nutsSelection.nuts_id, stat.load_profile.nuts_id), " +\
					"heatdemand as (SELECT sum as HDtotal, stat.heat_tot_curr_density_nuts_test.nuts_id from stat.heat_tot_curr_density_nuts_test " +\
						"INNER JOIN nutsSelection on stat.heat_tot_curr_density_nuts_test.nuts_id = nutsSelection.nuts_id " +\
						"where stat.heat_tot_curr_density_nuts_test.nuts_id = nutsSelection.nuts_id), " +\
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
	sql_query =	"WITH nutsSelection as (select nuts_id FROM stat.heat_tot_curr_density_nuts_test WHERE nuts_id IN ("+nuts+")), " +\
						"loadprofile as (SELECT sum(stat.load_profile.value) as valtot, stat.load_profile.nuts_id from stat.load_profile " +\
							"INNER JOIN nutsSelection on stat.load_profile.nuts_id = nutsSelection.nuts_id " +\
							"where stat.load_profile.nuts_id = nutsSelection.nuts_id group by nutsSelection.nuts_id, stat.load_profile.nuts_id), " +\
						"heatdemand as (SELECT sum as HDtotal, stat.heat_tot_curr_density_nuts_test.nuts_id from stat.heat_tot_curr_density_nuts_test " +\
							"INNER JOIN nutsSelection on stat.heat_tot_curr_density_nuts_test.nuts_id = nutsSelection.nuts_id " +\
							"where stat.heat_tot_curr_density_nuts_test.nuts_id = nutsSelection.nuts_id) " +\
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
							"AND STAT_LEVL_=2 AND year = to_date('" + str(year) + "','YYYY')), " +\
						"statBySubAreas as (SELECT (ST_SummaryStatsAgg(ST_Clip(heat_tot_curr_density.rast,1, " +\
							"ST_Transform(subAreas.soustracteGeom,3035),0,true),1,true)).* as stat, subAreas.gid " +\
							"FROM subAreas, geo.heat_tot_curr_density " +\
							"WHERE ST_Intersects(heat_tot_curr_density.rast,ST_Transform(subAreas.soustracteGeom,3035)) group by subAreas.gid), " +\
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

def sampling_data(listValues):
	# Get number of values
	numberOfValues = len(listValues)

	# Create the points for the curve with the X and Y axis
	listPoints = []
	for n, l in enumerate(listValues):
		listPoints.append({
			'X':n+1,
			'Y':listValues[n]
		})

	# Sampling of the values
	cut1 = int(numberOfValues*settings.POINTS_FIRST_GROUP_PERCENTAGE) 
	cut2 = int(cut1+(numberOfValues*settings.POINTS_SECOND_GROUP_PERCENTAGE)) 
	cut3 = int(cut2+(numberOfValues*settings.POINTS_THIRD_GROUP_PERCENTAGE)) 

	firstGroup = listPoints[0:cut1:settings.POINTS_FIRST_GROUP_STEP]
	secondGroup = listPoints[cut1:cut2:settings.POINTS_SECOND_GROUP_STEP]
	thirdGroup = listPoints[cut2:cut3:settings.POINTS_THIRD_GROUP_STEP]
	fourthGroup = listPoints[cut3:numberOfValues:settings.POINTS_FOURTH_GROUP_STEP]

	# Get min and max values needed for the sampling list
	maxValue = min(listPoints)
	minValue = max(listPoints)

	# Concatenate the groups to a new list of points (sampling list)
	finalListPoints = firstGroup+secondGroup+thirdGroup+fourthGroup

	# Add max value at the beginning if the list doesn't contain it
	if maxValue not in finalListPoints:
		finalListPoints.insert(0, maxValue)

	# Add min value at the end if the list doesn't contain it
	if minValue not in finalListPoints:
		finalListPoints.append(minValue)

	return finalListPoints

def computeConsPerPerson(l1, l2, output):
	"""
	Compute the heat consumption/person if population_density and heat_density layers are selected
	"""
	hdm = None
	heat_cons = None
	population = None

	for l in output:
		if l.get('name') == l2:
			hdm = l
			for v in l.get('values', []):
				if v.get('name') == 'heat_consumption':
					heat_cons = v
		if l.get('name') == l1:
			for v in l.get('values', []):
				if v.get('name') == 'population':
					population = v

	if heat_cons != None and population != None:
		pop_val = float(population.get('value', 1))
		pop_val = pop_val if pop_val > 0 else 1
		hea_val = float(heat_cons.get('value', 0))

		v = {
			'name': 'consumption_per_citizen',
			'value': hea_val / pop_val,
			'unit': heat_cons.get('unit') + '/' + population.get('unit')
		}

		hdm.get('values').append(v)

	return hdm