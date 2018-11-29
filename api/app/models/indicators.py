from app import constants


# LAYERS
popDe = constants.POPULATION_TOT
heatDe = constants.HEAT_DENSITY_TOT
wwtp = constants.WWTP
wwtpCapacity = constants.WWTP_CAPACITY
wwtpPower = constants.WWTP_POWER
grass = constants.GRASS_FLOOR_AREA_TOT
grassRes = constants.GRASS_FLOOR_AREA_RES
grassNonRes = constants.GRASS_FLOOR_AREA_NON_RES
bVolTot = constants.BUILDING_VOLUMES_TOT
bVolRes = constants.BUILDING_VOLUMES_RES
bVolNonRes = constants.BUILDING_VOLUMES_NON_RES
land_data = 'land_surface_temperature'
heatRes = constants.HEAT_DENSITY_RES
heatNonRes = constants.HEAT_DENSITY_NON_RES
indSites = constants.INDUSTRIAL_SITES
indSitesEm = constants.INDUSTRIAL_SITES_EMISSIONS
indSitesExc = constants.INDUSTRIAL_SITES_EXCESS_HEAT
biomassPot = constants.BIOMASS_POTENTIAL
msw = constants.MUNICIPAL_SOLID_WASTE
windPot = constants.WIND_POTENTIAL
solarPot = constants.SOLAR_POTENTIAL
geothermalPotHeatCond = constants.GEOTHERMAL_POTENTIAL_HEAT_COND2
electricityCo2EmisionsFactor = constants.ELECRICITY_CO2_EMISSION_FACTOR
hdd = constants.HDD_CUR
cdd = constants.CDD_CUR
heatDe = 'heat_tot_curr_density_tif'
stat = 'stat_'
stat_pop = 'stat_pop'
stat_wwtp = 'stat_wwtp'
stat_heat = 'stat_heat'
stat_pop = 'stat_pop'
stat_wwtpCap = 'stat_wwtpCap'
stat_wwtpPower = 'stat_wwtpPower'
stat_grass = 'stat_grass'
stat_grassRes = 'stat_grassRes'
stat_grassNonRes = 'stat_grassNonRes'
stat_bVolTot = 'stat_bVolTot'
stat_heatRes = 'stat_heatRes'
stat_bVolRes = 'stat_bVolRes'
stat_bVolNonRes = 'stat_bVolNonRes'
stat_heatNonRes = 'stat_heatNonRes'
stat_geothermalPotHeatCond = 'stat_geothermalPotHeatCond'
stat_yearly_co2_emission = 'stat_yearly_co2_emission'
stat_indSitesEm = 'stat_indSitesEm'
stat_indSitesExc = 'stat_indSitesExc'
stat_hdd_curr_tif = 'stat_hdd_curr_tif'
stat_cdd_curr_tif = 'stat_cdd_curr_tif'
stat_solarPot = 'stat_solarPot'
stat_land_data = 'stat_land_data'



stat_schema = 'stat'
public_schema = 'public'
geo_schema = 'geo'
geometry_column = 'geometry'
geom_column = 'geom'
# ALL DATA FOR THE STATS

layersData = {
    land_data:{'tablename':land_data,
			'from_indicator_name':stat_land_data,
			'where':'',
            'schema': stat_schema,
            'schema_hectare': geo_schema,
            'geo_column': geometry_column,
            'crs': '4326',

			'indicators':[
				{'select': 'sum', 'unit': 'MWh','name':'sum'},
				{'select': 'count', 'unit': 'cells','name':'count'},
			]},
	heatDe:{'tablename':heatDe,
			'from_indicator_name':stat + heatDe,
			'where':'',
            'schema': stat_schema,
            'schema_hectare': geo_schema,
            'crs': '4326',
            'geo_column': geometry_column,

			'indicators':[
				{'select': 'sum', 'unit': 'MWh','name':'consumption'},
				{'select': 'count', 'unit': 'cells','name':'count_cell'},
				{'select': 'min', 'unit': 'MWh','name':'consumption_min'},
				{'select': 'max', 'unit': 'MWh','name':'consumption_max'},
				{'select': 'mean', 'unit': 'Blabla','name':'consumption_mean'},
				{'val1': heatDe+'consumption', 'operator': '/','val2':heatDe+'count_cell', 'unit':'blablabla', 'name':'blablabla'},
				{'val1': heatDe+'consumption', 'operator': '/','val2':popDe+'count_cell', 'unit':'MWh/person', 'name':heatDe+'_per_'+popDe},
			]},
	popDe:{'tablename':popDe,
			'from_indicator_name':stat_pop,
            'schema': stat_schema,
            'schema_hectare': geo_schema,
            'crs': '4326',
            'geo_column': geometry_column,
			'indicators':[
				{'select': 'sum', 'unit': 'person','name':'population'},
				{'select': 'count', 'unit': 'cells','name':'count_cell'},
				{'val1': popDe+'population', 'operator': '/','val2':popDe+'count_cell', 'unit':'person/ha', 'name':'density'},
			]
			},
	wwtp:{'tablename':wwtp,
			'from_indicator_name':stat_wwtp,
            'schema': stat_schema,
            'schema_hectare': geo_schema,
            'geo_column': geom_column,
            'crs': '4326',

			'indicators':[
				{'select': 'capacityPerson', 'unit': 'kW','name':'power'},
				{'select': 'power', 'unit': 'Person equivalent','name':'capacity'},
			]
			},
	wwtpCapacity:{'tablename':wwtp,
            'schema': public_schema,
            'schema_hectare': geo_schema,
            'crs': '4326',

			'from_indicator_name':stat_wwtpCap,
            'geo_column': geom_column,

            #'custom_select':"SELECT SUM(capacity) as capacity",
			'indicators':[
				{'select': 'capacity', 'unit': 'Person equivalent','name':'capacity'},
	]},
	wwtpPower:{'tablename':wwtp,
            'schema': public_schema,
            'schema_hectare': geo_schema,
            'geo_column': geom_column,
            'crs': '4326',

			'from_indicator_name':stat_wwtpPower,
			'indicators':[
				{'select': 'power', 'unit': 'kW','name':'power'},
			]
			},
	grass:{'tablename':grass,
            'schema': stat_schema,
            'schema_hectare': geo_schema,
            'geo_column': geometry_column,
            'crs': '4326',

			'from_indicator_name':stat_grass,
			'indicators':[
				{'select': 'sum', 'unit': 'm2','name':'density'},
				{'select': 'count', 'unit': 'cells','name':'cells'},
			]
			},
	grassRes:{'tablename':grassRes,
            'schema': stat_schema,
            'schema_hectare': geo_schema,
            'geo_column': geometry_column,
            'crs': '4326',

			'from_indicator_name':stat_grassRes,
			'indicators':[
				{'select': 'sum', 'unit': 'm2','name':'density'},
				{'select': 'count', 'unit': 'cells','name':'cells'},
			]
			},
	grassNonRes:{'tablename':grassNonRes,
            'schema': stat_schema,
            'schema_hectare': geo_schema,
            'geo_column': geometry_column,
            'crs': '4326',

			'from_indicator_name': stat_grassNonRes,
			'indicators':[
				{'select': 'sum', 'unit': 'm2','name':'density'},
				{'select': 'count', 'unit': 'cells','name':'cells'}
			]
			},
	bVolTot:{'tablename':bVolTot,
            'schema': stat_schema,
            'schema_hectare': geo_schema,
            'geo_column': geometry_column,
            'crs': '4326',

			'from_indicator_name':stat_bVolTot,
			'indicators':[
				{'select': 'sum', 'unit': 'm3','name':'value'},
				{'select': 'count', 'unit': 'cells','name':'cells'},
				{'val1': bVolTot+'value', 'operator': '/','val2':bVolTot+'cells', 'unit':'person/ha', 'name':'density'},
			]
			},
	bVolRes:{'tablename':bVolRes,
            'schema': stat_schema,
            'schema_hectare': geo_schema,
            'geo_column': geometry_column,
            'crs': '4326',

			'from_indicator_name':stat_bVolRes,
			'indicators':[
				{'select': 'sum', 'unit': 'm3','name':'value'},
				{'val1': bVolRes+'value', 'operator': '/','val2':bVolRes+'cells', 'unit':'m3/ha', 'name':'density'},
				{'select': 'count', 'unit': 'cells','name':'cells'}
			]
			},
	bVolNonRes:{'tablename':bVolNonRes,
			'from_indicator_name':stat_bVolNonRes,
            'schema': stat_schema,
            'schema_hectare': geo_schema,
            'geo_column': geometry_column,
            'crs': '4326',

			'indicators':[
				{'select':  'sum', 'unit': 'm3','name':'value'},
				{'val1': bVolNonRes+'value', 'operator': '/','val2':bVolNonRes+'cells', 'unit':'m3/ha', 'name':'density'},
				{'select': 'count', 'unit': 'cells','name':'cells'}
			]
			},
	heatRes:{'tablename':heatRes,
			'from_indicator_name':stat_heatRes,
            'schema': stat_schema,
            'schema_hectare': geo_schema,
            'geo_column': geometry_column,
            'crs': '4326',

			'indicators':[
				{'select': 'sum', 'unit': 'MWh','name':'value'},
				{'val1': heatRes+'value', 'operator': '/','val2':heatRes+'cells', 'unit':'MWh/ha', 'name':'density'},
				{'select': 'count', 'unit': 'cells','name':'cells'}
			]
			},
	heatNonRes:{'tablename':heatNonRes,
			'from_indicator_name':stat_heatNonRes,
            'schema': stat_schema,
            'schema_hectare': geo_schema,
            'geo_column': geometry_column,
            'crs': '4326',

			'indicators':[
				{'select': 'sum', 'unit': 'MWh','name':'value'},
				{'val1': heatNonRes+'value', 'operator': '/','val2':heatNonRes+'cells', 'unit':'MWh/ha', 'name':'density'},			
				{'select': 'count', 'unit': 'cells','name':'cells'}
			]},
	geothermalPotHeatCond:{'tablename':geothermalPotHeatCond,
		   'from_indicator_name':stat_geothermalPotHeatCond,
            'schema': public_schema,
            'schema_hectare': geo_schema,
            'geo_column': geometry_column,
            'crs': '4326',

            'custom_select':"SELECT SUM(CAST(heat_cond as DECIMAL(9,2)) * CAST(ST_Area(geometry) as DECIMAL(9,2))) / SUM(ST_Area(geometry)) as sum ",
			'indicators':[
				{'select': 'sum', 'unit': 'W/mK','name':'value'}
			]
		   },
	indSitesEm:{'tablename':indSitesEm,
			'from_indicator_name':stat_indSitesEm,
            'schema': stat_schema,
            'schema_hectare': public_schema,
            'geo_column': geom_column,
            'crs': '4326',

			'indicators':[
				#{'select': 'sum/1000000', 'unit': 'Mtonnes/year','name':'value'}
			]
			},
	indSitesExc:{'tablename':indSitesExc,
			'from_indicator_name':stat_indSitesExc,
            'schema': public_schema,
            'schema_hectare': public_schema,
            'geo_column': geom_column,
            'crs': '4326',

            #'custom_select':'SELECT sum(excess_heat_100_200c) as sum1, sum(excess_heat_200_500c) as sum2, sum(excess_heat_500c) as sum3, sum(excess_heat_total) as total ',
			'indicators':[
				{'select': 'excess_heat_100_200c', 'unit': 'GWh/year','name':'value1'},
				{'select': 'excess_heat_200_500c', 'unit': 'GWh/year','name':'value2'},
				{'select': 'excess_heat_500c', 'unit': 'GWh/year','name':'value3'},
				{'select': 'excess_heat_total', 'unit': 'GWh/year','name':'total'}
			]
			},
	solarPot:{'tablename':solarPot,
			'from_indicator_name':stat_solarPot,
            'schema': stat_schema,
            'schema_hectare': geo_schema,
            'geo_column': geometry_column,
            'crs': '4326',

			'indicators':[
				{'val1': solarPot+'value', 'operator': '/','val2':solarPot+'cells', 'unit':'GWh/ha', 'name':'density'},			
				{'select': 'sum', 'unit': 'GWh','name':'value'},
				{'select': 'count', 'unit': 'cells','name':'cells'},
			]
			},

	electricityCo2EmisionsFactor:{'tablename':electricityCo2EmisionsFactor,
            'schema': public_schema,
            'schema_hectare': geo_schema,
            'geo_column': geometry_column,
            'crs': '4326',

			'from_indicator_name':stat_yearly_co2_emission,
			'indicators':[
				{'select': 'sum', 'unit': 'kg/MWh','name':'density'}
			]
			},
	hdd:{'tablename':hdd,
            'schema': stat_schema,
            'schema_hectare': geo_schema,
            'geo_column': geometry_column,
            'crs': '4326',

		 'from_indicator_name':stat_hdd_curr_tif,
			'indicators':[
				{'val1': hdd+'value', 'operator': '/','val2':hdd+'cells', 'unit':'Kd', 'name':'density'},		

				{'select': 'count', 'unit': 'cells','name':'cells'},
				{'select': 'sum', 'unit': '','name':'value'}
			]
		 },
	cdd:{'tablename':cdd,
            'schema': stat_schema,
            'schema_hectare': geo_schema,
            'geo_column': geometry_column,
            'crs': '4326',

		 'from_indicator_name':stat_cdd_curr_tif,
		'indicators':[
			{'select': 'sum', 'unit': '','name':'value'},
			{'select': 'count', 'unit': 'cells','name':'cells'},
			{'val1': cdd+'value', 'operator': '/','val2':cdd+'cells', 'unit':'Kd', 'name':'density'},		

		]
		 }
}



"""
	Lorsque je fais un indicateur, on definit la position de la table de base.
				{'select': '(' + stat_heat + '.sum/' + stat_heat + '.count)', 'unit': 'MWh/ha','name': heatDe + '_density'}, 

elif layer == electricityCo2EmisionsFactor:
		query += nuts_selection
		query += query_from_part
		query += query_select
		query += query_from + layer_table
		query += " where "+layer_table+".nuts_code  in ("+nuts+")) "



"""