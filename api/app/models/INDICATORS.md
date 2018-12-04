# Indicators guidelines

This documentation explain how to manage indicators on the hotmaps toolbox.

## Indicators :

An indicator is a value that is displayed on the Hotmaps toolbox in the client side. The indicator is part of a layer. Indicator is a value, for a specific spatial region, with a unit. An indicator is part of a layer dictionary. A layer object contains an array named "indicators". This table will be used to list all the indicators that you want to see for the layer.

    layers = {
	    'heat_tot_curr_density_tif':{
            'tablename':'heat_tot_curr_density_tif',
			'from_indicator_name':'stat_heat_tot_curr_density_tif',
            'schema': 'stat',
            'schema_hectare': 'geo',
            'crs': '3035',
            'geo_column': 'geometry',
			'table_type':'raster',
			'indicators':[
				{'select': 'sum', 'unit': 'MWh','name':'consumption'},
				{'select': 'count', 'unit': 'cells','name':'count_cell'},
				{
                    'val1': 'consumption',
                    'from_val1':'heat_tot_curr_density_tif', 
                    'operator': '/',
                    'val2':'count_cell',
                    'from_val2':'pop_tot_curr_density_tif', 
                    'unit':'MWh/person', 
                    'name':'heat_tot_curr_density_tif_per_pop_tot_curr_density_tif'
                }
			]
        }
    }


- 'tablename'

Name of the DB table. (Exemple: 'heat_tot_curr_density_tif')

- 'from_indicator_name'

Subtablename for the selection of indicators. **Must be unique.** (Exemple: 'stat_heat_tot_curr_density_tif') 

- 'schema'

Table schema location for the nuts level. (Exemple: 'geo', 'stat', 'public')

- 'schema_hectare'

Table schema location for the hectare level. (Exemple: 'geo', 'stat', 'public')

- 'crs'

Projection of the geometry (Exemple: '3035', '4326', '4258')

- 'geo_column'

Name of the geometry column in the database (Exemple: 'geom', 'geometry')

- 'table_type'

Type of the layer in the database (Values: 'vector' or 'raster'). 

***Important :*** If it is a raster, the column available are **count, sum, mean, stddev, min and max**

- 'Indicators'

There are 2 types of indicators (Simple indicators & Cross indicators).


### Simple indicator

A simple indicator is an object with 3 parameters. 

    {
        'select': 'count', 
        'unit': 'cells',
        'name':'count_cell'
    }



- 'select'

This is the database column that is selected in the table. (Exemple: 'count')

![tablecolumnselection](/api/assets/table_image.png)

- 'unit'

This is the unit of the indicator. (Exemple: 'cells', 'MWh')

- 'name'

This is the name of the indicator (Like an ID). This name **must be unique** in the array of indicator.



### Cross indicator

A cross indicator is an object with 7 parameters. The goal of this indicator is to make a calcul between simple indicators and cross indicator. 

	{
        'val1': 'consumption',
        'from_val1':'heat_tot_curr_density_tif', 
        'operator': '/',
        'val2':'count_cell',
        'from_val2':'pop_tot_curr_density_tif', 
        'unit':'MWh/person', 
        'name':'heat_tot_curr_density_tif_per_pop_tot_curr_density_tif'
    }

- 'val1'

Corresponds to the name of a simple indicator. This name **must be defined** in the indicator array. It is the value number 1.

- 'from_val1'

Name of the layer tablename that reference the value number 1. (Exemple: 'heat_tot_curr_density_tif')

- 'operator'

Calcul rule to apply to the 2 values (Values: '/' or '*' or '+' or '-')

- 'val2'

Corresponds to the name of a simple indicator. This name **must be defined** in the indicator array. It is the value number 2.

- 'from_val2'

Name of the layer tablename that reference the value number 2. (Exemple: 'pop_tot_curr_density_tif')

- 'unit'

This is the unit of the indicator. (Exemple: 'cells', 'MWh')

- 'name'

This is the name of the indicator (Like an ID). This name **must be unique** in the array of indicator.


##### Note: For this exemple, the calculation bellow is done.

    from1.val1 / from2.val2 = heat_tot_curr_density_tif.consumption / pop_tot_curr_density_tif.count_cell

### Indicator result

The result of the indicators are as follows:

    {
      "values": [
        {
          "unit": "MWh",
          "name": "heat_tot_curr_density_tif_consumption",
          "value": "4112030.46"
        },
        {
          "unit": "cells",
          "name": "heat_tot_curr_density_tif_count_cell",
          "value": "46764"
        },
        {
          "unit": "MWh/person",
          "name": "heat_tot_curr_density_tif_per_pop_tot_curr_density_tif",
          "value": "38.0092476775893146"
        }
      ],
      "name": "heat_tot_curr_density_tif"
    }

