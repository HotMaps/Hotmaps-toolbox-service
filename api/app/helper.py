import json
import uuid
import shapely.geometry as shapely_geom
import ast
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
    print ('value ', value)
    print ('type ', type(value))
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

def generate_geotif_name(directory):
    filename = generate_file(directory, '.tif')
    return filename

def generate_shapefile_name(directory):
    filename = generate_file(directory, '.shp')
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
    print ('data_output',data_output)
    data = json.dumps(data_output)
    return data

