from main_api import settings

# LAYERS
popDeHa = settings.POPULATION_TOT + '_ha'
heatDeHa = settings.HEAT_DENSITY_TOT + '_ha'
wwtpHa = settings.WWTP + '_ha'
grassHa = settings.GRASS_FLOOR_AREA_TOT + '_ha'
grassResHa = settings.GRASS_FLOOR_AREA_RES + '_ha'
grassNonResHa = settings.GRASS_FLOOR_AREA_NON_RES + '_ha'
bVolTotHa = settings.BUILDING_VOLUMES_TOT + '_ha'
bVolResHa = settings.BUILDING_VOLUMES_RES + '_ha'
bVolNonResHa = settings.BUILDING_VOLUMES_NON_RES + '_ha'
heatResHa = settings.HEAT_DENSITY_RES + '_ha'
heatNonResHa = settings.HEAT_DENSITY_NON_RES + '_ha'
indSitesHa = settings.INDUSTRIAL_SITES + '_ha'
biomassPotHa = settings.BIOMASS_POTENTIAL + '_ha'
mswHa = settings.MUNICIPAL_SOLID_WASTE + '_ha'
windPotHa = settings.WIND_POTENTIAL + '_ha'
solarPotHa = settings.SOLAR_POTENTIAL + '_ha'
geothermalPotHa = settings.GEOTHERMAL_POTENTIAL + '_ha'

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
			},
	grassHa:{'tablename':'gfa_tot_curr_density',
			'resultsName':{
				0:'value', 1:'density', 2:'count_cell'},
			'resultsUnit':{ 
				0:'value', 1:'value/ha', 2:'cell'}
			},
	grassResHa:{'tablename':'gfa_res_curr_density',
			'resultsName':{
				0:'value5', 1:'density5', 2:'count_cell5'},
			'resultsUnit':{ 
				0:'value', 1:'value/ha', 2:'cell'}
			},
	grassNonResHa:{'tablename':'gfa_nonres_curr_density',
			'resultsName':{
				0:'value6', 1:'density6', 2:'count_cell6'},
			'resultsUnit':{ 
				0:'value', 1:'value/ha', 2:'cell'}
			},
	bVolTotHa:{'tablename':'vol_tot_curr_density',
			'resultsName':{
				0:'value2', 1:'density2', 2:'count_cell2'},
			'resultsUnit':{ 
				0:'value', 1:'value/ha', 2:'cell'}
			},
	bVolResHa:{'tablename':'vol_res_curr_density',
			'resultsName':{
				0:'value3', 1:'density3', 2:'count_cell3'},
			'resultsUnit':{ 
				0:'value', 1:'value/ha', 2:'cell'}
			},
	bVolNonResHa:{'tablename':'vol_nonres_curr_density',
			'resultsName':{
				0:'value4', 1:'density4', 2:'count_cell4'},
			'resultsUnit':{ 
				0:'value', 1:'value/ha', 2:'cell'}
			},
	heatResHa:{'tablename':'heat_res_curr_density',
			'resultsName':{
				0:'value7', 1:'density7', 2:'count_cell7'},
			'resultsUnit':{ 
				0:'value', 1:'value/ha', 2:'cell'}
			},
	heatNonResHa:{'tablename':'heat_nonres_curr_density',
			'resultsName':{
				0:'value8', 1:'density8', 2:'count_cell8'},
			'resultsUnit':{ 
				0:'value', 1:'value/ha', 2:'cell'}
			},
	geothermalPotHa:{'tablename':'potential_shallowgeothermal',
			'resultsName':{
				0:'value9', 1:'density9', 2:'count_cell9'},
			'resultsUnit':{ 
				0:'value', 1:'value/ha', 2:'cell'}
			},
}

# ALL QUERIES DATA FOR THE STATS BY LAYERS 
def createQueryDataStatsHectares(geometry, year):
	# 'from' parts
	fromPop = 'stat_pop'
	fromHeat = 'stat_heat'
	fromWwtp = 'stat_wwtp'
	fromGrass = 'stat_grass'
	fromGrassRes = 'stat_grassRes'
	fromGrassNonRes = 'stat_grassNonRes'
	frombVolTot = 'stat_bVolTot'
	frombVolRes = 'stat_bVolRes'
	frombVolNonRes = 'stat_bVolNonRes'
	fromHeatRes = 'stat_heatRes'
	fromHeatNonRes = 'stat_heatNonRes'
	fromGeothermalPot = 'stat_geothermalPot'

	# 'with' parts
	withPop = createWithPartEachLayer(geometry=geometry, year=year, layer=popDeHa, fromPart=fromPop)
	withHeat = createWithPartEachLayer(geometry=geometry, year=year, layer=heatDeHa, fromPart=fromHeat)
	withWwtp = createWithPartEachLayer(geometry=geometry, year=year, layer=wwtpHa, fromPart=fromWwtp)
	withGrass = createWithPartEachLayer(geometry=geometry, year=year, layer=grassHa, fromPart=fromGrass)
	withGrassRes = createWithPartEachLayer(geometry=geometry, year=year, layer=grassResHa, fromPart=fromGrassRes)
	withGrassNonRes = createWithPartEachLayer(geometry=geometry, year=year, layer=grassNonResHa, fromPart=fromGrassNonRes)
	withbVolTot = createWithPartEachLayer(geometry=geometry, year=year, layer=bVolTotHa, fromPart=frombVolTot)
	withbVolRes = createWithPartEachLayer(geometry=geometry, year=year, layer=bVolResHa, fromPart=frombVolRes)
	withbVolNonRes = createWithPartEachLayer(geometry=geometry, year=year, layer=bVolNonResHa, fromPart=frombVolNonRes)
	withHeatRes = createWithPartEachLayer(geometry=geometry, year=year, layer=heatResHa, fromPart=fromHeatRes)
	withHeatNonRes = createWithPartEachLayer(geometry=geometry, year=year, layer=heatNonResHa, fromPart=fromHeatNonRes)
	withGeothermalPot = createWithPartEachLayer(geometry=geometry, year=year, layer=geothermalPotHa, fromPart=fromGeothermalPot)
	
	# 'select' parts
	selectPop = 'stat_pop.sum as population, (stat_pop.sum/stat_pop.count) as population_density, stat_pop.count as count_cell_pop '
	selectHeat = 'stat_heat.sum as heat_consumption, (stat_heat.sum/stat_heat.count) as heat_density, stat_heat.count as count_cell_heat '
	selectWwtp = 'stat_wwtp.capacityPerson as capacity, stat_wwtp.power as power '
	selectGrass = 'stat_grass.sum as value, (stat_grass.sum/stat_grass.count) as density, stat_grass.count as count_cell '
	selectGrassRes = 'stat_grassRes.sum as value5, (stat_grassRes.sum/stat_grassRes.count) as density5, stat_grassRes.count as count_cell5 '
	selectGrassNonRes = 'stat_grassNonRes.sum as value6, (stat_grassNonRes.sum/stat_grassNonRes.count) as density6, stat_grassNonRes.count as count_cell6 '
	selectbVolTot = 'stat_bVolTot.sum as value2, (stat_bVolTot.sum/stat_bVolTot.count) as density2, stat_bVolTot.count as count_cell2 '
	selectbVolRes = 'stat_bVolRes.sum as value3, (stat_bVolRes.sum/stat_bVolRes.count) as density3, stat_bVolRes.count as count_cell3 '
	selectbVolNonRes = 'stat_bVolNonRes.sum as value4, (stat_bVolNonRes.sum/stat_bVolNonRes.count) as density4, stat_bVolNonRes.count as count_cell4 '
	selectHeatRes = 'stat_heatRes.sum as value7, (stat_heatRes.sum/stat_heatRes.count) as density7, stat_heatRes.count as count_cell7 '
	selectHeatNonRes = 'stat_heatNonRes.sum as value8, (stat_heatNonRes.sum/stat_heatNonRes.count) as density8, stat_heatNonRes.count as count_cell8 '
	selectGeothermalPot = 'stat_geothermalPot.sum as value9, (stat_geothermalPot.sum/stat_geothermalPot.count) as density9, stat_geothermalPot.count as count_cell9 '

	# Dictionary with query data
	layersQueryData = {heatDeHa:{'with':withHeat, 'select':selectHeat, 'from':fromHeat},
						popDeHa:{'with':withPop, 'select':selectPop, 'from':fromPop},
						wwtpHa:{'with':withWwtp, 'select':selectWwtp, 'from':fromWwtp},
						grassHa:{'with':withGrass, 'select':selectGrass, 'from':fromGrass},
						grassResHa:{'with':withGrassRes, 'select':selectGrassRes, 'from':fromGrassRes},
						grassNonResHa:{'with':withGrassNonRes, 'select':selectGrassNonRes, 'from':fromGrassNonRes},
						bVolTotHa:{'with':withbVolTot, 'select':selectbVolTot, 'from':frombVolTot},
						bVolResHa:{'with':withbVolRes, 'select':selectbVolRes, 'from':frombVolRes},
						bVolNonResHa:{'with':withbVolNonRes, 'select':selectbVolNonRes, 'from':frombVolNonRes},
						heatResHa:{'with':withHeatRes, 'select':selectHeatRes, 'from':fromHeatRes},
						heatNonResHa:{'with':withHeatNonRes, 'select':selectHeatNonRes, 'from':fromHeatNonRes},
						geothermalPotHa:{'with':withGeothermalPot, 'select':selectGeothermalPot, 'from':fromGeothermalPot}}

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

def createWithPartEachLayer(geometry, year, layer, fromPart):
	if layer == wwtpHa:
		w = ''+fromPart+' AS (SELECT ' + \
		'		count(*) as nbWwtp, sum(capacity) as capacityPerson, sum(power) as power ' + \
		'FROM' + \
		'	geo.'+ layersData[layer]['tablename'] + ' tbl_wwtp' + \
		' WHERE' + \
		'	ST_Within(tbl_wwtp.geom,st_transform(st_geomfromtext(\''+ geometry +'\'::text,4326),' + str(CRS) + ')) ' + \
		'AND date = to_date(\''+ str(year) +'\',\'YYYY\')) '
	else:
		w = ''+fromPart+' AS ( SELECT (' + \
		'	((ST_SummaryStatsAgg(ST_Clip('+ layersData[layer]['tablename'] + '.rast, 1, ' + \
		'			st_transform(st_geomfromtext(\'' + \
						geometry + '\'::text,4326),' + str(CRS) + '),false),true,0))).*) as stats ' + \
		'FROM' + \
		'	geo.'+ layersData[layer]['tablename'] + \
		' WHERE' + \
		'	ST_Intersects('+ layersData[layer]['tablename'] + '.rast,' + \
		'		st_transform(st_geomfromtext(\''+ geometry +'\'::text,4326),' + str(CRS) + ')) '
		if layer == popDeHa or layer == heatDeHa:
			w += 'AND date = to_date(\''+ str(year) +'\',\'YYYY\')) '
		else:
			w += ')'

	return w