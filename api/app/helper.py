from app.constants import LAU_TABLE

import json
import uuid
import shapely.geometry as shapely_geom
import ast
from osgeo import ogr
from osgeo import osr
from . import constants
import csv
def find_key_in_dict(key, dictionary):
    for k, v in dictionary.items():
        if k == key:
            yield v
        elif isinstance(v, dict):
            for result in find_key_in_dict(key, v):
                yield result
        elif isinstance(v, list):
            for d in v:
                for result in find_key_in_dict(key, d):
                    yield result

def retrieveCrossIndicator(denominator_indicator_name, numerator_indicator_name, layers, payload_output):
    if denominator_indicator_name in layers and numerator_indicator_name in layers:
        numerator = getValuesFromName(numerator_indicator_name,payload_output)
        denominator = getValuesFromName(denominator_indicator_name,payload_output)
        generateCrossIndicator(numerator, denominator,numerator_indicator_name, payload_output)

def generateCrossIndicator(numerator, denominator, value_to_append, output):
    denominator_val = float(denominator.get('value', 1))
    denominator_val = denominator_val if denominator_val > 0 else 1
    numerator_val = float(numerator.get('value', 0))
    v = {
        'name': numerator['name'] + '_per_' + denominator['name'],
        'value': numerator_val / denominator_val,
        'unit': numerator.get('unit') + '/' + denominator.get('unit')
    }
    for x in output:
        if x['name'] == value_to_append:
            x['values'].append(v)

def getValuesFromName(name, output):
    values = None
    for i in output:
        if i['name'] == name:
            values = i['values'][0]
            break
    return values
def unicode_array_to_string(unicode_string):
    return ast.literal_eval(unicode_string)
def unicode_string_to_string(unicode_string):
    return str(unicode_string).encode('ascii','ignore')


def test_display(value):
    pass
    #print ('value ', value)
    #print ('type ', type(value))
def getDictFromJson(output):
    outputdumps = json.dumps(output)
    outputloads = json.loads(outputdumps)[0]
    return outputloads

def roundValue(value):
    return round(value, 1)

def getGenerationMixColor(value):
    switcher = {
        "Nuklear": "#909090",
        "Lignite": "#556B2F",
        "Hard coal": "#000000",
        "Natural gas": "#FFD700",
        "Oil": "#8B0000",
        "Other fossil fuels": "#A9A9A9",
        "PV": "#FFFF00",
        "Wind ": "#D8BFD8",
        "Biomass": "#228B22",
        "Hydro": "#1E90FF",
        "No information on source": "#FFFAFA",
    }
    return switcher.get(value, "#D8BFD8")

    raise Exception(msg)

def get_result_formatted(name='not_defined', value=0, unit='unit'):
    return {
        'name': name,
        'value': value,
        'unit': unit
    }



def generate_geotif_name(directory):
    filename = generate_file(directory, '.tif')
    return filename

def generate_shapefile_name(directory):
    filename = generate_file(directory, '.shp')
    return filename
def generate_csv_name(directory):
    filename = generate_file(directory, '.csv')
    return filename
def generate_archive(directory):
    filename = generate_file(directory, '.zip')
    return filename
def generate_file(directory,extension):
    filename = directory+'/' + str(uuid.uuid4()) + extension
    return filename

def generate_directory_name():
    return str(uuid.uuid4())

def area_to_geom(areas):
    polyArray = []
    # convert to polygon format for each polygon and store them in polyArray
    for polygon in areas:
        po = shapely_geom.Polygon([[p['lng'], p['lat']] for p in polygon['points']])
        polyArray.append(po)
    # convert array of polygon into multipolygon
    multipolygon = shapely_geom.MultiPolygon(polyArray)
    #geom = "SRID=4326;{}".format(multipolygon.wkt)

    geom = multipolygon.wkt
    return geom

def adapt_nuts_list(nuts):
    # Store nuts in new custom list
    nutsPayload = []
    for n in nuts:
        if n not in nutsPayload:
            nutsPayload.append(str(n))

    # Adapt format of list for the query
    nutsListQuery = str(nutsPayload)
    nutsListQuery = nutsListQuery[1:] # Remove the left hook
    nutsListQuery = nutsListQuery[:-1] # Remove the right hook

    return nutsListQuery

def generate_payload_for_compute(inputs_raster_selection,inputs_parameter_selection):

    data_output = {}

    data_output.update({

        'inputs_parameter_selection':inputs_parameter_selection
    })
    data_output.update({

        'inputs_raster_selection':inputs_raster_selection
    })
    ##print ('data_output',data_output)
    data = json.dumps(data_output)
    return data

def remove_None_in_turple(tupleX):
    tupleX = [x for x in tupleX if x is not None]
    return tupleX

def write_wkt_csv(output_file,content):

    with open(output_file, mode='w') as csv_file:
        fieldnames = ['id', 'WKT']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerow({'id': '1', 'WKT': content})
    return output_file
def projection_4326_to_3035(wkt):
    # use the database to transform the geometry from 3857 to 4326
    source = osr.SpatialReference()
    source.ImportFromEPSG(4326)

    target = osr.SpatialReference()
    target.ImportFromEPSG(3035)

    transform = osr.CoordinateTransformation(source, target)

    point = ogr.CreateGeometryFromWkt(wkt)
    point.Transform(transform)

    return point.ExportToWkt()



def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))

def retrieve_list_from_sql_result(results):
    response = []
    for value in results:
        ##print ('value', value)
        ze_value = {}
        i = 0
        for key in results.description:
            ze_value[key[0]]= str(value[i])
            if isinstance(unicode_string_to_string(value[i]), str):
                val = unicode_string_to_string(value[i])
                if val.find('[') == 0: # and value.find(']')==
                    #print ('value ', val)
                    ze_value[key[0]]= unicode_array_to_string(value[i])
            elif isinstance(value[i], str):
                val = value[i]
                if val.find('[') == 0: # and value.find(']')==
                    #print ('value ', val)
                    ze_value[key[0]]= unicode_array_to_string(value[i])
            i = i + 1
        response.append(ze_value)
    return response

def force_decode(string, codecs=['utf8', 'cp1252']):
    for i in codecs:
        try:
            return string.decode(i)
        except UnicodeDecodeError:
            pass
def from_dict_to_unique_array(results,key):
    response = []
    for value in results:
        ze_value = value[key]
        response.append(ze_value)
    return response

def sampling_data(listValues):
	# Get number of values
	numberOfValues = len(listValues)

	# Create the points for the curve with the X and Y axis
	listPoints = []
	for n, l in enumerate(listValues):
		listPoints.append({
			'X':n+1,
			'Y':listValues[n]
		})

	# Sampling of the values
	cut1 = int(numberOfValues*constants.POINTS_FIRST_GROUP_PERCENTAGE)
	cut2 = int(cut1+(numberOfValues*constants.POINTS_SECOND_GROUP_PERCENTAGE))
	cut3 = int(cut2+(numberOfValues*constants.POINTS_THIRD_GROUP_PERCENTAGE))

	firstGroup = listPoints[0:cut1:constants.POINTS_FIRST_GROUP_STEP]
	secondGroup = listPoints[cut1:cut2:constants.POINTS_SECOND_GROUP_STEP]
	thirdGroup = listPoints[cut2:cut3:constants.POINTS_THIRD_GROUP_STEP]
	fourthGroup = listPoints[cut3:numberOfValues:constants.POINTS_FOURTH_GROUP_STEP]

	# Get min and max values needed for the sampling list
	maxValue = min(listPoints)
	minValue = max(listPoints)

	# Concatenate the groups to a new list of points (sampling list)
	finalListPoints = firstGroup+secondGroup+thirdGroup+fourthGroup

	# Add max value at the beginning if the list doesn't contain it
	if maxValue not in finalListPoints:
		finalListPoints.insert(0, maxValue)

	# Add min value at the end if the list doesn't contain it
	if minValue not in finalListPoints:
		finalListPoints.append(minValue)

	return finalListPoints
def nuts_array_to_string(nuts):
    nuts_transformed = ''.join("'"+str(nu)+"'," for nu in nuts)[:-1]
    return nuts_transformed

def transform_nuts_list(nuts):
		# Store nuts in new custom list
		nutsPayload = []
		for n in nuts:
			n = n[:4]
			if n not in nutsPayload:
				nutsPayload.append(str(n))

		# Adapt format of list for the query
		nutsListQuery = str(nutsPayload)
		nutsListQuery = nutsListQuery[1:] # Remove the left hook
		nutsListQuery = nutsListQuery[:-1] # Remove the right hook

		return nutsListQuery


def createAllLayers(layers):
	allLayers = []
	for l in layers:
		allLayers.append(l)
		allLayers.append(l+'_ha')
		allLayers.append(l+'_nuts3')
		allLayers.append(l+'_nuts2')
		allLayers.append(l+'_nuts1')
		allLayers.append(l+'_nuts0')
		allLayers.append(l+'_lau2')

	return allLayers

def getTypeScale(layers):
	if layers:
		if layers[0].endswith('lau2'):
			return 'lau'
		else:
			return 'nuts'
	else:
		return ''

def areas_to_geom(areas):
    polygon_array=[]
    for polygon in areas:
        po = shapely_geom.Polygon([[p['lng'], p['lat']] for p in polygon['points']])
        polygon_array.append(po)
	# convert array of polygon into multipolygon
    mp = shapely_geom.MultiPolygon(polygon_array)
    return mp.wkt

def adapt_layers_list(layersPayload, type, allLayers):
	layers = []
	if type == 'lau':
		for layer in layersPayload:
			if layer in allLayers:
				layer = layer[:-5] # Remove the type for each layer
				layers.append(layer)
	elif type == 'ha':
		for layer in layersPayload:
			if layer in allLayers:
				layer = layer[:-3] # Remove the type for each layer
				layers.append(layer)
	else:
		for layer in layersPayload:
			if layer in allLayers:
				layer = layer[:-6] # Remove the type for each layer
				layers.append(layer)

	return layers
def removeScaleLayers(layersList, type):
	layers = []
	if type == 'lau':
		for layer in layersList:
			layer = layer[:-5] # Remove the type for each layer
			layers.append(layer)
	elif type == 'ha':
		for layer in layersList:
			layer = layer[:-3] # Remove the type for each layer
			layers.append(layer)
	else:
		for layer in layersList:
			layer = layer[:-6] # Remove the type for each layer
			layers.append(layer)

	return layers

def layers_filter(layersPayload, list):
	layers = []
	for l in layersPayload:
		if l not in list:
			layers.append(l)

	return layers
def get_nuts_query_selection(nuts, scale_level_table, scale_id):

    if scale_level_table == 'nuts':
        scale_schema = 'geo'
        return """nutsSelection as (
            SELECT nuts.nuts_id as nuts2_id, tbl2."""+scale_id+""" as scale_id
            from geo.nuts nuts, """+scale_schema+"""."""+scale_level_table+""" tbl2
            where tbl2.year = date('2013-01-01') and tbl2."""+scale_id+""" in ("""+nuts+""")
            and st_within(st_transform(tbl2.geom,"""+constants.CRS_NUTS+"""),nuts.geom)
            and nuts.stat_levl_ = 2
            group by nuts.nuts_id, tbl2."""+scale_id+"""),"""

    else:
        scale_schema = 'public'
        return """nutsSelection as (
                SELECT nuts.nuts_id as nuts2_id, tbl2."""+scale_id+""" as scale_id
                from geo.nuts nuts, """+scale_schema+"""."""+LAU_TABLE+""" tbl2
                where tbl2."""+scale_id+""" in ("""+nuts+""")
                and st_within(st_centroid(tbl2.geom),nuts.geom)
                and nuts.stat_levl_ = 2
                group by nuts.nuts_id, tbl2."""+scale_id+"""),"""
