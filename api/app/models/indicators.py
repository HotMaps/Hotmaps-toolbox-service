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
geothermalPotHeatCond = constants.GEOTHERMAL_POTENTIAL_HEAT_COND
electricityCo2EmisionsFactor = constants.ELECRICITY_CO2_EMISSION_FACTOR
hdd = constants.HDD_CUR
cdd = constants.CDD_CUR
heatDe = 'heat_tot_curr_density_tif'

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
# ALL DATA FOR THE STATS

layersData = {
    land_data:{'tablename':land_data,
			'from':stat_land_data,
			'where':'',
            'schema':'stat',
			'indicators':[
				{'select': stat_land_data + '.sum', 'unit': 'MWh','name':stat_land_data+'_sum'},
				{'select': stat_land_data + '.count', 'unit': 'cells','name':stat_land_data + '_count'},
			]},
	heatDe:{'tablename':heatDe,
			'from':stat_heat,
			'where':'',
            'schema':'stat',
			'indicators':[
				{'select': stat_heat + '.sum', 'unit': 'MWh','name':'heat_consumption'},
				{'select': '(' + stat_heat + '.sum/' + stat_heat + '.count)', 'unit': 'MWh/ha','name':'heat_density'},
				{'select': stat_heat + '.count', 'unit': 'cells','name':'count_cell_heat'},
				{'select': stat_heat + '.min', 'unit': 'MWh','name':'heat_consumption_min'},
				{'select': stat_heat + '.max', 'unit': 'MWh','name':'heat_consumption_max'},
				{'select': stat_heat + '.mean', 'unit': 'Blabla','name':'heat_consumption_mean'},
			]},
	popDe:{'tablename':popDe,
			'from':stat_pop,
            'schema':'stat',
			'indicators':[
				{'select': stat_pop + '.sum', 'unit': 'person','name':'population'},
				{'select': '(' + stat_pop + '.sum/' + stat_pop + '.count)', 'unit': 'person/ha','name':'population_density'},
				{'select': stat_pop + '.count', 'unit': 'cells','name':'count_cell_pop'}
			]},
	wwtp:{'tablename':'wwtp',
			'from':stat_wwtp,
            'schema':'stat',
			'indicators':[
				{'select': stat_wwtp + '.capacityPerson', 'unit': 'kW','name':'power'},
				{'select': stat_wwtp + '.power', 'unit': 'Person equivalent','name':'capacity'},
			]
			},
	wwtpCapacity:{'tablename':'wwtp_capacity',
            'schema':'public',
			'from':stat_wwtpCap,
            'custom_select':"SELECT SUM(capacity) as capacity",
			'indicators':[
				{'select': stat_wwtpCap + '.capacity', 'unit': 'Person equivalent','name':'capacity'},
			]
			},
	wwtpPower:{'tablename':'wwtp_power',
            'schema':'public',
			'from':stat_wwtpPower,
            'custom_select':"SELECT SUM(power) as power",
			'indicators':[
				{'select': stat_wwtpPower + '.power', 'unit': 'kW','name':'power'},
			]
			},
	grass:{'tablename':grass,
            'schema':'stat',
			'from':stat_grass,
			'indicators':[
				{'select': stat_grass + '.sum', 'unit': 'm2','name':grass+'_density'},
				{'select': stat_grass + '.count', 'unit': 'cells','name':grass+'_cells'},
			]
			},
	grassRes:{'tablename':grassRes,
            'schema':'stat',            
			'from':stat_grassRes,
			'indicators':[
				{'select': stat_grassRes + '.sum', 'unit': 'm2','name':grassRes+'_density'},
				{'select': stat_grassRes + '.count', 'unit': 'cells','name':grassRes+'_cells'},
			]
			},
	grassNonRes:{'tablename':grassNonRes,
            'schema':'stat',
			'from': stat_grassNonRes,
			'indicators':[
				{'select': stat_grassNonRes + '.sum', 'unit': 'm2','name':grassNonRes+'_density'},
				{'select': stat_grassNonRes + '.count', 'unit': 'cells','name':grassNonRes+'_cells'}
			]
			},
	bVolTot:{'tablename':bVolTot,
            'schema':'stat',
			'from':stat_bVolTot,
			'indicators':[
				{'select': stat_bVolTot + '.sum', 'unit': 'm3','name':bVolTot+'_value'},
				{'select': '('+stat_bVolTot+'.sum/'+stat_bVolTot+'.count)', 'unit': 'm3/ha','name':bVolTot+'_density'},
				{'select': stat_bVolTot + '.count', 'unit': 'cells','name':bVolTot+'_cells'}
			]
			},
	bVolRes:{'tablename':bVolRes,
            'schema':'stat',
			'from':stat_bVolRes,
			'indicators':[
				{'select': stat_bVolRes + '.sum', 'unit': 'm3','name':bVolRes+'_value'},
				{'select': '('+stat_bVolRes+'.sum/'+stat_bVolRes+'.count)', 'unit': 'm3/ha','name':bVolRes+'_density'},
				{'select': stat_bVolRes + '.count', 'unit': 'cells','name':bVolRes+'_cells'}
			]
			},
	bVolNonRes:{'tablename':bVolNonRes,
			'from':stat_bVolNonRes,
            'schema':'stat',

			'indicators':[
				{'select': stat_bVolNonRes + '.sum', 'unit': 'm3','name':bVolNonRes+'_value'},
				{'select': '('+stat_bVolNonRes+'.sum/'+stat_bVolNonRes+'.count)', 'unit': 'm3/ha','name': bVolNonRes+'_density'},
				{'select': stat_bVolNonRes + '.count', 'unit': 'cells','name':bVolNonRes+'_cells'}
			]
			},
	heatRes:{'tablename':'heat_res_curr_density',
			'from':stat_heatRes,
            'schema':'stat',

			'indicators':[
				{'select': stat_heatRes + '.sum', 'unit': 'MWh','name':heatRes+'_value'},
				{'select': '('+stat_heatRes+'.sum/'+stat_heatRes+'.count)', 'unit': 'MWh/ha','name':heatRes+'_density'},
				{'select': stat_heatRes + '.count', 'unit': 'cells','name':heatRes+'_cells'}
			]
			},
	heatNonRes:{'tablename':'heat_nonres_curr_density',
			'from':stat_heatNonRes,
            'schema':'stat',

			'indicators':[
				{'select': stat_heatNonRes + '.sum', 'unit': 'MWh','name':heatNonRes+'_value'},
				{'select': '('+stat_heatNonRes+'.sum/'+stat_heatNonRes+'.count)', 'unit': 'MWh/ha','name':heatNonRes+'_density'},
				{'select': stat_heatNonRes + '.count', 'unit': 'cells','name':heatNonRes+'_cells'}
			]
			},
	geothermalPotHeatCond:{'tablename':'potential_shallowgeothermal_heat_cond',
		   'from':stat_geothermalPotHeatCond,
            'schema':'public',
            'custom_select':"SELECT SUM(CAST(heat_cond as DECIMAL(9,2)) * CAST(ST_Area(geometry) as DECIMAL(9,2))) / SUM(ST_Area(geometry)) as sum ",
			'indicators':[
				{'select': stat_geothermalPotHeatCond + '.sum', 'unit': 'W/mK','name':geothermalPotHeatCond+'_value'}
			]
		   },
	indSitesEm:{'tablename':'industrial_database_emissions',
			'from':stat_indSitesEm,
            'schema':'stat',

			'indicators':[
				{'select': stat_indSitesEm + '.sum/1000000', 'unit': 'Mtonnes/year','name':indSitesEm+'_value'}
			]
			},
	indSitesExc:{'tablename':'industrial_database_excess_heat',
			'from':stat_indSitesExc,
            'schema':'public',
            'custom_select':'SELECT sum(excess_heat_100_200c) as sum1, sum(excess_heat_200_500c) as sum2, sum(excess_heat_500c) as sum3, sum(excess_heat_total) as total ',
			'indicators':[
				{'select': stat_indSitesExc + '.sum1', 'unit': 'GWh/year','name':indSitesExc+'_value'},
				{'select': stat_indSitesExc + '.sum2', 'unit': 'GWh/year','name':indSitesExc+'_value2'},
				{'select': stat_indSitesExc + '.sum3', 'unit': 'GWh/year','name':indSitesExc+'_value3'},
				{'select': stat_indSitesExc + '.total', 'unit': 'GWh/year','name':indSitesExc+'_total'}
			]
			},
	solarPot:{'tablename':'solar_optimal_total',
			'from':stat_solarPot,
            'schema':'stat',

			'indicators':[
				{'select': '('+stat_solarPot+'.sum/'+stat_solarPot+'.count)', 'unit': 'GWh/year','name':solarPot+'_density'},
				{'select': stat_solarPot + '.count', 'unit': 'cells','name':solarPot+'_cells'}
			]
			},

	electricityCo2EmisionsFactor:{'tablename':electricityCo2EmisionsFactor,
            'schema':'public',
								  'from':stat_yearly_co2_emission,
			'indicators':[
				{'select': stat_yearly_co2_emission+'.sum', 'unit': 'kg/MWh','name':electricityCo2EmisionsFactor+'_density'}
			]
								  },
	hdd:{'tablename':'hdd_curr_tif',
            'schema':'stat',
		 'from':stat_hdd_curr_tif,
			'indicators':[
				{'select': '('+stat_hdd_curr_tif+'.sum/'+stat_hdd_curr_tif+'.count)', 'unit': 'Kd','name':hdd+'_density'},
				{'select': stat_hdd_curr_tif+'.count', 'unit': 'cells','name':hdd+'_cells'}
			]
		 },
	cdd:{'tablename':'cdd_curr_tif',
            'schema':'stat',
		 'from':stat_cdd_curr_tif,
		'indicators':[
			{'select': '('+stat_cdd_curr_tif+'.sum/'+stat_cdd_curr_tif+'.count)', 'unit': 'Kd','name':cdd+'_density'},
			{'select': stat_cdd_curr_tif+'.count', 'unit': 'cells','name':cdd+'_cells'}
		]
		 }
}