from app.models.indicators import *
from app.constants import CRS_USER_GEOMETRY, NUTS_VAlUES

def createQueryDataStatsHectares(layer, geometry, year):
	return {
			'with': constructWithPartEachLayerHectare(geometry=geometry, year=year, layer=layer, fromPart='stat_' + layer),
			'indicators':layersData[layer]['indicators'],
			'schema_hectare':layersData[layer]['schema_hectare'],'geo_column':layersData[layer]['geo_column'], 'from':layersData[layer]['tablename'],
			'from_indicator_name':'stat_' + layer, 'table_type':layersData[layer]['table_type']
		}

def createQueryDataStatsNutsLau(layer, nuts, year, scale_level):
	return {
				'with':constructWithPartEachLayerNutsLau(nuts=nuts, year=year, layer=layer, scale_level=scale_level, fromPart='stat_' + layer), 
				'from_indicator_name':'stat_' + layer, 'indicators':layersData[layer]['indicators'], 'table_type':layersData[layer]['table_type']
			}

def constructWithPartEachLayerHectare(geometry, year, layer, fromPart):
	if len(layersData[layer]['indicators']) == 0:
		return ' '
	query = ''
	layer_table_name = layersData[layer]['schema_hectare']+"."+layersData[layer]['tablename']
	query_select = 'SELECT '
	if layersData[layer]['table_type'] == 'vector':
		for indic in layersData[layer]['indicators']:
			if 'select' in indic:
				query_select+= 'sum(' +layer_table_name+'.' +indic['select'] + ') as '+layer + indic['name'] + ','


		query_select = query_select[:-1]
		query += fromPart+" as ("
		query += query_select
		query += " FROM "+layer_table_name
		query += " WHERE "+ "ST_Within("+layer_table_name+"."+layersData[layer]['geo_column']+",st_transform(st_geomfromtext('"+ geometry +"'::text,"+CRS_USER_GEOMETRY+")," + layersData[layer]['crs'] + "))"
		query += ")"
	else:
		for indic in layersData[layer]['indicators']:
			if 'select' in indic:
				query_select += "(((ST_SummaryStatsAgg(ST_Clip("+ layersData[layer]['tablename'] + ".rast, 1, st_transform(st_geomfromtext('" + geometry + "'::text,"+CRS_USER_GEOMETRY+")," + layersData[layer]['crs'] + "),false),true,0)))."+indic['select']+") as "+layersData[layer]['tablename'] + indic['name'] + ','
		query_select = query_select[:-1]
		query += fromPart+' AS ( '
		query += query_select
		query +=  " FROM "+ layer_table_name
		query += "  WHERE ST_Intersects(" + layersData[layer]['tablename'] + ".rast, st_transform(st_geomfromtext('"+ geometry +"'::text,"+CRS_USER_GEOMETRY+")," + layersData[layer]['crs'] + ")) "
		query += ")"
				
	return query

def constructWithPartEachLayerNutsLau(nuts, year, layer, scale_level, fromPart):
	# Get name of table to select nuts/lau
	if len(layersData[layer]['indicators']) == 0:
		return ' '
	query = ''
	if scale_level in NUTS_VAlUES:
		id_type = 'nuts_id'
		name_type = 'nuts'
	else:
		id_type = 'comm_id'
		name_type = 'lau'

	query_from_part = fromPart+" as ("
	nust_select_name = "nutsSelection_"+ layer
	nuts_selection =  nust_select_name +" as (SELECT geom from geo."+name_type+" where "+id_type+" in ("+nuts+")), "
	layer_table_name = layersData[layer]['schema']+"."+layersData[layer]['tablename']
	query_select = 'SELECT '

	
	if layersData[layer]['schema'] == 'stat' and layersData[layer]['tablename'] != 'wwtp' and layersData[layer]['tablename'] != 'industrial_database':
		layer_table_name += '_'+name_type
	for indic in layersData[layer]['indicators']:
		if 'select' in indic:
			query_select+= 'sum(' +layer_table_name+'.' +indic['select'] + ') as '+layer + indic['name'] + ','

	query_select = query_select[:-1]


	if layersData[layer]['table_type'] == 'vector':
		query += nuts_selection
		query += query_from_part 
		query += query_select
		query += " from " + nust_select_name + ", "+layer_table_name
		query += " where st_within("+layer_table_name+"."+layersData[layer]['geo_column']+", st_transform("+nust_select_name+".geom,"+layersData[layer]['crs']+"))) "
	else:
		query += query_from_part
		query += query_select
		query += " FROM "+layer_table_name
		query += " WHERE "+layer_table_name+"."+id_type+" IN ("+nuts+") ) "
				
	return query
