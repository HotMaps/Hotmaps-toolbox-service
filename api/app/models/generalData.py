from indicators import *

def createQueryDataStatsHectares(layer, geometry, year):
	return {
			'with': constructWithPartEachLayerHectare(geometry=geometry, year=year, layer=layer, fromPart=layersData[layer]['from']),
			'from':layersData[layer]['from'], 'indicators':layersData[layer]['indicators']
		}

def createQueryDataStatsNutsLau(layer,nuts, year, type):
	return {
				'with':constructWithPartEachLayerNutsLau(nuts=nuts, year=year, layer=layer, type=type, fromPart=layersData[layer]['from']), 
				'from':layersData[layer]['from'], 'indicators':layersData[layer]['indicators']
			}

def constructWithPartEachLayerHectare(geometry, year, layer, fromPart):
	if layer == wwtpCapacity or layer == wwtpPower:
		w = ''+fromPart+' AS (SELECT '
		if layer == wwtpCapacity:
			w += 'sum(capacity) as capacityPerson '
		else:
			w += 'sum(power) as power '

		w += ' FROM ' + \
		' public.'+ layersData[layer]['tablename'] +'' + \
		' WHERE' + \
		' ST_Within(public.'+ layersData[layer]['tablename'] +'.geometry,st_transform(st_geomfromtext(\''+ geometry +'\'::text,4326),' + str(constants.CRS) + ')) ' + \
		') '
	elif layer == indSitesEm:
		w = ''+fromPart+' AS (SELECT ' + \
		' sum(emissions_ets_2014) as sum ' + \
		' FROM ' + \
		' public.'+ layersData[layer]['tablename'] + \
		' WHERE' + \
		' ST_Within(public.'+ layersData[layer]['tablename'] +'.geom,st_transform(st_geomfromtext(\''+ geometry +'\'::text,4326),4326))) '

	elif layer == geothermalPotHeatCond:
		w = ''+fromPart+' AS (SELECT ' + \
			' SUM(CAST(heat_cond as DECIMAL(9,2)) * CAST(ST_Area(geometry) as DECIMAL(9,2))) / SUM(ST_Area(geometry)) as sum ' + \
			' FROM ' + \
			' public.'+ layersData[layer]['tablename'] + \
			' WHERE' + \
			' ST_Within(public.'+ layersData[layer]['tablename'] +'.geometry,st_transform(st_geomfromtext(\''+ geometry +'\'::text,4326),4326))) '

	elif layer == indSitesExc:
		w = ''+fromPart+' AS (SELECT ' + \
		' sum(excess_heat_100_200c) as sum1, sum(excess_heat_200_500c) as sum2, sum(excess_heat_500c) as sum3, sum(excess_heat_total) as total ' + \
		' FROM ' + \
		' public.'+ layersData[layer]['tablename'] + \
		' WHERE' + \
		' ST_Within(public.'+ layersData[layer]['tablename'] +'.geom,st_transform(st_geomfromtext(\''+ geometry +'\'::text,4326),4326))) '
	elif layer == electricityCo2EmisionsFactor:
		w = ''+fromPart+' AS (SELECT ' + \
			' sum(value) as sum1, sum(unit) as sum2,' + \
			' FROM ' + \
			' public.'+ layersData[layer]['tablename'] + \
			' WHERE' + \
			' ST_Within(public.'+ layersData[layer]['tablename'] +'.geometry,st_transform(st_geomfromtext(\''+ geometry +'\'::text,4326),4326))) '
	else:
		w = ''+fromPart+' AS ( SELECT (' + \
		' ((ST_SummaryStatsAgg(ST_Clip('+ layersData[layer]['tablename'] + '.rast, 1, ' + \
		' st_transform(st_geomfromtext(\'' + \
						geometry + '\'::text,4326),' + str(constants.CRS) + '),false),true,0))).*) as stats ' + \
		' FROM ' + \
		' geo.'+ layersData[layer]['tablename'] + \
		' WHERE' + \
		' ST_Intersects('+ layersData[layer]['tablename'] + '.rast,' + \
		' st_transform(st_geomfromtext(\''+ geometry +'\'::text,4326),' + str(constants.CRS) + ')) '
		if layer == popDe or layer == heatDe:
			w += ') '
		else:
			w += ') '
		
	return w

def constructWithPartEachLayerNutsLau(nuts, year, layer, type, fromPart):
	
	# Get name of table to select nuts/lau
	query = ''
	if type == 'nuts':
		id_type = 'nuts_id'
	else:
		id_type = 'comm_id'
	query_from_part = fromPart+" as ("
	query_select = "SELECT * "

	nust_select_name = "nutsSelection_"+ layer
	nuts_selection =  nust_select_name +" as (SELECT geom from geo."+type+" where "+id_type+" in ("+nuts+")), "
	layer_table = layersData[layer]['schema']+"."+layersData[layer]['tablename']
	geom_name = 'geom'
	transformed_geom_id = '3035'
	



	if 'custom_select' in layersData[layer]:
		query_select = layersData[layer]['custom_select']

	if layer == geothermalPotHeatCond or layer == wwtpCapacity or layer == wwtpPower:
		geom_name = 'geometry'

	if layer == wwtpCapacity or layer == wwtpPower:
		transformed_geom_id = '3035'
	elif layer == indSitesEm or layer == geothermalPotHeatCond or layer == indSitesExc:
		transformed_geom_id = '4326'
	
	if layer == wwtpCapacity or layer == wwtpPower or layer == geothermalPotHeatCond or layer == indSitesExc:
		from_q = " from " + nust_select_name + ", "+layer_table
	elif layer == indSitesEm:
		from_q = "from " + layer_table

	if layer == wwtpCapacity or layer == wwtpPower or layer == geothermalPotHeatCond or layer == indSitesExc or layer == indSitesEm:
		sel = ''
		for indic in layersData[layer]['indicators']:
			sel += indic['select']+','
		print(sel)
		query += nuts_selection
		query += query_from_part
		query += query_select
		query += from_q
		query += " where st_within("+layer_table+"."+geom_name+", st_transform("+nust_select_name+".geom,"+transformed_geom_id+"))) "
	elif layer == electricityCo2EmisionsFactor:
		query += nuts_selection
		query += query_from_part
		query += query_select
		query += "from " + layer_table
		query += " where "+layer_table+".nuts_code  in ("+nuts+")) "
	else:
		query += query_from_part
		query += query_select
		query += " FROM "+layer_table+"_"+type
		query += " WHERE "+layer_table+"_"+type+"."+id_type+" IN ("+nuts+") ) "
				
	print(query)
	return query
