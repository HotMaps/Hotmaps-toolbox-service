from main_api import settings

# LAYERS
popDe = settings.POPULATION_TOT
heatDe = settings.HEAT_DENSITY_TOT
wwtp = settings.WWTP
grass = settings.GRASS_FLOOR_AREA_TOT
grassRes = settings.GRASS_FLOOR_AREA_RES
grassNonRes = settings.GRASS_FLOOR_AREA_NON_RES
bVolTot = settings.BUILDING_VOLUMES_TOT
bVolRes = settings.BUILDING_VOLUMES_RES
bVolNonRes = settings.BUILDING_VOLUMES_NON_RES
heatRes = settings.HEAT_DENSITY_RES
heatNonRes = settings.HEAT_DENSITY_NON_RES
indSites = settings.INDUSTRIAL_SITES
biomassPot = settings.BIOMASS_POTENTIAL
msw = settings.MUNICIPAL_SOLID_WASTE
windPot = settings.WIND_POTENTIAL
solarPot = settings.SOLAR_POTENTIAL
geothermalPot = settings.GEOTHERMAL_POTENTIAL

CRS = 3035

# ALL DATA FOR THE STATS
layersData = {
	heatDe:{'tablename':'heat_tot_curr_density',
			'from':'stat_heat',
			'select':'stat_heat.sum as heat_consumption, (stat_heat.sum/stat_heat.count) as heat_density, stat_heat.count as count_cell_heat ',
			'resultsName':{
				0:'heat_consumption', 1:'heat_density', 2:'count_cell_heat'},
			'resultsUnit':{
				0:'MWh', 1:'MWh/ha', 2:'cells'}
			},
	popDe:{'tablename':'pop_tot_curr_density',
			'from':'stat_pop',
			'select':'stat_pop.sum as population, (stat_pop.sum/stat_pop.count) as population_density, stat_pop.count as count_cell_pop ',
			'resultsName':{
				0:'population', 1:'population_density', 2:'count_cell_pop'},
			'resultsUnit':{ 
				0:'person', 1:'person/ha', 2:'cells'}
			},
	wwtp:{'tablename':'wwtp',
			'from':'stat_wwtp',
			'select':'stat_wwtp.capacityPerson as capacity, stat_wwtp.power as power ',
			'resultsName':{
				0:'power', 1:'capacity'},
			'resultsUnit':{
				0:'kW', 1:'Person equivalent'}
			},
	grass:{'tablename':'gfa_tot_curr_density',
			'from':'stat_grass',
			'select':'stat_grass.sum as '+grass+'_value, (stat_grass.sum/stat_grass.count) as '+grass+'_density, stat_grass.count as '+grass+'_cells ',
			'resultsName':{
				0:grass+'_value', 1:grass+'_density', 2:grass+'_cells'},
			'resultsUnit':{ 
				0:'m2', 1:'m2/ha', 2:'cells'}
			},
	grassRes:{'tablename':'gfa_res_curr_density',
			'from':'stat_grassRes',
			'select':'stat_grassRes.sum as '+grassRes+'_value, (stat_grassRes.sum/stat_grassRes.count) as '+grassRes+'_density, stat_grassRes.count as '+grassRes+'_cells ',
			'resultsName':{
				0:grassRes+'_value', 1:grassRes+'_density', 2:grassRes+'_cells'},
			'resultsUnit':{ 
				0:'value', 1:'value/ha', 2:'cells'}
			},
	grassNonRes:{'tablename':'gfa_nonres_curr_density',
			'from':'stat_grassNonRes',
			'select':'stat_grassNonRes.sum as '+grassNonRes+'_value, (stat_grassNonRes.sum/stat_grassNonRes.count) as '+grassNonRes+'_density, stat_grassNonRes.count as '+grassNonRes+'_cells ',
			'resultsName':{
				0:grassNonRes+'_value', 1:grassNonRes+'_density', 2:grassNonRes+'_cells'},
			'resultsUnit':{ 
				0:'value', 1:'value/ha', 2:'cells'}
			},
	bVolTot:{'tablename':'vol_tot_curr_density',
			'from':'stat_bVolTot',
			'select':'stat_bVolTot.sum as '+bVolTot+'_value, (stat_bVolTot.sum/stat_bVolTot.count) as '+bVolTot+'_density, stat_bVolTot.count as '+bVolTot+'_cells ',
			'resultsName':{
				0:bVolTot+'_value', 1:bVolTot+'_density', 2:bVolTot+'_cells'},
			'resultsUnit':{ 
				0:'value', 1:'value/ha', 2:'cells'}
			},
	bVolRes:{'tablename':'vol_res_curr_density',
			'from':'stat_bVolRes',
			'select':'stat_bVolRes.sum as '+bVolRes+'_value, (stat_bVolRes.sum/stat_bVolRes.count) as '+bVolRes+'_density, stat_bVolRes.count as '+bVolRes+'_cells ',
			'resultsName':{
				0:bVolRes+'_value', 1:bVolRes+'_density', 2:bVolRes+'_cells'},
			'resultsUnit':{ 
				0:'value', 1:'value/ha', 2:'cells'}
			},
	bVolNonRes:{'tablename':'vol_nonres_curr_density',
			'from':'stat_bVolNonRes',
			'select':'stat_bVolNonRes.sum as '+bVolNonRes+'_value, (stat_bVolNonRes.sum/stat_bVolNonRes.count) as '+bVolNonRes+'_density, stat_bVolNonRes.count as '+bVolNonRes+'_cells ',
			'resultsName':{
				0:bVolNonRes+'_value', 1:bVolNonRes+'_density', 2:bVolNonRes+'_cells'},
			'resultsUnit':{ 
				0:'value', 1:'value/ha', 2:'cells'}
			},
	heatRes:{'tablename':'heat_res_curr_density',
			'from':'stat_heatRes',
			'select':'stat_heatRes.sum as '+heatRes+'_value, (stat_heatRes.sum/stat_heatRes.count) as '+heatRes+'_density, stat_heatRes.count as '+heatRes+'_cells ',
			'resultsName':{
				0:heatRes+'_value', 1:heatRes+'_density', 2:heatRes+'_cells'},
			'resultsUnit':{ 
				0:'value', 1:'value/ha', 2:'cells'}
			},
	heatNonRes:{'tablename':'heat_nonres_curr_density',
			'from':'stat_heatNonRes',
			'select':'stat_heatNonRes.sum as '+heatNonRes+'_value, (stat_heatNonRes.sum/stat_heatNonRes.count) as '+heatNonRes+'_density, stat_heatNonRes.count as '+heatNonRes+'_cells ',
			'resultsName':{
				0:heatNonRes+'_value', 1:heatNonRes+'_density', 2:heatNonRes+'_cells'},
			'resultsUnit':{ 
				0:'value', 1:'value/ha', 2:'cells'}
			},
	geothermalPot:{'tablename':'potential_shallowgeothermal',
			'from':'stat_geothermalPot',
			'select':'stat_geothermalPot.sum as '+geothermalPot+'_value, (stat_geothermalPot.sum/stat_geothermalPot.count) as '+geothermalPot+'_density, stat_geothermalPot.count as '+geothermalPot+'_cells ',
			'resultsName':{
				0:geothermalPot+'_value', 1:geothermalPot+'_density', 2:geothermalPot+'_cells'},
			'resultsUnit':{ 
				0:'value', 1:'value/ha', 2:'cells'}
			},
}

# ALL QUERIES DATA FOR THE STATS BY LAYERS 
def createQueryDataStatsHectares(geometry, year):
	# 'with' parts
	withPop = constructWithPartEachLayerHectare(geometry=geometry, year=year, layer=popDe, fromPart=layersData[popDe]['from'])
	withHeat = constructWithPartEachLayerHectare(geometry=geometry, year=year, layer=heatDe, fromPart=layersData[heatDe]['from'])
	withWwtp = constructWithPartEachLayerHectare(geometry=geometry, year=year, layer=wwtp, fromPart=layersData[wwtp]['from'])
	withGrass = constructWithPartEachLayerHectare(geometry=geometry, year=year, layer=grass, fromPart=layersData[grass]['from'])
	withGrassRes = constructWithPartEachLayerHectare(geometry=geometry, year=year, layer=grassRes, fromPart=layersData[grassRes]['from'])
	withGrassNonRes = constructWithPartEachLayerHectare(geometry=geometry, year=year, layer=grassNonRes, fromPart=layersData[grassNonRes]['from'])
	withbVolTot = constructWithPartEachLayerHectare(geometry=geometry, year=year, layer=bVolTot, fromPart=layersData[bVolTot]['from'])
	withbVolRes = constructWithPartEachLayerHectare(geometry=geometry, year=year, layer=bVolRes, fromPart=layersData[bVolRes]['from'])
	withbVolNonRes = constructWithPartEachLayerHectare(geometry=geometry, year=year, layer=bVolNonRes, fromPart=layersData[bVolNonRes]['from'])
	withHeatRes = constructWithPartEachLayerHectare(geometry=geometry, year=year, layer=heatRes, fromPart=layersData[heatRes]['from'])
	withHeatNonRes = constructWithPartEachLayerHectare(geometry=geometry, year=year, layer=heatNonRes, fromPart=layersData[heatNonRes]['from'])
	
	# Dictionary with query data
	layersQueryData = {heatDe:{'with':withHeat, 'select':layersData[heatDe]['select'], 'from':layersData[heatDe]['from']},
						popDe:{'with':withPop, 'select':layersData[popDe]['select'], 'from':layersData[popDe]['from']},
						wwtp:{'with':withWwtp, 'select':layersData[wwtp]['select'], 'from':layersData[wwtp]['from']},
						grass:{'with':withGrass, 'select':layersData[grass]['select'], 'from':layersData[grass]['from']},
						grassRes:{'with':withGrassRes, 'select':layersData[grassRes]['select'], 'from':layersData[grassRes]['from']},
						grassNonRes:{'with':withGrassNonRes, 'select':layersData[grassNonRes]['select'], 'from':layersData[grassNonRes]['from']},
						bVolTot:{'with':withbVolTot, 'select':layersData[bVolTot]['select'], 'from':layersData[bVolTot]['from']},
						bVolRes:{'with':withbVolRes, 'select':layersData[bVolRes]['select'], 'from':layersData[bVolRes]['from']},
						bVolNonRes:{'with':withbVolNonRes, 'select':layersData[bVolNonRes]['select'], 'from':layersData[bVolNonRes]['from']},
						heatRes:{'with':withHeatRes, 'select':layersData[heatRes]['select'], 'from':layersData[heatRes]['from']},
						heatNonRes:{'with':withHeatNonRes, 'select':layersData[heatNonRes]['select'], 'from':layersData[heatNonRes]['from']}}

	return layersQueryData

def createQueryDataStatsNutsLau(nuts, year, type):
	# 'with' parts
	withPop = constructWithPartEachLayerNutsLau(nuts=nuts, year=year, layer=popDe, type=type, fromPart=layersData[popDe]['from'])
	withHeat = constructWithPartEachLayerNutsLau(nuts=nuts, year=year, layer=heatDe, type=type, fromPart=layersData[heatDe]['from'])
	withWwtp = constructWithPartEachLayerNutsLau(nuts=nuts, year=year, layer=wwtp, type=type, fromPart=layersData[wwtp]['from'])
	withGrass = constructWithPartEachLayerNutsLau(nuts=nuts, year=year, layer=grass, type=type, fromPart=layersData[grass]['from'])
	withGrassRes = constructWithPartEachLayerNutsLau(nuts=nuts, year=year, layer=grassRes, type=type, fromPart=layersData[grassRes]['from'])
	withGrassNonRes = constructWithPartEachLayerNutsLau(nuts=nuts, year=year, layer=grassNonRes, type=type, fromPart=layersData[grassNonRes]['from'])
	withbVolTot = constructWithPartEachLayerNutsLau(nuts=nuts, year=year, layer=bVolTot, type=type, fromPart=layersData[bVolTot]['from'])
	withbVolRes = constructWithPartEachLayerNutsLau(nuts=nuts, year=year, layer=bVolRes, type=type, fromPart=layersData[bVolRes]['from'])
	withbVolNonRes = constructWithPartEachLayerNutsLau(nuts=nuts, year=year, layer=bVolNonRes, type=type, fromPart=layersData[bVolNonRes]['from'])
	withHeatRes = constructWithPartEachLayerNutsLau(nuts=nuts, year=year, layer=heatRes, type=type, fromPart=layersData[heatRes]['from'])
	withHeatNonRes = constructWithPartEachLayerNutsLau(nuts=nuts, year=year, layer=heatNonRes, type=type, fromPart=layersData[heatNonRes]['from'])

	# Dictionary with query data
	layersQueryData = {heatDe:{'with':withHeat, 'select':layersData[heatDe]['select'], 'from':layersData[heatDe]['from']},
						popDe:{'with':withPop, 'select':layersData[popDe]['select'], 'from':layersData[popDe]['from']},
						wwtp:{'with':withWwtp, 'select':layersData[wwtp]['select'], 'from':layersData[wwtp]['from']},
						grass:{'with':withGrass, 'select':layersData[grass]['select'], 'from':layersData[grass]['from']},
						grassRes:{'with':withGrassRes, 'select':layersData[grassRes]['select'], 'from':layersData[grassRes]['from']},
						grassNonRes:{'with':withGrassNonRes, 'select':layersData[grassNonRes]['select'], 'from':layersData[grassNonRes]['from']},
						bVolTot:{'with':withbVolTot, 'select':layersData[bVolTot]['select'], 'from':layersData[bVolTot]['from']},
						bVolRes:{'with':withbVolRes, 'select':layersData[bVolRes]['select'], 'from':layersData[bVolRes]['from']},
						bVolNonRes:{'with':withbVolNonRes, 'select':layersData[bVolNonRes]['select'], 'from':layersData[bVolNonRes]['from']},
						heatRes:{'with':withHeatRes, 'select':layersData[heatRes]['select'], 'from':layersData[heatRes]['from']},
						heatNonRes:{'with':withHeatNonRes, 'select':layersData[heatNonRes]['select'], 'from':layersData[heatNonRes]['from']}}

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

def constructWithPartEachLayerHectare(geometry, year, layer, fromPart):
	if layer == settings.WWTP:
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
		if layer == popDe or layer == heatDe:
			w += 'AND date = to_date(\''+ str(year) +'\',\'YYYY\')) '
		else:
			w += ') '

	return w

def constructWithPartEachLayerNutsLau(nuts, year, layer, type, fromPart):
	# Get name of table to select nuts/lau
	if type == 'nuts':
		id_type = 'nuts_id'
	else:
		id_type = 'comm_id'

	if layer == wwtp:
		w = "nutsSelection as (SELECT geom from geo."+type+" where "+id_type+" in ("+nuts+") and year = to_date('2013','YYYY')), " +\
				""+fromPart+" as (SELECT sum(power) as power, sum(capacity) as capacityPerson " +\
				"from nutsSelection, geo.wwtp tbl_wwtp " +\
				"where st_within(tbl_wwtp.geom, st_transform(nutsSelection.geom,3035)) " +\
				"and date = to_date('2015','YYYY'))"
	elif layer == heatDe or layer == popDe:
		w = ""+fromPart+" as (SELECT sum(stat."+layersData[layer]['tablename']+"_"+type+"_test.sum) AS sum, " +\
					"sum(stat."+ layersData[layer]['tablename'] +"_"+type+"_test.count) AS count " +\
				"FROM stat."+layersData[layer]['tablename']+"_"+type+"_test " +\
				"WHERE stat."+layersData[layer]['tablename']+"_"+type+"_test."+id_type+" IN ("+nuts+")) "
	else:
		w = ""+fromPart+" as (SELECT sum(stat."+layersData[layer]['tablename']+"_"+type+".sum) AS sum, " +\
					"sum(stat."+ layersData[layer]['tablename'] +"_"+type+".count) AS count " +\
				"FROM stat."+layersData[layer]['tablename']+"_"+type+" " +\
				"WHERE stat."+layersData[layer]['tablename']+"_"+type+"."+id_type+" IN ("+nuts+")) "

	return w

def transform_nuts_list(nuts):
		# Store nuts in new custom list
		nutsPayload = []
		for n in nuts:
			n = n[:4]
			if n not in nutsPayload:
				nutsPayload.append(str(n))

		# Adapt format of list for the query
		nutsListQuery = str(nutsPayload)
		nutsListQuery = nutsListQuery[1:] # Remove the left hook
		nutsListQuery = nutsListQuery[:-1] # Remove the right hook

		return nutsListQuery

def adapt_nuts_list(nuts):
		# Store nuts in new custom list
		nutsPayload = []
		for n in nuts:
			if n not in nutsPayload:
				nutsPayload.append(str(n))

		# Adapt format of list for the query
		nutsListQuery = str(nutsPayload)
		nutsListQuery = nutsListQuery[1:] # Remove the left hook
		nutsListQuery = nutsListQuery[:-1] # Remove the right hook

		return nutsListQuery

def createAllLayers(layers):
	allLayers = []
	for l in layers:
		allLayers.append(l)
		allLayers.append(l+'_ha')
		allLayers.append(l+'_nuts3')
		allLayers.append(l+'_nuts2')
		allLayers.append(l+'_nuts1')
		allLayers.append(l+'_nuts0')
		allLayers.append(l+'_lau2')

	return allLayers

def getTypeScale(layers):
	if layers:		
		if layers[0].endswith('lau2'):
			return 'lau'
		else:
			return 'nuts'
	else:
		return ''


def adapt_layers_list(layersPayload, type, allLayers):
	layers = []
	if type == 'lau':
		for layer in layersPayload:
			if layer in allLayers:
				layer = layer[:-5] # Remove the type for each layer 
				layers.append(layer)
	elif type == 'ha':
		for layer in layersPayload:
			if layer in allLayers:
				layer = layer[:-3] # Remove the type for each layer 
				layers.append(layer)
	else:
		for layer in layersPayload:
			if layer in allLayers:
				layer = layer[:-6] # Remove the type for each layer 
				layers.append(layer)

	return layers

def removeScaleLayers(layersList, type):
	layers = []
	if type == 'lau':
		for layer in layersList:
			layer = layer[:-5] # Remove the type for each layer 
			layers.append(layer)
	elif type == 'ha':
		for layer in layersList:
			layer = layer[:-3] # Remove the type for each layer 
			layers.append(layer)
	else:
		for layer in layersList:
			layer = layer[:-6] # Remove the type for each layer 
			layers.append(layer)

	return layers

def layers_filter(layersPayload, list):
	layers = []
	for l in layersPayload:
		if l not in list:
			layers.append(l)

	return layers