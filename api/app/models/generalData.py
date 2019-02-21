from app.models.indicators import *
from app.constants import CRS_USER_GEOMETRY, NUTS_VAlUES, NUTS_LAU_LEVELS, CRS_NUTS,CRS_LAU,LAU_TABLE


def constructWithPartEachLayerHectare(geometry, year, layer, scale_level):
	if len(layersData[layer]['indicators']) == 0 and scale_level not in layersData[layer]['data_lvl']:
		return ' '
	query = ''
	layer_table_name = layersData[layer]['schema_hectare']+"."+layersData[layer]['tablename']
	query_select = 'SELECT '
	from_part = 'stat_' + layer
	scalelvl_column = ''
	if 'scalelvl_column' in layersData[layer]:
		scalelvl_column = layersData[layer]['scalelvl_column']
	if layersData[layer]['table_type'] == vector_type:
		for indic in layersData[layer]['indicators']:
			if 'table_column' in indic:
				query_select+=get_indicator_as_query(indic,layer_table_name,layer,scalelvl_column, scale_level)
				

		query_select = query_select[:-1]
		query += from_part+" as ("
		query += query_select
		query += " FROM "+layer_table_name
		
		if 'level_of_data' in layersData[layer] and NUTS_LAU_LEVELS[layersData[layer]['level_of_data']] < NUTS_LAU_LEVELS[scale_level]:
			query += " WHERE "+ "ST_Intersects(st_transform(st_geomfromtext('"+ geometry +"'::text,"+CRS_USER_GEOMETRY+")," + layersData[layer]['crs'] + "),"+layer_table_name+"."+layersData[layer]['geo_column']+")"
		else:
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
		query += "  WHERE ST_Intersects(st_transform(st_geomfromtext('"+ geometry +"'::text,"+CRS_USER_GEOMETRY+")," + layersData[layer]['crs'] + ")," + layersData[layer]['tablename'] + ".rast)) "+agg_summary_stat
		query += ")"
				
	return query

def constructWithPartEachLayerNutsLau(nuts, year, layer, scale_level):
	# Get name of table to select nuts/lau
	year='2013'
	if len(layersData[layer]['indicators']) == 0 and scale_level not in layersData[layer]['data_lvl']:
		return ' '
	query = ''
	name_type = ''
	scalelvl_column=''
	nust_select_name = "nutsSelection_"+ layer
	nuts_selection = None
	if scale_level in NUTS_VAlUES:
		scale_level_crs = CRS_NUTS
		scale_level_name = 'nuts_id'
		name_type = 'nuts'
		fk_column_id = 'fk_nuts_gid'
		nuts_selection =  nust_select_name +" as (SELECT geom as geom from geo."+name_type+" where "+name_type+".year = date('"+year+"-01-01') and "+scale_level_name+"  in ("+nuts+")), "
	else:
		scale_level_crs = CRS_LAU
		scale_level_name = 'comm_id'
		name_type = 'lau'
		fk_column_id = 'fk_lau_gid'
		nuts_selection =  nust_select_name +" as (SELECT st_transform(geom,4326) as geom from public."+LAU_TABLE+" where "+scale_level_name+"  in ("+nuts+")), "
	if 'scalelvl_column' in layersData[layer]:
		scalelvl_column = layersData[layer]['scalelvl_column']

	



	#TODO: Make a nuts selection like heatload with within where clause in nuts selection. Do not use geom! Too slow




	from_part = 'stat_' + layer
	query_from_part = from_part+" as ("
	layer_table_name = layersData[layer]['schema_scalelvl']+"."+layersData[layer]['tablename']
	query_select = 'SELECT '

	
	if layersData[layer]['table_type'] == 'raster' and layersData[layer]['data_aggregated']: #(layersData[layer]['tablename'] != 'wwtp' or layersData[layer]['tablename'] != 'industrial_database' or layersData[layer]['tablename'] != 'wind_50m'):
		layer_table_name += '_'+name_type
	
	for indic in layersData[layer]['indicators']:
		if 'table_column' in indic:
			""" if 'diss_agg_method' in indic and indic['diss_agg_method'] == 'NUTS_result' and check_if_agg_or_dis_method(layer, scale_level):
				get_dis_query(indic, layer_table_name, layer,scale_level_name)
			else: """
			query_select+=get_indicator_as_query(indic, layer_table_name, layer,scalelvl_column,scale_level)

	query_select = query_select[:-1]


	if layersData[layer]['data_aggregated'] == False:
		query += nuts_selection
		query += query_from_part 
		query += query_select

		print('nuts_selection',nuts_selection)
		query_from =" from " + nust_select_name + ", "+layer_table_name
		query += query_from


		if check_if_agg_or_dis_method(layer, scale_level):
			query += " where st_within(st_centroid("+nust_select_name+".geom),st_transform("+layer_table_name+"."+layersData[layer]['geo_column']+","+scale_level_crs+"))) "			
		else:
			query += " where st_within(st_transform("+layer_table_name+"."+layersData[layer]['geo_column']+","+scale_level_crs+"), "+nust_select_name+".geom)) "
	else:
		query += query_from_part
		query += query_select
		if scale_level in NUTS_VAlUES:
			query += " FROM "+layer_table_name + ", geo." + name_type
			query += " WHERE "+layer_table_name+"."+fk_column_id+" = geo."+name_type+".gid and "+name_type+".year = date('"+year+"-01-01') and "+layer_table_name+"."+scale_level_name+"  IN ("+nuts+") ) "
		else:
			query += " FROM "+layer_table_name + ", public." + LAU_TABLE
			query += " WHERE "+layer_table_name+"."+fk_column_id+" = public."+LAU_TABLE+".gid and "+layer_table_name+"."+scale_level_name+"  IN ("+nuts+") ) "

	return query


def get_indicator_as_query(indic, layer_table_name, layer, scale_level_name, scale_level):
	agg_method = 'sum'
	distinct=''
	indic_id = 'as '+layer + indic['indicator_id'] + ','
	query_calcul = layer_table_name+'.' +indic['table_column'] + ')' + indic_id
	if layer == 'agricultural_residues_view':
		distinct = 'distinct '

	switcher = {
		'sum':'sum('+query_calcul,
		'min':'min('+query_calcul,
		'max':'max('+query_calcul,
		'avg':'avg('+query_calcul,
		'mean_weighted_cell':'sum('+layer_table_name+'.count*'+layer_table_name+'.' +indic['table_column']+')/sum('+layer_table_name+'.count) '+indic_id,
		'mean_simple':'avg('+query_calcul,
		'NUTS_result':'sum('+layer_table_name+'.'+indic['table_column']+')/count('+distinct+layer_table_name+'.'+scale_level_name+') '+ indic_id
	}
	
	if 'agg_method' in indic:
		agg_method = indic['agg_method']
	if 'diss_agg_method' in indic and check_if_agg_or_dis_method(layer, scale_level):
		agg_method = indic['diss_agg_method']
	quer = switcher.get(agg_method,switcher['sum'])

	return quer
				
def check_if_agg_or_dis_method(layer,scale_level):
	return 'level_of_data' in layersData[layer] and NUTS_LAU_LEVELS[layersData[layer]['level_of_data']] < NUTS_LAU_LEVELS[scale_level]
	 