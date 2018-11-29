from indicators import *

def createQueryDataStatsHectares(layer, geometry, year):
	return {
			'with': constructWithPartEachLayerHectare(geometry=geometry, year=year, layer=layer, fromPart='stat_' + layer),
			'indicators':layersData[layer]['indicators'],
			'schema_hectare':layersData[layer]['schema_hectare'],'geo_column':layersData[layer]['geo_column'], 'from':layersData[layer]['tablename'],
			'from_indicator_name':'stat_' + layer
		}

def createQueryDataStatsNutsLau(layer,nuts, year, type):
	return {
				'with':constructWithPartEachLayerNutsLau(nuts=nuts, year=year, layer=layer, type=type, fromPart='stat_' + layersData[layer]['tablename']), 
				'from_indicator_name':'stat_' + layersData[layer]['tablename'], 'indicators':layersData[layer]['indicators']
			}

def constructWithPartEachLayerHectare(geometry, year, layer, fromPart):
	
	query = ''
	layer_table = layersData[layer]['schema_hectare']+"."+layersData[layer]['tablename']
	query_select = 'SELECT '
	if layer in [electricityCo2EmisionsFactor,indSitesExc,geothermalPotHeatCond, wwtpCapacity,wwtpPower,indSitesEm]:
		for indic in layersData[layer]['indicators']:
			if 'select' in indic:
				query_select+= 'sum(' +layer_table+'.' +indic['select'] + ') as '+layer + indic['name'] + ','


		query_select = query_select[:-1]
		query += fromPart+" as ("
		query += query_select
		query += " FROM "+layer_table
		query += " WHERE "+ "ST_Within("+layer_table+"."+layersData[layer]['geo_column']+",st_transform(st_geomfromtext('"+ geometry +"'::text,"+layersData[layer]['crs']+")," + str(constants.CRS) + "))"
		query += ")"
	else:
		for indic in layersData[layer]['indicators']:
			if 'select' in indic:
				query_select += "(((ST_SummaryStatsAgg(ST_Clip("+ layersData[layer]['tablename'] + ".rast, 1, st_transform(st_geomfromtext('" + geometry + "'::text,"+layersData[layer]['crs']+")," + str(constants.CRS) + "),false),true,0)))."+indic['select']+") as "+layersData[layer]['tablename'] + indic['name'] + ','
		query_select = query_select[:-1]
		query += fromPart+' AS ( '
		query += query_select
		query +=  " FROM "+ layer_table
		query += "  WHERE ST_Intersects(" + layersData[layer]['tablename'] + ".rast, st_transform(st_geomfromtext('"+ geometry +"'::text,4326)," + str(constants.CRS) + ")) "
		query += ")"
				
	print(query)
	return query

def constructWithPartEachLayerNutsLau(nuts, year, layer, type, fromPart):
	
	# Get name of table to select nuts/lau
	query = ''
	if type == 'nuts':
		id_type = 'nuts_id'
	else:
		id_type = 'comm_id'
	if layer == electricityCo2EmisionsFactor:
		id_type = 'nuts_code'


	query_from_part = fromPart+" as ("
	nust_select_name = "nutsSelection_"+ layer
	nuts_selection =  nust_select_name +" as (SELECT geom from geo."+type+" where "+id_type+" in ("+nuts+")), "
	layer_table = layersData[layer]['schema']+"."+layersData[layer]['tablename']
	geom_name = 'geom'
	transformed_geom_id = '3035'
	query_select = 'SELECT '
	query_from = ' FROM '
	layer_table
	suffix_table = ''
	if layersData[layer]['schema'] == 'stat':
		layer_table += '_'+type
	for indic in layersData[layer]['indicators']:
		if 'select' in indic:
			query_select+= 'sum(' +layer_table+'.' +indic['select'] + ') as '+layersData[layer]['tablename'] + indic['name'] + ','
	query_select = query_select[:-1]

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
		query += nuts_selection
		query += query_from_part
		query += query_select
		query += from_q
		query += " where st_within("+layer_table+"."+geom_name+", st_transform("+nust_select_name+".geom,"+transformed_geom_id+"))) "
	else:
		query += query_from_part
		query += query_select
		query += " FROM "+layer_table
		query += " WHERE "+layer_table+"."+id_type+" IN ("+nuts+") ) "
				
	print(query)
	return query
