import csv
import json
import os
import shutil
import uuid
from functools import partial
from io import StringIO

import pandas as pd
import pyproj
import requests
import shapely.geometry as shapely_geom
import shapely.wkt as shapely_wkt
from app import celery
from app import model
from geojson import Feature, FeatureCollection
from shapely.ops import transform
import xml.etree.ElementTree as ET

from .. import constants, dbGIS as db
from ..decorators.exceptions import RequestException
from .. import helper

ALLOWED_EXTENSIONS = set(['tif', 'csv'])
GREATER_OR_EQUAL = 'greaterOrEqual'
GREATER = 'greater'
LESSER_OR_EQUAL = 'lesserOrEqual'
LESSER = 'lesser'

class Uploads(db.Model):
    '''
    This class will describe the model of a file uploaded by a user
    '''
    __tablename__ = 'uploads'
    __table_args__ = (
        {"schema": 'user'}
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
        print ("Creation of the directory %s failed" % tile_path)
    else:
        print ("Successfully created the directory %s" % tile_path)

    rgb_tif = upload_folder + '/rgba.tif'

    helper.colorize(layer_type, grey_tif, rgb_tif)

    try:
        # commands launch to obtain the level of zooms
        args_tiles = model.commands_in_array("python3 app/helper/gdal2tiles.py -p 'mercator' -s 'EPSG:3035' -w 'leaflet' -r 'average' -z '4-11' {} {} ".format(rgb_tif, tile_path))
        model.run_command(args_tiles)

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
def generate_geojson(upload_folder, layer, upload_uuid, user_currently_used_space):
    '''
    This function is used to generate the geojson of a layer in the db.
    :param upload_folder: the folder of the upload
    :param layer: the name of the layer choosen for the input
    :param upload_uuid: the uuid of the upload
    :param user_currently_used_space: the space currently used by the user
    '''
    upload_csv = upload_folder + '/data.csv'

    try:
        geojson_file_path = upload_folder + '/data.json'
        with open(geojson_file_path, 'w') as geojson_file:
            json.dump(csv_to_geojson(upload_csv, layer), geojson_file)
    except :
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
    csv_file = ",".join(result._metadata.keys) + '\r\n'
    rowcount = 0
    for row in result:
        rowcount += 1
        csv_file += ",".join(map(str, row)) + '\r\n'

    # if the result is empty, we raise an error
    if rowcount is 0:
        raise RequestException('There is no result for this selection')

    # write string buffer
    str_io = StringIO()
    str_io.write(csv_file)
    str_io.seek(0)

    pandas_csv = pd.read_csv(str_io)
    pandas_csv = pandas_csv.drop(['geometry'], axis=1)

    result_io = StringIO()
    pandas_csv.to_csv(result_io, index=False)
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
    except Exception as e:
        raise RequestException(str(style_sheet))
    ns = {
        'se': 'http://www.opengis.net/se',
        'ogc': 'http://www.opengis.net/ogc'
    }
    rules = root.findall(".//se:Rule", ns)
    filters = rules[0].findall('./ogc:Filter/ogc:And', ns)
    for filter_element in filters:

        greater = filter_element.find('./ogc:PropertyIsGreaterThanOrEqualTo', ns)
        if greater is None:
            greater = filter_element.find('./ogc:PropertyIsGreaterThan', ns)

        if greater is None:
            continue

        property_name = greater.find('./ogc:PropertyName', ns).text

        if property_name in headers:
            return property_name

        else:
            return None


def generate_rule_dictionary(style_sheet):
    '''
    This method will generate a dictionnary of rule giving the stylesheet
    :param style_sheet: the sld stylesheet
    :return: the dictionnary of rules
    '''
    # create the xml tree
    try:
        root = ET.fromstring(style_sheet)
    except Exception as e:
        raise RequestException(str(style_sheet))
    ns = {
        'se': 'http://www.opengis.net/se',
        'ogc': 'http://www.opengis.net/ogc'
    }

    # get the list of rules
    rules = root.findall(".//se:Rule", ns)
    rules_dictionary = {}
    i = 0
    for rule in rules:
        filters = rule.findall('ogc:Filter/ogc:And', ns)
        greater_type = None
        lesser_type = None

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
        greater = float(greater.find('ogc:Literal', ns).text)
        lesser = float(lesser.find('ogc:Literal', ns).text)
        mark_name = rule.find('se:PointSymbolizer/se:Graphic/se:Mark/se:WellKnownName', ns).text,
        fill = rule.find('se:PointSymbolizer/se:Graphic/se:Mark/se:Fill/se:SvgParameter', ns).text,
        stroke = rule.find('se:PointSymbolizer/se:Graphic/se:Mark/se:Stroke/se:SvgParameter', ns).text,
        size = rule.find('se:PointSymbolizer/se:Graphic/se:Size', ns).text

        rules_dictionary[i] = {
            'greater_type': greater_type,
            'lesser_type': lesser_type,
            'greater': greater,
            'lesser': lesser,
            'mark_name': mark_name,
            'fill': fill,
            'stroke': stroke,
            'size': size
        }

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
        style = {
            "name": rule_info['mark_name'],
            "fill": rule_info['fill'],
            "stroke": rule_info['stroke'],
            "size": rule_info['size']
        }
        return style
    return "No corresponding style"


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
    # parse file
    with open(url, 'r') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        for row in reader:
            geom = None
            properties = {}
            srid = row['srid']
            property_column = find_property_column(sld_file, reader.fieldnames)
            # read each column
            for field in reader.fieldnames:
                value = row[field]

                # get geometry and reproject (transform)
                if field == 'geometry_wkt' or field == 'geometry' or field == 'geom':
                    try:
                        wkt = shapely_wkt.loads(value)
                        geometry = shapely_geom.mapping(wkt)
                        project = partial(
                            pyproj.transform,
                            pyproj.Proj(init='epsg:{0}'.format(srid)),
                            pyproj.Proj(init='epsg:4326')
                        )
                        geom = transform(project, shapely_geom.shape(geometry))
                    except:
                        print('Exception raised: could not retrieve/transform geometry from file.')
                        geom = None
                else:
                    properties[field] = value
            style = find_rule(float(row[property_column]), rule_dictionary)

            features.append(Feature(geometry=geom, properties=properties, style=style))

    crs = {
        "type": "name",
        "properties": {
            "name": "EPSG:{0}".format(output_srid)
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
