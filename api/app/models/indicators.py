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
	AGRI_RES_VIEW:{'tablename':AGRI_RES_VIEW,
			'from_indicator_name':stat + AGRI_RES_VIEW,
			'where':'',
            'schema': geo_schema,
            'schema_hectare': geo_schema,
            'geo_column': geom_column,
            'crs': '4258',
			'table_type':vector_type,
			'indicators':[
				{'select': 'value', 'unit': 'MWh','name':'values'},
			]},
    LAND_SURFACE:{'tablename':LAND_SURFACE,
			'from_indicator_name':stat + LAND_SURFACE,
			'where':'',
            'schema': stat_schema,
            'schema_hectare': geo_schema,
            'geo_column': geometry_column,
            'crs': '3035',
			'table_type':raster_type,

			'indicators':[
				{'select': 'sum', 'unit': 'MWh','name':'sum'},
				{'select': 'count', 'unit': 'cells','name':'count'},
			]},
	HEAT_DENSITY_TOT:{'tablename':HEAT_DENSITY_TOT,
			'from_indicator_name':stat + HEAT_DENSITY_TOT,
			'where':'',
            'schema': stat_schema,
            'schema_hectare': geo_schema,
            'crs': '3035',
            'geo_column': geometry_column,
			'table_type':raster_type,

			'indicators':[
				{'select': 'sum', 'unit': 'MWh','name':'consumption'},
				{'select': 'count', 'unit': 'cells','name':'count_cell'},
				{'select': 'min', 'unit': 'MWh','name':'consumption_min'},
				{'select': 'max', 'unit': 'MWh','name':'consumption_max'},
				{'select': 'mean', 'unit': 'Blabla','name':'consumption_mean'},
				{'val1': 'consumption','from_val1':HEAT_DENSITY_TOT, 'operator': '/','val2':'count_cell','from_val2':POPULATION_TOT, 'unit':'MWh/person', 'name':HEAT_DENSITY_TOT+'_per_'+POPULATION_TOT},
			]},
	POPULATION_TOT:{'tablename':POPULATION_TOT,
			'from_indicator_name':stat + POPULATION_TOT,
            'schema': stat_schema,
            'schema_hectare': geo_schema,
            'crs': '3035',
			'table_type':raster_type,

            'geo_column': geometry_column,
			'indicators':[
				{'select': 'sum', 'unit': 'person','name':'population'},
				{'select': 'count', 'unit': 'cells','name':'count_cell'},
				{'val1': 'population','from_val1':POPULATION_TOT, 'operator': '/','val2':'count_cell','from_val2':POPULATION_TOT, 'unit':'person/ha', 'name':'density'},

			]
			},
	WWTP:{'tablename':WWTP,
			'from_indicator_name':stat + WWTP,
            'schema': geo_schema,
            'schema_hectare': geo_schema,
            'geo_column': geom_column,
            'crs': '3035',
			'table_type':vector_type,

			'indicators':[
				{'select': 'capacity', 'unit': 'kW','name':'power'},
				{'select': 'power', 'unit': 'Person equivalent','name':'capacity'},
			]
			},
WWTP_CAPACITY:{'tablename':WWTP_CAPACITY,
            'schema': public_schema,
            'schema_hectare': public_schema,
            'crs': '3035',
			'table_type':vector_type,

			'from_indicator_name':stat + WWTP_CAPACITY,
            'geo_column': geometry_column,

			'indicators':[
				{'select': 'capacity', 'unit': 'Person equivalent','name':'capacity'},
	]},
	WWTP_POWER:{'tablename':WWTP_POWER,
            'schema': public_schema,
            'schema_hectare': public_schema,
            'geo_column': geometry_column,
            'crs': '3035',
			'table_type':vector_type,

			'from_indicator_name':stat + WWTP_POWER,
			'indicators':[
				{'select': 'power', 'unit': 'kW','name':'power'},
			]
			},
	GRASS_FLOOR_AREA_TOT:{'tablename':GRASS_FLOOR_AREA_TOT,
            'schema': stat_schema,
            'schema_hectare': geo_schema,
            'geo_column': geometry_column,
            'crs': '3035',
			'table_type':raster_type,

			'from_indicator_name':stat + GRASS_FLOOR_AREA_TOT,
			'indicators':[
				{'select': 'sum', 'unit': 'm2','name':'density'},
				{'select': 'count', 'unit': 'cells','name':'cells'},
			]
			},
	GRASS_FLOOR_AREA_RES:{'tablename':GRASS_FLOOR_AREA_RES,
            'schema': stat_schema,
            'schema_hectare': geo_schema,
            'geo_column': geometry_column,
            'crs': '3035',
			'table_type':raster_type,

			'from_indicator_name':stat + GRASS_FLOOR_AREA_RES,
			'indicators':[
				{'select': 'sum', 'unit': 'm2','name':'density'},
				{'select': 'count', 'unit': 'cells','name':'cells'},
			]
			},
	GRASS_FLOOR_AREA_NON_RES:{'tablename':GRASS_FLOOR_AREA_NON_RES,
            'schema': stat_schema,
            'schema_hectare': geo_schema,
            'geo_column': geometry_column,
            'crs': '3035',
			'table_type':raster_type,

			'from_indicator_name': stat + GRASS_FLOOR_AREA_NON_RES,
			'indicators':[
				{'select': 'sum', 'unit': 'm2','name':'density'},
				{'select': 'count', 'unit': 'cells','name':'cells'}
			]
			},
	BUILDING_VOLUMES_TOT:{'tablename':BUILDING_VOLUMES_TOT,
            'schema': stat_schema,
            'schema_hectare': geo_schema,
            'geo_column': geometry_column,
            'crs': '3035',
			'table_type':raster_type,

			'from_indicator_name':stat + BUILDING_VOLUMES_TOT,
			'indicators':[
				{'select': 'sum', 'unit': 'm3','name':'value'},
				{'select': 'count', 'unit': 'cells','name':'cells'},
				{'val1': 'value','from_val1':BUILDING_VOLUMES_TOT, 'operator': '/','val2':'cells','from_val2':BUILDING_VOLUMES_TOT, 'unit':'person/ha', 'name':'density'},

				
			]
			},
	BUILDING_VOLUMES_RES:{'tablename':BUILDING_VOLUMES_RES,
            'schema': stat_schema,
            'schema_hectare': geo_schema,
            'geo_column': geometry_column,
            'crs': '3035',
			'table_type':raster_type,

			'from_indicator_name':stat + BUILDING_VOLUMES_RES,
			'indicators':[
				{'select': 'sum', 'unit': 'm3','name':'value'},
				{'select': 'count', 'unit': 'cells','name':'cells'},
				{'val1': 'value', 'from_val1':BUILDING_VOLUMES_RES, 'operator': '/','val2':'cells','from_val2':BUILDING_VOLUMES_RES, 'unit':'m3/ha', 'name':'density'},

			]
			},
	BUILDING_VOLUMES_NON_RES:{'tablename':BUILDING_VOLUMES_NON_RES,
			'from_indicator_name':stat + BUILDING_VOLUMES_NON_RES,
            'schema': stat_schema,
            'schema_hectare': geo_schema,
            'geo_column': geometry_column,
            'crs': '3035',
			'table_type':raster_type,

			'indicators':[
				{'select':  'sum', 'unit': 'm3','name':'value'},
				{'val1': 'value', 'from_val1':BUILDING_VOLUMES_NON_RES, 'operator': '/','val2':'cells','from_val2':BUILDING_VOLUMES_NON_RES, 'unit':'m3/ha', 'name':'density'},
				{'select': 'count', 'unit': 'cells','name':'cells'}
			]
			},
	HEAT_DENSITY_RES:{'tablename':HEAT_DENSITY_RES,
			'from_indicator_name':stat + HEAT_DENSITY_RES,
            'schema': stat_schema,
            'schema_hectare': geo_schema,
            'geo_column': geometry_column,
            'crs': '3035',
			'table_type':raster_type,

			'indicators':[
				{'select': 'sum', 'unit': 'MWh','name':'value'},
				{'val1': 'value', 'from_val1':HEAT_DENSITY_RES, 'operator': '/','val2':'cells','from_val2':HEAT_DENSITY_RES, 'unit':'MWh/ha', 'name':'density'},
				{'select': 'count', 'unit': 'cells','name':'cells'}
			]
			},
	HEAT_DENSITY_NON_RES:{'tablename':HEAT_DENSITY_NON_RES,
			'from_indicator_name':stat + HEAT_DENSITY_NON_RES,
            'schema': stat_schema,
            'schema_hectare': geo_schema,
            'geo_column': geometry_column,
            'crs': '3035',
			'table_type':raster_type,

			'indicators':[
				{'select': 'sum', 'unit': 'MWh','name':'value'},
				{'val1': 'value', 'from_val1':HEAT_DENSITY_NON_RES, 'operator': '/','val2':'cells','from_val2':HEAT_DENSITY_NON_RES, 'unit':'MWh/ha', 'name':'density'},
				{'select': 'count', 'unit': 'cells','name':'cells'}
			]},
	GEOTHERMAL_POTENTIAL_HEAT_COND:{'tablename':GEOTHERMAL_POTENTIAL_HEAT_COND,
		   'from_indicator_name':stat + GEOTHERMAL_POTENTIAL_HEAT_COND,
            'schema': geo_schema,
            'schema_hectare': geo_schema,
            'geo_column': geometry_column,
            'crs': '4326',
			'table_type':vector_type,

            #'custom_select':"SELECT SUM(CAST(heat_cond as DECIMAL(9,2)) * CAST(ST_Area(geometry) as DECIMAL(9,2))) / SUM(ST_Area(geometry)) as sum ",
			'indicators':[

			]
		   },
	INDUSTRIAL_SITES_EMISSIONS:{'tablename':INDUSTRIAL_SITES_EMISSIONS,
			'from_indicator_name':stat + INDUSTRIAL_SITES_EMISSIONS,
            'schema': stat_schema,
            'schema_hectare': public_schema,
            'geo_column': geom_column,
            'crs': '4326',
			'table_type':vector_type,

			'indicators':[
				#{'select': 'sum/1000000', 'unit': 'Mtonnes/year','name':'value'}
			]
			},
	INDUSTRIAL_SITES_EXCESS_HEAT:{'tablename':'industrial_database',
			'from_indicator_name':stat + INDUSTRIAL_SITES_EXCESS_HEAT,
            'schema': stat_schema,
            'schema_hectare': stat_schema,
            'geo_column': geom_column,
            'crs': '4326',
			'table_type':vector_type,
			'indicators':[
				{'select': 'excess_heat_100_200c', 'unit': 'GWh/year','name':'value1'},
				{'select': 'excess_heat_200_500c', 'unit': 'GWh/year','name':'value2'},
				{'select': 'excess_heat_500c', 'unit': 'GWh/year','name':'value3'},
				{'select': 'excess_heat_total', 'unit': 'GWh/year','name':'total'}
			]
			},
	SOLAR_POTENTIAL:{'tablename':SOLAR_POTENTIAL,
			'from_indicator_name':stat + SOLAR_POTENTIAL,
            'schema': stat_schema,
            'schema_hectare': geo_schema,
            'geo_column': geometry_column,
            'crs': '3035',
			'table_type':raster_type,

			'indicators':[
				{'val1': 'value', 'from_val1':SOLAR_POTENTIAL, 'operator': '/','val2':'cells','from_val2':SOLAR_POTENTIAL, 'unit':'GWh/ha', 'name':'density'},
				{'select': 'sum', 'unit': 'GWh','name':'value'},
				{'select': 'count', 'unit': 'cells','name':'cells'},
			]
			},

	ELECRICITY_CO2_EMISSION_FACTOR:{'tablename':ELECRICITY_CO2_EMISSION_FACTOR,
            'schema': public_schema,
            'schema_hectare': public_schema,
            'geo_column': geom_column,
            'crs': '4258',
			'table_type':vector_type,

			'from_indicator_name':stat + ELECRICITY_CO2_EMISSION_FACTOR,
			'indicators':[
				{'select': 'value', 'unit': 'kg/MWh','name':'density'}
			]
			},
	HDD_CUR:{'tablename':HDD_CUR,
            'schema': stat_schema,
            'schema_hectare': geo_schema,
            'geo_column': geometry_column,
            'crs': '3035',
			'table_type':raster_type,

		 'from_indicator_name':stat + HDD_CUR,
			'indicators':[
				{'val1': 'value', 'from_val1':HDD_CUR, 'operator': '/','val2':'cells','from_val2':HDD_CUR, 'unit':'Kd', 'name':'density'},
				{'select': 'count', 'unit': 'cells','name':'cells'},
				{'select': 'sum', 'unit': '','name':'value'}
			]
		 },
	CDD_CUR:{	
		'tablename':CDD_CUR,
        'schema': stat_schema,
        'schema_hectare': geo_schema,
        'geo_column': geometry_column,
        'crs': '3035',
		'table_type':raster_type,

		'from_indicator_name':stat + CDD_CUR,
		'indicators':[
			{'select': 'sum', 'unit': '','name':'value'},
			{'select': 'count', 'unit': 'cells','name':'cells'},
			{'val1': 'value', 'from_val1':CDD_CUR, 'operator': '/','val2':'cells','from_val2':CDD_CUR, 'unit':'Kd', 'name':'density'},
		]}
}
