from app.models.indicators import *
from app.constants import CRS_USER_GEOMETRY, NUTS_VAlUES


def constructWithPartEachLayerHectare(geometry, year, layer, scale_level):
	if len(layersData[layer]['indicators']) == 0 and scale_level not in layersData[layer]['data_lvl']:
		return ' '
	query = ''
	layer_table_name = layersData[layer]['schema_hectare']+"."+layersData[layer]['tablename']
	query_select = 'SELECT '
	from_part = 'stat_' + layer
	if layersData[layer]['table_type'] == vector_type:
		for indic in layersData[layer]['indicators']:

			if 'table_column' in indic:
				query_select+=get_indicator_as_query(indic,layer_table_name,layer)
				#query_select+= 'sum(' + layer_table_name + '.' + indic['table_column'] + ') as '+ layer + indic['indicator_id'] + ','

		query_select = query_select[:-1]
		query += from_part+" as ("
		query += query_select
		query += " FROM "+layer_table_name

		""" if 'level_of_data' in layersData[layer]:
			query += " WHERE "+ "ST_Intersects(st_transform(st_geomfromtext('"+ geometry +"'::text,"+CRS_USER_GEOMETRY+")," + layersData[layer]['crs'] + "),"+layer_table_name+"."+layersData[layer]['geo_column']+")"
		else: """
		query += " WHERE "+ "ST_Within("+layer_table_name+"."+layersData[layer]['geo_column']+",st_transform(st_geomfromtext('"+ geometry +"'::text,"+CRS_USER_GEOMETRY+")," + layersData[layer]['crs'] + "))"
		query += ")"
	else:
		agg_summary_stat = 'agg_summary_stat'
		for indic in layersData[layer]['indicators']:
			if 'table_column' in indic:
				query_select += agg_summary_stat + '.'+indic['table_column']+' as '+ layer + indic['indicator_id'] + ','
		query_select = query_select[:-1]
		query_select += " from (select (((ST_SummaryStatsAgg(ST_Clip("+ layersData[layer]['tablename'] + ".rast, 1, st_transform(st_geomfromtext('" + geometry + "'::text,"+CRS_USER_GEOMETRY+")," + layersData[layer]['crs'] + "),false),true,0))).*) as "+layersData[layer]['tablename']
		query += from_part+' AS ( '
		query += query_select
		query +=  " FROM "+ layer_table_name
		query += "  WHERE ST_Intersects(" + layersData[layer]['tablename'] + ".rast, st_transform(st_geomfromtext('"+ geometry +"'::text,"+CRS_USER_GEOMETRY+")," + layersData[layer]['crs'] + "))) "+agg_summary_stat
		query += ")"
				
	return query

def constructWithPartEachLayerNutsLau(nuts, year, layer, scale_level):
	# Get name of table to select nuts/lau
	year='2013'
	if len(layersData[layer]['indicators']) == 0 and scale_level not in layersData[layer]['data_lvl']:
		return ' '
	query = ''
	name_type = ''
	if scale_level in NUTS_VAlUES:
		scale_level_name = 'nuts_id'
		name_type = 'nuts'
		fk_column_id = 'fk_nuts_gid'
	else:
		scale_level_name = 'comm_id'
		name_type = 'lau'
		fk_column_id = 'fk_lau_gid'
	if 'scalelvl_column' in layersData[layer]:
		scale_level_name = layersData[layer]['scalelvl_column']
	
	nust_select_name = "nutsSelection_"+ layer
	nuts_selection =  nust_select_name +" as (SELECT geom from geo."+name_type+" where year = date('2013-01-01') and "+scale_level_name+"  in ("+nuts+")), "

	from_part = 'stat_' + layer
	query_from_part = from_part+" as ("
	layer_table_name = layersData[layer]['schema_scalelvl']+"."+layersData[layer]['tablename']
	query_select = 'SELECT '

	
	if layersData[layer]['table_type'] == 'raster' and layersData[layer]['data_aggregated']: #(layersData[layer]['tablename'] != 'wwtp' or layersData[layer]['tablename'] != 'industrial_database' or layersData[layer]['tablename'] != 'wind_50m'):
		layer_table_name += '_'+name_type
	
	for indic in layersData[layer]['indicators']:
		if 'table_column' in indic:
			query_select+=get_indicator_as_query(indic, layer_table_name, layer)
		#if 'table_column' in indic:
		#	query_select+= 'sum(' +layer_table_name+'.' +indic['table_column'] + ') as '+layer + indic['indicator_id'] + ','

	query_select = query_select[:-1]


	if layersData[layer]['data_aggregated'] == False:
		#print(layer)
		query += nuts_selection
		query += query_from_part 
		query += query_select
		query += " from " + nust_select_name + ", "+layer_table_name
		query += " where st_within("+layer_table_name+"."+layersData[layer]['geo_column']+", st_transform("+nust_select_name+".geom,"+layersData[layer]['crs']+"))) "
	else:
		query += query_from_part
		query += query_select
		query += " FROM "+layer_table_name + ", geo." + name_type
		query += " WHERE "+layer_table_name+"."+fk_column_id+" = geo."+name_type+".gid and year = date('"+year+"-01-01') and "+layer_table_name+"."+scale_level_name+"  IN ("+nuts+") ) "
				
	return query

def get_indicator_as_query(indic, layer_table_name, layer):
	agg_method = 'sum'
	indic_id = 'as '+layer + indic['indicator_id'] + ','
	query_calcul = layer_table_name+'.' +indic['table_column'] + ')' + indic_id 
	switcher = {
		'sum':'sum('+query_calcul,
		'min':'min('+query_calcul,
		'max':'max('+query_calcul,
		'avg':'avg('+query_calcul,
		'mean_weighted_cell':'sum('+layer_table_name+'.count*'+layer_table_name+'.' +indic['table_column']+')/sum('+layer_table_name+'.count) '+indic_id,
		'mean_simple':'avg('+query_calcul
	}
	
	if 'agg_method' in indic:
		agg_method = indic['agg_method']
	quer = switcher.get(agg_method,'sum')
	print(quer)
	return quer
				
def get_indicator_as_query_hectare(indic,layer_table_name,layer):
	pass