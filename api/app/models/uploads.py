import csv
import json
import os
import shutil
import uuid
from functools import partial
from io import StringIO

import pandas as pd
from pandas import DataFrame
import pyproj
import requests
import shapely.geometry as shapely_geom
import shapely.wkt as shapely_wkt

import app.helper
from app import celery
from app import model
from geojson import Feature, FeatureCollection
from shapely.ops import transform
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, parse_qs
import re

from .. import constants, dbGIS as db
from ..decorators.exceptions import RequestException
from .. import helper


ALLOWED_EXTENSIONS = set(['tif', 'csv'])
GREATER_OR_EQUAL = 'greaterOrEqual'
GREATER = 'greater'
LESSER_OR_EQUAL = 'lesserOrEqual'
LESSER = 'lesser'
EQUAL = 'equal'

class Uploads(db.Model):
    '''
    This class will describe the model of a file uploaded by a user
    '''
    __tablename__ = 'uploads'
    __table_args__ = (
        {'schema': 'user'}
    )

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(255))
    name = db.Column(db.String(255))
    layer = db.Column(db.String(255))
    layer_type = db.Column(db.String(255))
    size = db.Column(db.Numeric)
    url = db.Column(db.String(255))
    is_generated = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.users.id'))


@celery.task(name='generate_tiles_file_upload')
def generate_tiles(upload_folder, grey_tif, layer_type, upload_uuid, user_currently_used_space):
    '''
    This function is used to generate the various tiles of a layer in the db.
    :param upload_folder: the folder of the upload
    :param grey_tif: the url to the input file
    :param layer_type: the type of the layer chosen for the input
    :param upload_uuid: the uuid of the upload
    :param user_currently_used_space: the space currently used by the user

    '''
    # we set up the directory for the tif
    directory_for_tiles = upload_folder + '/tiles'

    tile_path = directory_for_tiles
    access_rights = 0o755
    try:
        os.mkdir(tile_path, access_rights)
    except OSError:
        print ('Creation of the directory %s failed' % tile_path)
    else:
        print ('Successfully created the directory %s' % tile_path)

    rgb_tif = upload_folder + '/rgba.tif'
    if layer_type != 'custom':
        helper.colorize(layer_type, grey_tif, rgb_tif)
    else:
        args_gdal = app.helper.commands_in_array('gdal_translate -of GTiff -expand rgba {} {} -co COMPRESS=DEFLATE '.format(grey_tif, rgb_tif))
        app.helper.run_command(args_gdal)

    try:
        # commands launch to obtain the level of zooms
        args_tiles = app.helper.commands_in_array("python3 app/helper/gdal2tiles.py -p 'mercator' -s 'EPSG:3035' -w 'leaflet' -r 'average' -z '4-11' {} {} ".format(rgb_tif, tile_path))
        app.helper.run_command(args_tiles)

    except :
        generate_state = 10
    else:
        generate_state = 0

    # updating generate state of upload
    upload = Uploads.query.filter_by(url=grey_tif).first()
    upload.is_generated = generate_state
    db.session.commit()

    check_map_size(upload_folder, user_currently_used_space, upload_uuid)
    return generate_state


@celery.task(name='generate_geojson_file_upload')
def generate_geojson(upload_folder, layer_type, upload_uuid, user_currently_used_space):
    '''
    This function is used to generate the geojson of a layer in the db.
    :param upload_folder: the folder of the upload
    :param layer_type: the name of the layer type choosen for the input
    :param upload_uuid: the uuid of the upload
    :param user_currently_used_space: the space currently used by the user
    '''
    upload_csv = upload_folder + '/data.csv'

    try:
        geojson_file_path = upload_folder + '/data.json'
        with open(geojson_file_path, 'w') as geojson_file:
            json.dump(csv_to_geojson(upload_csv, layer_type), geojson_file)
    except:
        generate_state = 10
    else:
        generate_state = 0

    # updating generate state of upload
    upload = Uploads.query.filter_by(uuid=upload_uuid).first()
    upload.is_generated = generate_state
    db.session.commit()
    check_map_size(upload_folder, user_currently_used_space, upload_uuid)
    return generate_state


def check_map_size(upload_folder, user_currently_used_space, upload_uuid):
    '''
    This method is used to check the size of the file
    :param upload_folder: the folder where the upload is stored
    :param user_currently_used_space: the space already used by the user
    :param upload_uuid: the uuid of the upload
    :return:
    '''
    size = 0
    for dirpath, dirnames, filenames in os.walk(upload_folder):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            size += float(os.path.getsize(fp)) / 1000000
    # we need to check if there is enough disk space for the dataset
    total_used_space = user_currently_used_space + size
    upload = Uploads.query.filter_by(uuid=upload_uuid).first()
    if total_used_space > constants.USER_DISC_SPACE_AVAILABLE:
        db.session.delete(upload)
        shutil.rmtree(upload_folder)
    else:
        upload.size = size
    db.session.commit()


def generate_csv_string(result):
    '''
    This method will generate the csv stringIO containing the result of a query without extra data
    :param result: the sql result of a csv export
    :return resultIO: the StringIO result formatted appropriately
    '''
    columns_name = result.keys()
    # if the selection is empty, we return only the columns names
    if result.rowcount == 0:
        df = DataFrame(columns=columns_name)

    else:
        df = DataFrame(result.fetchall(), columns=columns_name)
    
    # remove geom columns
    try:
        df = df.drop(['geometry'], axis=1)
    except:
        pass
    try:
        df = df.drop(['geom'], axis=1)
    except:
        pass
    
    result_io = StringIO()
    df.to_csv(result_io, index=False, quoting=csv.QUOTE_NONNUMERIC)
    result_io.seek(0)
    
    return result_io


def find_property_column(style_sheet, headers):
    '''
    This method will find the column that contains the property
    :param style_sheet: the style sheet
    :param headers: the available headers of our CSV
    :return: the property column name
    '''
    # create the xml tree
    try:
        root = ET.fromstring(style_sheet)
    except:
        raise RequestException('Can\'t parse SLD file')
    ns = {
        'se': 'http://www.opengis.net/se',
        'ogc': 'http://www.opengis.net/ogc'
    }

    # read rules
    rules = root.findall('.//se:Rule', ns)
    # read rules without 'se' prefix if previous did not work
    if len(rules) == 0:
        rules = root.findall('.//{http://www.opengis.net/sld}Rule')
    # raise exception if rules is empty
    if len(rules) == 0:
        print("Can't read rules of SLD file.")

    # read filters
    filters = rules[0].findall('./ogc:Filter/ogc:And', ns)
    if len(filters) == 0:
        filters = rules[0].findall('ogc:Filter', ns)
    if len(filters) == 0:
        print("Can't find any filter in SLD file.")

    for filter_element in filters:

        rule = filter_element.find('./ogc:PropertyIsGreaterThanOrEqualTo', ns)
        if rule is None:
            rule = filter_element.find('./ogc:PropertyIsGreaterThan', ns)

        if rule is None:
            rule = filter_element.find('./ogc:PropertyIsEqualTo', ns)

        if rule is None:
            rule = filter_element.find('./ogc:PropertyIsLessOrEqualTo', ns)

        if rule is None:
            rule = filter_element.find('./ogc:PropertyIsLessThan', ns)

        if rule is None:
            continue

        property_name = rule.find('./ogc:PropertyName', ns).text

        if property_name in headers:
            return property_name

    return None

def extract_query_string_parameters(url):
    '''
    This method will extract all parameters from a url.
    :param url: the url to extract the parameters from
    :return: the dictionary of parameters
    '''
    params = {}
    try:
        qs = urlparse(url).query
        params = parse_qs(qs)
    except:
        pass


    return params


def build_sld_size_formula(etree_size, operator=''):
    '''
    This recursive method will build the formula to compute the size of the SLD graphic.
    :param etree_size: the size XML tree element from SLD
    :return: the string containing the formula
    '''
    prefix = '{http://www.opengis.net/ogc}'
    _operator = ''

    children = etree_size.getchildren()
    formula = ''
    values = []
    for child in children:
        tag = child.tag.replace(prefix, '')
        if tag == 'Literal':
            values.append(child.text)
        elif tag == 'PropertyName':
            values.append(child.text)
        else:
            if tag == 'Add':
                _operator = '+'
            elif tag == 'Div':
                _operator = '/'
            elif tag == 'Mul':
                _operator = '*'
            elif tag == 'Sub':
                _operator = '-'
            values.append(build_sld_size_formula(child, _operator))

    formula = '(' + operator.join(values) + ')'


    return formula


def generate_rule_dictionary(style_sheet):
    '''
    This method will generate a dictionnary of rule giving the stylesheet
    :param style_sheet: the sld stylesheet
    :return: the dictionnary of rules
    '''
    # create the xml tree
    try:
        root = ET.fromstring(style_sheet)
    except:
        raise RequestException('Can\'t parse SLD file')
    ns = {
        'se': 'http://www.opengis.net/se',
        'ogc': 'http://www.opengis.net/ogc'
    }
    ns_xlink = '{http://www.w3.org/1999/xlink}'

    # read rules
    rules = root.findall('.//se:Rule', ns)
    # read rules without 'se' prefix if previous did not work
    if len(rules) == 0:
        rules = root.findall('.//{http://www.opengis.net/sld}Rule')
    # raise exception if rules is empty
    if len(rules) == 0:
        print("Can't read rules of SLD file.")

    # get the list of rules
    rules_dictionary = {}
    i = 0
    
    for rule in rules:
        filters = rule.findall('ogc:Filter/ogc:And', ns)
        if len(filters) == 0:
            filters = rule.findall('ogc:Filter', ns)
        if len(filters) == 0:
            print("Can't find any filter in SLD file.")
        greater_type = None
        lesser_type = None
        equal_type = None

        for filter_type in filters:

            greater = filter_type.find('ogc:PropertyIsGreaterThanOrEqualTo', ns)
            if greater is not None:
                greater_type = GREATER_OR_EQUAL
            else:
                greater = filter_type.find('ogc:PropertyIsGreaterThan', ns)
                if greater is not None:
                    greater_type = GREATER

            lesser = filter_type.find('ogc:PropertyIsLessThanOrEqualTo', ns)
            if lesser is not None:
                lesser_type = LESSER_OR_EQUAL
            else:
                lesser = filter_type.find('ogc:PropertyIsLessThan', ns)
                if lesser is not None:
                    lesser_type = LESSER

            equal = filter_type.find('ogc:PropertyIsEqualTo', ns)
            if equal is not None:
                equal_type = EQUAL

        if greater is not None:
            greater = float(greater.find('ogc:Literal', ns).text)
        if lesser is not None:
            lesser = float(lesser.find('ogc:Literal', ns).text)
        if equal is not None:
            try:
                equal = float(equal.find('ogc:Literal', ns).text)
            except ValueError:
                equal = equal.find('ogc:Literal', ns).text
            except TypeError:
                equal = ''

        # identify symbology
        graphic = rule.find('se:PointSymbolizer/se:Graphic/se:Mark/se:WellKnownName', ns)
        external_graphic = None

        if graphic is not None:
            mark_name = graphic.text
            fill = rule.find('se:PointSymbolizer/se:Graphic/se:Mark/se:Fill/se:SvgParameter', ns).text
            stroke = rule.find('se:PointSymbolizer/se:Graphic/se:Mark/se:Stroke/se:SvgParameter', ns).text
            size = rule.find('se:PointSymbolizer/se:Graphic/se:Size', ns).text
        else:
            # TODO: handle points as charts if found
            # otherwise return default style

            # defaults
            mark_name = 'circle'
            fill = '#0099ff'
            stroke = '#ffffff'
            size = '30'

            # extract graphic
            xpath = 'se:PointSymbolizer/se:Graphic'.replace('se:', '{http://www.opengis.net/sld}')
            graphic = rule.find(xpath)
            if graphic is not None:
                # extract external graphic
                xpath = 'se:ExternalGraphic'.replace('se:', '{http://www.opengis.net/sld}')
                _external_graphic = graphic.find('se:ExternalGraphic'.replace('se:', '{http://www.opengis.net/sld}'))
                if _external_graphic is not None:
                    online_resource = _external_graphic.find('se:OnlineResource'.replace('se:', '{http://www.opengis.net/sld}'), ns)
                    xlink_resource = online_resource.attrib['{0}href'.format(ns_xlink)] if online_resource is not None else ''
                    chart_params = extract_query_string_parameters(xlink_resource)
                    chart_formulas = None
                    # extract chart formula
                    try:
                        # chd = chart data (geoserver SLD)
                        chd = chart_params['chd'][0]
                        chd_arr = chd.split(':')
                        if chd_arr[0] == 't':
                            # get raw formula from chd
                            chart_formula_raw = chd_arr[1].replace(' ', '')
                            # find all formulas used to compute chart (get array of formulas)
                            chart_formulas = re.findall(r'\$\{([^\}]*)\}', chart_formula_raw)
                        else:
                            print('chart data type not supported')
                    except:
                        print('error while parsing chart data')
                        pass

                    try:
                        graphic_format = _external_graphic.find('se:Format'.replace('se:', '{http://www.opengis.net/sld}')).text
                    except:
                        graphic_format = ''

                    # extract formula to compute size
                    _size = rule.find('se:PointSymbolizer/se:Graphic/se:Size'.replace('se:', '{http://www.opengis.net/sld}'))
                    if len(_size.getchildren()) > 0:
                        size_formula = build_sld_size_formula(_size)  # retrieve formula from xml tree

                    # join parameters
                    external_graphic = {
                        'type': graphic_format,
                        'params': chart_params,
                        'formulas': chart_formulas,
                        'size_formula': size_formula
                    }

        rules_dictionary[i] = {
            'greater_type': greater_type,
            'lesser_type': lesser_type,
            'equal_type': equal_type,
            'greater': greater,
            'lesser': lesser,
            'equal': equal,
            'mark_name': mark_name,
            'fill': fill,
            'stroke': stroke,
            'size': size
        }

        if external_graphic is not None:
            rules_dictionary[i]['external_graphic'] = external_graphic

        i += 1

    return rules_dictionary


def find_rule(literal, rules_dictionary):
    '''
    This method will find a specific rule in a rule dictionary
    :param literal: the value we need to check
    :param rules_dictionary: the dictionary of the rules used in the stylesheet
    :return style: the style corresponding to the rule
    '''
    for rule_id, rule_info in rules_dictionary.items():
        if rule_info['greater_type'] == GREATER_OR_EQUAL:
            if not literal >= rule_info['greater']:
                continue
        elif rule_info['greater_type'] == GREATER:
            if not literal > rule_info['greater']:
                continue

        if rule_info['lesser_type'] == LESSER_OR_EQUAL:
            if not literal <= rule_info['lesser']:
                continue
        elif rule_info['lesser_type'] == LESSER:
            if not literal < rule_info['lesser']:
                continue

        if rule_info['equal_type'] == EQUAL:
            if not literal == rule_info['equal']:
                continue

        # standard rule
        style = {
            'name': rule_info['mark_name'],
            'fill': rule_info['fill'],
            'stroke': rule_info['stroke'],
            'size': rule_info['size']
        }

        # handle external graphic (charts)
        if 'external_graphic' in rule_info.keys():
            style['external_graphic'] = rule_info['external_graphic']


        return style


    return {}



def csv_to_geojson(url, layer_type):
    '''
    This method will convert the CSV to a geojson file
    :param url: the URL of the CSV file
    :param layer_type: the type of the layer of the CSV file
    :return: the geojson
    '''
    features = []
    srid = None
    output_srid = '4326'
    sld_file = helper.get_style_from_geoserver(layer_type)
    rule_dictionary = generate_rule_dictionary(sld_file)
    filtered_columns = [
        'year',
		'month',
		'day',
		'weekday',
		'season',
		'hour_of_day',
		'hour_of_year',
		'date'
    ]

    # parse file
    with open(url, 'r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        property_column = find_property_column(sld_file, reader.fieldnames)

        for row in reader:
            geom = None
            properties = {}
            srid = row['srid']
            
            # read each column
            for field in reader.fieldnames:
                # remove filtered columns
                if field in filtered_columns:
                    continue

                value = row[field]

                # get geometry and reproject (transform)
                if field == 'geometry_wkt' or field == 'geometry' or field == 'geom':
                    try:
                        wkt = shapely_wkt.loads(value)
                        geometry = shapely_geom.mapping(wkt)
                        if srid != '4326':
                            project = partial(
                                pyproj.transform,
                                pyproj.Proj(init='epsg:{0}'.format(srid)),
                                pyproj.Proj(init='epsg:4326')
                            )
                            geom = transform(project, shapely_geom.shape(geometry))
                        else:
                            geom = geometry
                    except:
                        geom = None
                else:
                    properties[field] = value
                    
            # find property value in rules to retrieve style
            try:
                # prevent None or empty value
                val = row[property_column]
                if val == 'None' or len(val) == 0:
                    val = 0

                # try to parse number
                style = find_rule(float(val), rule_dictionary)
            except ValueError:
                # if type is not number
                style = find_rule(row[property_column], rule_dictionary)
            except TypeError:
                # if type is not str or number
                style = {}

            # handle external graphic (charts)
            if 'external_graphic' in style.keys():
                external_graphic = style['external_graphic'] 
                eg_params = external_graphic.get('params', {})
                eg_formulas = external_graphic.get('formulas', {})
                eg_size_formula = external_graphic.get('size_formula', None)

                # compute data from SLD formulas & build style
                data = {}
                chart_options = {}
                try:
                    colors = eg_params['chco'][0].split(',')
                except:
                    colors = ['845ec2', 'd65db1', 'ff6f91', 'ff9671', 'ffc75f', 'f9f871', '0081cf', '00dbad', '96ee86', '008f7a']
                i = 0
                for f in eg_formulas:
                    # compute data
                    data_header = 'Data {}'.format(i)
                    used_headers = []
                    for h in reader.fieldnames:
                        if h in f:
                            f = f.replace(h, row[h])
                            used_headers.append(h)
                    try:
                        result = eval(f)
                    except:
                        result = 0.0

                    if len(used_headers) > 0:
                        data_header = used_headers[0]

                    data[data_header] = result

                    # chart style
                    chart_options[data_header] = {
                        'fillColor': '#{}'.format(colors[i]),
                        'color': '#ffffff'
                        #'minValue': 0,
                        #'maxValue': 20,
                        #'maxHeight': 20,
                    }

                    i = i + 1

                # chart type
                # TODO handle other chart types
                # default chart type = pie
                chart_type = 'p'
                try:
                    chart_type = eg_params['cht'][0]  # cht = chart type
                except:
                    pass

                if chart_type == 'p':
                    chart_type = 'pie'

                style['name'] = 'chart'
                style['chart_type'] = chart_type
                style['data'] = data
                style['chartOptions'] = chart_options
                style.pop('external_graphic', None)

                # compute size based on formula
                try:
                    style['size'] = eval(eg_size_formula.replace(property_column, row[property_column]))
                except:
                    # keep default 'size' if computation fails
                    pass

            features.append(Feature(geometry=geom, properties=properties, style=style))

    crs = {
        'type': 'name',
        'properties': {
            'name': 'EPSG:{0}'.format(output_srid)
        }
    }


    return FeatureCollection(features, crs=crs)


def calculate_total_space(uploads):
    '''
    This method will calculate the amount of disc space taken by a list of uploads
    :param uploads:
    :return: the used disk space
    '''
    used_size = float(0)

    # sum of every size
    for upload in uploads:
        used_size += float(upload.size)

    return used_size


def allowed_file(filename):
    '''
    This method will check if the file is allowed
    :param filename:
    :return:
    '''
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
