from app.constants import nuts0,nuts1,nuts2,nuts3,lau2,hectare_name

# LAYERS
""" POPULATION_TOT = constants.POPULATION_TOT
HEAT_DENSITY_TOT = constants.HEAT_DENSITY_TOT
wwtp = constants.WWTP
WWTP_CAPACITY = constants.WWTP_CAPACITY
WWTP_POWER = constants.WWTP_POWER
grass = constants.GRASS_FLOOR_AREA_TOT
GRASS_FLOOR_AREA_RES = constants.GRASS_FLOOR_AREA_RES
GRASS_FLOOR_AREA_NON_RES = constants.GRASS_FLOOR_AREA_NON_RES
BUILDING_VOLUMES_TOT = constants.BUILDING_VOLUMES_TOT
BUILDING_VOLUMES_RES = constants.BUILDING_VOLUMES_RES
BUILDING_VOLUMES_NON_RES = constants.BUILDING_VOLUMES_NON_RES
LAND_SURFACE = 'land_surface_temperature'
HEAT_DENSITY_RES = constants.HEAT_DENSITY_RES
HEAT_DENSITY_NON_RES = constants.HEAT_DENSITY_NON_RES
indSites = constants.INDUSTRIAL_SITES
INDUSTRIAL_SITES_EMISSIONS = constants.INDUSTRIAL_SITES_EMISSIONS
INDUSTRIAL_SITES_EXCESS_HEAT = constants.INDUSTRIAL_SITES_EXCESS_HEAT
BIOMASS_POTENTIAL = constants.BIOMASS_POTENTIAL
MUNICIPAL_SOLID_WASTE = constants.MUNICIPAL_SOLID_WASTE
WIND_POTENTIAL = constants.WIND_POTENTIAL
SOLAR_POTENTIAL = constants.SOLAR_POTENTIAL
GEOTHERMAL_POTENTIAL_HEAT_COND = constants.GEOTHERMAL_POTENTIAL_HEAT_COND2
ELECRICITY_CO2_EMISSION_FACTOR = constants.ELECRICITY_CO2_EMISSION_FACTOR
hdd = constants.HDD_CUR
cdd = constants.CDD_CUR """

POPULATION_TOT = 'pop_tot_curr_density_tif'
HEAT_DENSITY_TOT = 'heat_tot_curr_density_tif'
HEAT_DENSITY_NON_RES = 'heat_nonres_curr_density_tif'
HEAT_DENSITY_RES = 'heat_res_curr_density_tif'
WWTP = 'wwtp'
WWTP_CAPACITY = 'wwtp_capacity'
WWTP_POWER = 'wwtp_power'
GRASS_FLOOR_AREA_TOT = 'gfa_tot_curr_density_tif'
GRASS_FLOOR_AREA_RES = 'gfa_res_curr_density_tif'
GRASS_FLOOR_AREA_NON_RES = 'gfa_nonres_curr_density_tif'
BUILDING_VOLUMES_RES = 'vol_res_curr_density_tif'
BUILDING_VOLUMES_TOT = 'vol_tot_curr_density_tif'
BUILDING_VOLUMES_NON_RES = 'vol_nonres_curr_density_tif'
INDUSTRIAL_SITES = 'industrial_database'
INDUSTRIAL_SITES_EMISSIONS = 'industrial_database_emissions'
INDUSTRIAL_SITES_EXCESS_HEAT = 'industrial_database_excess_heat'
BIOMASS_POTENTIAL = 'potential_biomass'
MUNICIPAL_SOLID_WASTE = 'potential_municipal_solid_waste'
WIND = 'wind_50m'
WIND_POTENTIAL = 'potential_wind'
SOLAR_POTENTIAL = 'solar_optimal_total'
#GEOTHERMAL_POTENTIAL_HEAT_COND = 'potential_shallowgeothermal_heat_cond'
GEOTHERMAL_POTENTIAL_HEAT_COND = 'shallow_geothermal_potential'
ELECRICITY_CO2_EMISSION_FACTOR = 'yearly_co2_emission'
HDD_CUR = 'hdd_curr_tif'
CDD_CUR = 'cdd_curr_tif'
ELECRICITY_MIX = 'stat.yearly_electricity_generation_mix'
LAND_SURFACE = 'land_surface_temperature'
AGRI_RES_VIEW = 'agricultural_residues_view'
SOLAR_RADIATION = 'solar_radiation'



stat = 'stat_'
vector_type = 'vector'
raster_type = 'raster'

stat_schema = 'stat'
public_schema = 'public'
geo_schema = 'geo'

geometry_column = 'geometry'
geom_column = 'geom'


# ALL DATA FOR THE STATS
layersData = {
	MUNICIPAL_SOLID_WASTE:{'tablename':MUNICIPAL_SOLID_WASTE,
			'from_indicator_name':stat + MUNICIPAL_SOLID_WASTE,
			'where':'',
            'schema_scalelvl': stat_schema,
            'schema_hectare': geo_schema,
            'crs': '3035',
            'geo_column': geometry_column,
			'table_type':vector_type,
			'data_lvl':[nuts3],
			'scalelvl_column':'code',
			'data_aggregated':True,'indicators':[
				{'table_column': 'value', 'unit': 'unit_1','indicator_id':'val'},
				
			]},
	SOLAR_RADIATION:{'tablename':SOLAR_RADIATION,
			'from_indicator_name':stat + SOLAR_RADIATION,
			'where':'',
            'schema_scalelvl': stat_schema,
            'schema_hectare': geo_schema,
            'crs': '3035',
            'geo_column': geometry_column,
			'table_type':raster_type,
			'data_lvl':[nuts0,nuts1,nuts2,nuts3,lau2,hectare_name],
			'data_aggregated':True,'indicators':[
				{'table_column': 'sum', 'unit': 'unit_1','indicator_id':'solar'},
				{'table_column': 'count', 'unit': 'unit_1','indicator_id':'count_cell'},
				{
					'reference_indicator_id_1': 'solar','reference_tablename_indicator_id_1':SOLAR_RADIATION, 
					'operator': '/',
					'reference_indicator_id_2':'count_cell','reference_tablename_indicator_id_2':POPULATION_TOT, 
					'unit':'MWh/person', 'indicator_id':SOLAR_RADIATION+'_per_'+POPULATION_TOT
				},
				
			]},
	HEAT_DENSITY_TOT:{'tablename':HEAT_DENSITY_TOT,
			'from_indicator_name':stat + HEAT_DENSITY_TOT,
			'where':'',
            'schema_scalelvl': stat_schema,
            'schema_hectare': geo_schema,
            'crs': '3035',
            'geo_column': geometry_column,
			'table_type':raster_type,
			'data_lvl':[nuts0,nuts1,nuts2,nuts3,lau2,hectare_name],
			'data_aggregated':True,'indicators':[
				{'table_column': 'sum', 'unit': 'MWh','indicator_id':'consumption'},
				{'table_column': 'count', 'unit': 'cells','indicator_id':'count_cell'},
				{'table_column': 'min', 'unit': 'MWh','indicator_id':'consumption_min'},
				{'table_column': 'max', 'unit': 'MWh','indicator_id':'consumption_max'},
				{'table_column': 'mean', 'unit': 'Blabla','indicator_id':'consumption_mean'},
				{
					'reference_indicator_id_1': 'consumption','reference_tablename_indicator_id_1':HEAT_DENSITY_TOT, 
					'operator': '/',
					'reference_indicator_id_2':'count_cell','reference_tablename_indicator_id_2':POPULATION_TOT, 
					'unit':'MWh/person', 'indicator_id':HEAT_DENSITY_TOT+'_per_'+POPULATION_TOT
				},
			]},
	POPULATION_TOT:{
		'tablename':POPULATION_TOT,
			'from_indicator_name':stat + POPULATION_TOT,
            'schema_scalelvl': stat_schema,
            'schema_hectare': geo_schema,
            'crs': '3035',
			'table_type':raster_type,
			'data_lvl':[nuts0,nuts1,nuts2,nuts3,lau2,hectare_name],
            'geo_column': geometry_column,
			'data_aggregated':True,'indicators':[
				{'table_column': 'sum', 'unit': 'person','indicator_id':'population'},
				{'table_column': 'count', 'unit': 'cells','indicator_id':'count_cell'},
				{'reference_indicator_id_1': 'population','reference_tablename_indicator_id_1':POPULATION_TOT, 'operator': '/','reference_indicator_id_2':'count_cell','reference_tablename_indicator_id_2':POPULATION_TOT, 'unit':'person/ha', 'indicator_id':'density'},
			]
			},
	WWTP:{'tablename':WWTP,
			'from_indicator_name':stat + WWTP,
            'schema_scalelvl': geo_schema,
            'schema_hectare': geo_schema,
            'geo_column': geom_column,
            'crs': '3035',
			'table_type':vector_type,
			'data_lvl':[nuts1,nuts2,nuts3,lau2,hectare_name],
			'data_aggregated':False,
			'indicators':[
				{'table_column': 'capacity', 'unit': 'kW','indicator_id':'power'},
				{'table_column': 'power', 'unit': 'Person equivalent','indicator_id':'capacity'},
			]
			},
WWTP_CAPACITY:{'tablename':WWTP_CAPACITY,
            'schema_scalelvl': public_schema,
            'schema_hectare': public_schema,
            'crs': '3035',
			'table_type':vector_type,
			'from_indicator_name':stat + WWTP_CAPACITY,
            'geo_column': geometry_column,
			'data_lvl':[nuts1,nuts2,nuts3,lau2,hectare_name],
			
			'data_aggregated':False,
			'indicators':[
				{'table_column': 'capacity', 'unit': 'Person equivalent','indicator_id':'capacity'},
	]},
	WWTP_POWER:{'tablename':WWTP_POWER,
            'schema_scalelvl': public_schema,
            'schema_hectare': public_schema,
            'geo_column': geometry_column,
            'crs': '3035',
			'table_type':vector_type,
			'data_lvl':[nuts1,nuts2,nuts3,lau2,hectare_name],
			'from_indicator_name':stat + WWTP_POWER,
			'data_aggregated':False,
			'indicators':[
				{'table_column': 'power', 'unit': 'kW','indicator_id':'power'},
			]
			},
	GRASS_FLOOR_AREA_TOT:{'tablename':GRASS_FLOOR_AREA_TOT,
            'schema_scalelvl': stat_schema,
            'schema_hectare': geo_schema,
            'geo_column': geometry_column,
            'crs': '3035',
			'table_type':raster_type,
			'data_lvl':[nuts0,nuts1,nuts2,nuts3,lau2,hectare_name],
			
			'from_indicator_name':stat + GRASS_FLOOR_AREA_TOT,
			'data_aggregated':True,'indicators':[
				{'table_column': 'sum', 'unit': 'm2','indicator_id':'density'},
				{'table_column': 'count', 'unit': 'cells','indicator_id':'cells'},
			]
			},
	GRASS_FLOOR_AREA_RES:{'tablename':GRASS_FLOOR_AREA_RES,
            'schema_scalelvl': stat_schema,
            'schema_hectare': geo_schema,
            'geo_column': geometry_column,
            'crs': '3035',
			'table_type':raster_type,
			'data_lvl':[nuts0,nuts1,nuts2,nuts3,lau2,hectare_name],
			
			'from_indicator_name':stat + GRASS_FLOOR_AREA_RES,
			'data_aggregated':True,'indicators':[
				{'table_column': 'sum', 'unit': 'm2','indicator_id':'density'},
				{'table_column': 'count', 'unit': 'cells','indicator_id':'cells'},
			]
			},
	GRASS_FLOOR_AREA_NON_RES:{'tablename':GRASS_FLOOR_AREA_NON_RES,
            'schema_scalelvl': stat_schema,
            'schema_hectare': geo_schema,
            'geo_column': geometry_column,
            'crs': '3035',
			'table_type':raster_type,
			'data_lvl':[nuts0,nuts1,nuts2,nuts3,lau2,hectare_name],
			
			'from_indicator_name': stat + GRASS_FLOOR_AREA_NON_RES,
			'data_aggregated':True,'indicators':[
				{'table_column': 'sum', 'unit': 'm2','indicator_id':'density'},
				{'table_column': 'count', 'unit': 'cells','indicator_id':'cells'}
			]
			},
	BUILDING_VOLUMES_TOT:{'tablename':BUILDING_VOLUMES_TOT,
            'schema_scalelvl': stat_schema,
            'schema_hectare': geo_schema,
            'geo_column': geometry_column,
            'crs': '3035',
			'table_type':raster_type,
			'data_lvl':[nuts0,nuts1,nuts2,nuts3,lau2,hectare_name],
			'from_indicator_name':stat + BUILDING_VOLUMES_TOT,
			'data_aggregated':True,'indicators':[
				{'table_column': 'sum', 'unit': 'm3','indicator_id':'value'},
				{'table_column': 'count', 'unit': 'cells','indicator_id':'cells'},
				{'reference_indicator_id_1': 'value','reference_tablename_indicator_id_1':BUILDING_VOLUMES_TOT, 'operator': '/','reference_indicator_id_2':'cells','reference_tablename_indicator_id_2':BUILDING_VOLUMES_TOT, 'unit':'person/ha', 'indicator_id':'density'},

				
			]
			},
	BUILDING_VOLUMES_RES:{'tablename':BUILDING_VOLUMES_RES,
            'schema_scalelvl': stat_schema,
            'schema_hectare': geo_schema,
            'geo_column': geometry_column,
            'crs': '3035',
			'table_type':raster_type,
			'data_lvl':[nuts0,nuts1,nuts2,nuts3,lau2,hectare_name],
			'from_indicator_name':stat + BUILDING_VOLUMES_RES,
			'data_aggregated':True,'indicators':[
				{'table_column': 'sum', 'unit': 'm3','indicator_id':'value'},
				{'table_column': 'count', 'unit': 'cells','indicator_id':'cells'},
				{'reference_indicator_id_1': 'value', 'reference_tablename_indicator_id_1':BUILDING_VOLUMES_RES, 'operator': '/','reference_indicator_id_2':'cells','reference_tablename_indicator_id_2':BUILDING_VOLUMES_RES, 'unit':'m3/ha', 'indicator_id':'density'},

			]
			},
	BUILDING_VOLUMES_NON_RES:{'tablename':BUILDING_VOLUMES_NON_RES,
			'from_indicator_name':stat + BUILDING_VOLUMES_NON_RES,
            'schema_scalelvl': stat_schema,
            'schema_hectare': geo_schema,
            'geo_column': geometry_column,
            'crs': '3035',
			'table_type':raster_type,
			'data_lvl':[nuts0,nuts1,nuts2,nuts3,lau2,hectare_name],			
			'data_aggregated':True,'indicators':[
				{'table_column':  'sum', 'unit': 'm3','indicator_id':'value'},
				{'reference_indicator_id_1': 'value', 'reference_tablename_indicator_id_1':BUILDING_VOLUMES_NON_RES, 'operator': '/','reference_indicator_id_2':'cells','reference_tablename_indicator_id_2':BUILDING_VOLUMES_NON_RES, 'unit':'m3/ha', 'indicator_id':'density'},
				{'table_column': 'count', 'unit': 'cells','indicator_id':'cells'}
			]
			},
	HEAT_DENSITY_RES:{'tablename':HEAT_DENSITY_RES,
			'from_indicator_name':stat + HEAT_DENSITY_RES,
            'schema_scalelvl': stat_schema,
            'schema_hectare': geo_schema,
            'geo_column': geometry_column,
            'crs': '3035',
			'table_type':raster_type,
			'data_lvl':[nuts0,nuts1,nuts2,nuts3,lau2,hectare_name],
			
			'data_aggregated':True,'indicators':[
				{'table_column': 'sum', 'unit': 'MWh','indicator_id':'value'},
				{'reference_indicator_id_1': 'value', 'reference_tablename_indicator_id_1':HEAT_DENSITY_RES, 'operator': '/','reference_indicator_id_2':'cells','reference_tablename_indicator_id_2':HEAT_DENSITY_RES, 'unit':'MWh/ha', 'indicator_id':'density'},
				{'table_column': 'count', 'unit': 'cells','indicator_id':'cells'}
			]
			},
	HEAT_DENSITY_NON_RES:{'tablename':HEAT_DENSITY_NON_RES,
			'from_indicator_name':stat + HEAT_DENSITY_NON_RES,
            'schema_scalelvl': stat_schema,
            'schema_hectare': geo_schema,
            'geo_column': geometry_column,
            'crs': '3035',
			'table_type':raster_type,
			'data_lvl':[nuts0,nuts1,nuts2,nuts3,lau2,hectare_name],
			
			'data_aggregated':True,'indicators':[
				{'table_column': 'sum', 'unit': 'MWh','indicator_id':'value'},
				{'reference_indicator_id_1': 'value', 'reference_tablename_indicator_id_1':HEAT_DENSITY_NON_RES, 'operator': '/','reference_indicator_id_2':'cells','reference_tablename_indicator_id_2':HEAT_DENSITY_NON_RES, 'unit':'MWh/ha', 'indicator_id':'density'},
				{'table_column': 'count', 'unit': 'cells','indicator_id':'cells'}
			]},
	GEOTHERMAL_POTENTIAL_HEAT_COND:{'tablename':GEOTHERMAL_POTENTIAL_HEAT_COND,
		   'from_indicator_name':stat + GEOTHERMAL_POTENTIAL_HEAT_COND,
            'schema_scalelvl': geo_schema,
            'schema_hectare': geo_schema,
            'geo_column': geom_column,
            'crs': '4326',
			'table_type':vector_type,
			'data_lvl':[nuts0,nuts1,nuts2,nuts3,lau2,hectare_name],
			'data_aggregated':False,'indicators':[
				{'table_column': 'sum', 'unit': 'MWh','indicator_id':'value'}
			]
		   },
	INDUSTRIAL_SITES_EMISSIONS:{'tablename':INDUSTRIAL_SITES_EMISSIONS,
			'from_indicator_name':stat + INDUSTRIAL_SITES_EMISSIONS,
            'schema_scalelvl': public_schema,
            'schema_hectare': public_schema,
            'geo_column': geom_column,
            'crs': '4326',
			'table_type':vector_type,
			'data_lvl':[nuts1,nuts2,nuts3,lau2,hectare_name],
			'data_aggregated':False,
			'indicators':[
				#{'table_column': 'sum/1000000', 'unit': 'Mtonnes/year','indicator_id':'value'}
			]
			},
	INDUSTRIAL_SITES_EXCESS_HEAT:{'tablename':INDUSTRIAL_SITES_EXCESS_HEAT,
			'from_indicator_name':stat + INDUSTRIAL_SITES_EXCESS_HEAT,
            'schema_scalelvl': public_schema,
            'schema_hectare': public_schema,
            'geo_column': geom_column,
            'crs': '4326',
			'table_type':vector_type,
			'data_lvl':[nuts1,nuts2,nuts3,lau2,hectare_name],
			
			'data_aggregated':False,'indicators':[
				{'table_column': 'excess_heat_100_200c', 'unit': 'GWh/year','indicator_id':'value1'},
				{'table_column': 'excess_heat_200_500c', 'unit': 'GWh/year','indicator_id':'value2'},
				{'table_column': 'excess_heat_500c', 'unit': 'GWh/year','indicator_id':'value3'},
				{'table_column': 'excess_heat_total', 'unit': 'GWh/year','indicator_id':'total'}
			]
			},
	SOLAR_POTENTIAL:{'tablename':SOLAR_POTENTIAL,
			'from_indicator_name':stat + SOLAR_POTENTIAL,
            'schema_scalelvl': stat_schema,
            'schema_hectare': geo_schema,
            'geo_column': geometry_column,
            'crs': '3035',
			'table_type':raster_type,
			'data_lvl':[nuts0,nuts1,nuts2,nuts3,lau2,hectare_name],	
			'data_aggregated':True,
			'indicators':[
				{'reference_indicator_id_1': 'value', 'reference_tablename_indicator_id_1':SOLAR_POTENTIAL, 'operator': '/','reference_indicator_id_2':'cells','reference_tablename_indicator_id_2':SOLAR_POTENTIAL, 'unit':'GWh/ha', 'indicator_id':'density'},
				{'table_column': 'sum', 'unit': 'GWh','indicator_id':'value'},
				{'table_column': 'count', 'unit': 'cells','indicator_id':'cells'},
			]
			},

	ELECRICITY_CO2_EMISSION_FACTOR:{'tablename':ELECRICITY_CO2_EMISSION_FACTOR,
            'schema_scalelvl': public_schema,
            'schema_hectare': public_schema,
            'geo_column': geom_column,
            'crs': '4258',
			'table_type':vector_type,
			'level_of_data':'NUTS 0',
			'from_indicator_name':stat + ELECRICITY_CO2_EMISSION_FACTOR,
			'data_lvl':[nuts0],
			'data_aggregated':True,'indicators':[
				{'table_column': 'value', 'unit': 'kg/MWh','indicator_id':'density'}
			]
			},
	HDD_CUR:{'tablename':HDD_CUR,
            'schema_scalelvl': stat_schema,
            'schema_hectare': geo_schema,
            'geo_column': geometry_column,
            'crs': '3035',
			'table_type':raster_type,
			'data_lvl':[nuts0,nuts1,nuts2,nuts3,lau2,hectare_name],	
		 	'from_indicator_name':stat + HDD_CUR,
			'data_aggregated':True,
			'indicators':[
				{'reference_indicator_id_1': 'value', 'reference_tablename_indicator_id_1':HDD_CUR, 'operator': '/','reference_indicator_id_2':'cells','reference_tablename_indicator_id_2':HDD_CUR, 'unit':'Kd', 'indicator_id':'density'},
				{'table_column': 'count', 'unit': 'cells','indicator_id':'cells'},
				{'table_column': 'sum', 'unit': '','indicator_id':'value'}
			]
		 },
	CDD_CUR:{	
		'tablename':CDD_CUR,
        'schema_scalelvl': stat_schema,
        'schema_hectare': geo_schema,
        'geo_column': geometry_column,
        'crs': '3035',
		'table_type':raster_type,
		'data_lvl':[nuts0,nuts1,nuts2,nuts3,lau2,hectare_name],	
		'from_indicator_name':stat + CDD_CUR,
		'data_aggregated':True,
		'indicators':[
			{'table_column': 'sum', 'unit': '','indicator_id':'value'},
			{'table_column': 'count', 'unit': 'cells','indicator_id':'cells'},
			{'reference_indicator_id_1': 'value', 'reference_tablename_indicator_id_1':CDD_CUR, 'operator': '/','reference_indicator_id_2':'cells','reference_tablename_indicator_id_2':CDD_CUR, 'unit':'Kd', 'indicator_id':'density'},
		]}
}
