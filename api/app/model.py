import uuid

import app.helper
from app.decorators.exceptions import ValidationError, HugeRequestException, RequestException, NotEnoughPointsException


from .helper import area_to_geom, write_wkt_csv, generate_csv_name, projection_4326_to_3035, commands_in_array, \
    run_command

try:
    from shlex import quote
except ImportError:
    from pipes import quote
import subprocess
from app.constants import DATASET_DIRECTORY, USER_DB,HOST_DB,PASSWORD_DB,PORT_DB,DATABASE_DB
from app.constants import DATASET_DIRECTORY, UPLOAD_DIRECTORY, NUTS_YEAR, LAU_YEAR
from datetime import datetime
import psycopg2
import sqlalchemy.pool as pool
import sqlite3
from app import celery, dbGIS as db, constants
from app.constants import CM_DB_NAME
from app import helper
from app import sql_queries
from .models.uploads import Uploads, generate_csv_string
import os
import shapely.geometry as shapely_geom
try:
    import ogr
except ImportError:
    from osgeo import ogr

try:
    import osr
except ImportError:
    from osgeo import osr
basedir = os.path.abspath(os.path.dirname(__file__))

db_path = os.path.join(basedir, '../data.sqlite')

DB_NAME = CM_DB_NAME

def getConnection_db_CM():
    c = sqlite3.connect(DB_NAME)
    return c


myCMpool = pool.QueuePool(getConnection_db_CM, max_overflow=10, pool_size=15)


def addRegisterCalulationModule(data):
    """
    this request will get the signature of a CM and will insert it to the database
    :param data: signature payload of the CM
    :return:
    """

    cm_name = data['cm_name']



    wiki_url = ''
    try:
        wiki_url = data['wiki_url']
    except:
        pass
    category = data['category']
    type_layer_needed = data['type_layer_needed']
    authorized_scale = '[]'
    try:
        authorized_scale = data['authorized_scale']
    except:
        pass
    description_link = ''
    try:
        description_link = data['description_link']
    except:
        pass
    vectors_needed = '[]'
    try:
        vectors_needed = data['vectors_needed']
    except:
        pass

    try:
        type_vectors_needed = data['type_vectors_needed']
    except:
        pass
    cm_description = data['cm_description']
    cm_url = data['cm_url']
    cm_Id = data['id']
    layers_needed = data['layers_needed']
    updatedAt = datetime.utcnow()
    createdAt = datetime.utcnow()
    conn = myCMpool.connect()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO calculation_module (cm_id, cm_name, cm_description, category, cm_url, layers_needed, createdAt, updateAt,type_layer_needed,authorized_scale,description_link,vectors_needed,wiki_url) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)', ( cm_Id, cm_name, cm_description, category, cm_url, layers_needed, createdAt, updatedAt ,type_layer_needed,authorized_scale,description_link,vectors_needed,type_vectors_needed,wiki_url))
    cursor.close()

def init_sqlite_caculation_module_database(dbname=DB_NAME):
    """

    :param dbname: this part will manually create the database for CM
    :return: conn : this is the connection to the database
    """
    conn = sqlite3.connect(dbname)
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS calculation_module')
    cursor.execute('CREATE TABLE calculation_module (cm_id INTEGER NOT NULL, cm_name VARCHAR(255), wiki_url VARCHAR(255),'
                   'cm_description VARCHAR(255),cm_url VARCHAR(255),category VARCHAR(255),layers_needed VARCHAR(255),authorized_scale VARCHAR(255),description_link VARCHAR(255),createdAt REAL(255),updatedAt REAL(255),type_layer_needed REAL(255),vectors_needed REAL(255),type_vectors_needed REAL(255),'
                   ' PRIMARY KEY(cm_id))')
    conn.commit()
    cursor.execute('DROP TABLE IF EXISTS inputs_calculation_module')
    cursor.execute('CREATE TABLE inputs_calculation_module (input_id INTEGER NOT NULL, input_name VARCHAR(255), '
                   'input_type VARCHAR(255),input_parameter_name VARCHAR(255),input_value  VARCHAR(255),input_priority INTEGER, input_unit VARCHAR(255),'
                   'input_min INTEGER,input_max INTEGER,createdAt REAL(255),updatedAt REAL(255),cm_id INTEGER NOT NULL,'
                   ' PRIMARY KEY(input_id),FOREIGN KEY(cm_id) REFERENCES calculation_module(cm_id))')
    conn.commit()
    return conn

def register_calulation_module(data):
    if data is not None:
        conn = myCMpool.connect()
        cursor = conn.cursor()
        cm_name = data['cm_name']


        wiki_url = ''
        try:
            wiki_url = data['wiki_url']
        except:
            pass
        category = data['category']
        type_layer_needed = data['type_layer_needed']

        cm_description = data['cm_description']
        cm_url = data['cm_url']
        cm_id = data['cm_id']
        layers_needed = data['layers_needed']
        authorized_scale = '[]'
        try:
            authorized_scale = data['authorized_scale']
        except:
            pass

        description_link = ''
        try:
            description_link = data['description_link']
        except:
            pass
        vectors_needed = '[]'
        try:
            vectors_needed = data['vectors_needed']
        except:
            pass

        type_vectors_needed = '[]'
        try:
            type_vectors_needed = data['type_vectors_needed']
        except:
            pass

        updatedAt = datetime.utcnow()
        createdAt = datetime.utcnow()
        inputs_calculation_module = data['inputs_calculation_module']
        try:

            ln = str(layers_needed)
            tn = str(type_layer_needed)
            authorized_scale = str(authorized_scale)
            description_link = str(description_link)
            vectors_needed = str(vectors_needed)
            type_vectors_needed = str(type_vectors_needed)
            cursor.execute('INSERT INTO calculation_module (cm_id, cm_name, cm_description, category, cm_url, layers_needed, createdAt, updatedAt, type_layer_needed,authorized_scale,description_link,vectors_needed,type_vectors_needed,wiki_url) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)', ( cm_id, cm_name, cm_description, category, cm_url, ln, createdAt, updatedAt,tn,authorized_scale,description_link,vectors_needed,type_vectors_needed,wiki_url ))
            conn.commit()
            for value in inputs_calculation_module:
                input_name = value['input_name']
                input_type = value['input_type']
                input_parameter_name = value['input_parameter_name']
                input_value = str(value['input_value'])
                input_priority = 0
                try:
                    input_priority = value['input_priority']
                except:
                    pass
                input_unit = value['input_unit']
                input_min = value['input_min']
                input_max = value['input_max']
                cm_id = value['cm_id']
                conn = myCMpool.connect()
                cursor = conn.cursor()
                cursor.execute('INSERT INTO inputs_calculation_module (input_name, input_type, input_parameter_name, input_value,input_priority, input_unit, input_min, input_max, cm_id, createdAt,updatedAt) VALUES (?,?,?,?,?,?,?,?,?,?,?)', (input_name, input_type, input_parameter_name, input_value,input_priority, input_unit, input_min, input_max, cm_id, createdAt,updatedAt))

                conn.commit()
            conn.close()

        except ValidationError:
            pass
        except sqlite3.IntegrityError as e:
            update_calulation_module(cm_id, cm_name, cm_description, category, cm_url, layers_needed, createdAt, updatedAt,type_layer_needed,authorized_scale,description_link,vectors_needed,inputs_calculation_module,cursor,conn,type_vectors_needed,wiki_url)


def update_calulation_module(cm_id, cm_name, cm_description, category, cm_url, layers_needed, createdAt, updatedAt, type_layer_needed,authorized_scale,description_link,vectors_needed ,inputs_calculation_module,cursor,conn,type_vectors_needed,wiki_url):
    try:
        ln = str(layers_needed)
        tn = str(type_layer_needed)
        auth_s = str(authorized_scale)
        description_link = str(description_link)
        vn = str(vectors_needed)

        type_vectors_needed = str(type_vectors_needed)

        cursor.execute('UPDATE calculation_module SET cm_name = ?, cm_description = ?, category= ?,  cm_url= ?,  layers_needed= ?,  createdAt= ?,  updatedAt = ? ,  type_layer_needed = ?, authorized_scale = ?,description_link = ?, vectors_needed = ?, type_vectors_needed=?, wiki_url=? WHERE cm_id = ? ', ( cm_name, cm_description, category, cm_url,ln , createdAt, updatedAt, tn,auth_s,description_link, vn,type_vectors_needed, wiki_url, cm_id ))
        conn.commit()
        cursor.execute('DELETE FROM inputs_calculation_module WHERE cm_id = ? ', (str(cm_id)))
        conn.commit()
        for value in inputs_calculation_module:
            input_name = value['input_name']
            input_type = value['input_type']
            input_parameter_name = value['input_parameter_name']
            input_value = str(value['input_value'])
            input_priority = 0
            try:
                input_priority = value['input_priority']
            except:
                pass
            input_unit = value['input_unit']
            input_min = value['input_min']
            input_max = value['input_max']
            cm_id = value['cm_id']

            cursor.execute('INSERT INTO inputs_calculation_module (input_name, input_type, input_parameter_name, input_value, input_priority, input_unit, input_min, input_max, cm_id, createdAt,updatedAt) VALUES (?,?,?,?,?,?,?,?,?,?,?)', (input_name, input_type, input_parameter_name, input_value,input_priority, input_unit, input_min, input_max, cm_id, createdAt,updatedAt))
            conn.commit()
        conn.close()

    except ValidationError:
        pass
    except sqlite3.IntegrityError as e:
        pass

def getUI(cm_id):
        conn = myCMpool.connect()
        cursor = conn.cursor()


        results = cursor.execute('select * from inputs_calculation_module where cm_id = ?',
                                (cm_id,))
        conn.commit()
        response = helper.retrieve_list_from_sql_result(results)

        """        valid_condition = assert((cmd_id) in (get_all_cm_ids())()
        if valid_condition:
            results = cursor.execute('select * from inputs_calculation_module where cm_id = ?',
                                (cm_id))
        else:
            return False()"""
        conn.close()
        return response

def delete_cm(cm_id):
    delete_cm_with_id(cm_id)
    delete_cm_ui_with_id(cm_id)

def delete_cm_ui_with_id(cm_id):
    try:
        conn = myCMpool.connect()
        cursor = conn.cursor()

        results = cursor.execute('DELETE FROM inputs_calculation_module WHERE cm_id = ?',
                                 (cm_id))
        conn.commit()
        conn.close()
        return results

    except ValidationError:
        pass
    except sqlite3.IntegrityError as e:
        pass

def delete_cm_with_id(cm_id):
    try:
        conn = myCMpool.connect()
        cursor = conn.cursor()

        results = cursor.execute('DELETE FROM calculation_module WHERE cm_id = ?',
                                 (cm_id))
        conn.commit()
        conn.close()
        return results

    except ValidationError:
        pass
    except sqlite3.IntegrityError as e:
        pass

def getCMList():
    response = helper.retrieve_list_from_sql_result(query_calculation_module_database('select * from calculation_module '))
    return response

@celery.task(name = 'task-getConnection_db_gis')
def getConnection_db_gis():
    c = psycopg2.connect(get_connection_string())
    return c

def get_connection_string():
    con = 'host=' + HOST_DB + ' user=' + USER_DB + ' dbname=' + DATABASE_DB + ' port=' + PORT_DB + ' password=' + PASSWORD_DB + ''
    return con

def get_shapefile_from_selection(scalevalue, id_selected_list, ouput_directory, EPSG=str(3035)):
    id_selected_list = helper.adapt_nuts_list(id_selected_list)

    output_shapefile = quote(helper.generate_shapefile_name(ouput_directory))
    if scalevalue == 'nuts':
        subprocess.call('ogr2ogr -overwrite -f "ESRI Shapefile" '+output_shapefile+' PG:"'+get_connection_string()+'" -sql "select ST_Union(ST_Transform(geom,'+EPSG+')) from geo.nuts where nuts_id IN ('+ id_selected_list +') AND year = date({})"'.format("'2013-01-01'"), shell=True)

    else:
        subprocess.call('ogr2ogr -overwrite -f "ESRI Shapefile" '+output_shapefile+' PG:"'+get_connection_string()+'" -sql "select ST_Union(ST_Transform(geom,'+EPSG+')) from public.tbl_lau1_2 where comm_id IN ('+ id_selected_list +')"', shell=True)

    return output_shapefile

def get_raster_from_csv(wkt_point, layer_needed, output_directory):
    inputs_raster_selection = {}
    wkt_point_3035 = helper.projection_4326_to_3035(wkt_point)
    filename_csv = helper.write_wkt_csv(helper.generate_csv_name(output_directory),wkt_point_3035)
    for layer in layer_needed:
        if 'layer_type' in layer:
            type = layer['layer_type']
            id = layer['id']
        else:
            type = layer['name']
            id = 0
        if id == 0:
            dataset_directory = DATASET_DIRECTORY
            directory = layer['workspaceName']
            root_path = dataset_directory + directory + '/data/'
            path_to_dataset = root_path + layer['workspaceName'] + '.tif'
            if not os.path.abspath(path_to_dataset).startswith(root_path):
                raise Exception('directory traversal denied')
        else:
            upload = Uploads.query.get(layer['id'])
            path_to_dataset = upload.url

        # create a file name as output
        filename_tif = helper.generate_geotif_name(output_directory)
        args = commands_in_array('gdalwarp -dstnodata 0 -cutline {} -crop_to_cutline -of GTiff {} {} -tr 100 100 -co COMPRESS=DEFLATE'.format(filename_csv, path_to_dataset, filename_tif))
        run_command(args)
        #os.system(com_string)
        inputs_raster_selection[type] = filename_tif
    return inputs_raster_selection

def clip_raster_from_shapefile(shapefile_path,layer_needed, output_directory):
    """

    :param datasets_directory: input dataset directory
    :param shapefile_path:  input shapefile path
    :param layer_needed: list of layer need for the CM
    :param output_directory: output directory where we c
    :return: dictionnary
    """
    inputs_raster_selection = {}
    # retrieve all layer neeeded
    for layer in layer_needed:
        if 'layer_type' in layer:
            type = layer['layer_type']
            id = layer['id']
        else:
            type = layer['name']
            id = 0
        if id == 0:
            dataset_directory = DATASET_DIRECTORY
            directory = layer['workspaceName']
            root_path = dataset_directory + directory + '/data/'
            path_to_dataset = root_path + layer['workspaceName'] + '.tif'
            if not os.path.abspath(path_to_dataset).startswith(root_path):
                raise Exception('directory traversal denied')
        else:
            upload = Uploads.query.filter_by(id=layer['id']).first()
            path_to_dataset = upload.url
        # create a file name as output
        filename_tif = helper.generate_geotif_name(output_directory)
        # The previous option "-tr 100 100" seems to shift the layer
        args = commands_in_array('gdalwarp -dstnodata 0 -cutline {} -crop_to_cutline -of GTiff {} {} -co COMPRESS=DEFLATE'.format(shapefile_path, path_to_dataset, filename_tif))
        run_command(args)
        inputs_raster_selection[type] = filename_tif


    return inputs_raster_selection


def nuts2_within_the_selection_nuts_lau(scalevalue, nuts):
    toCRS = 4258
    sql_query = sql_queries.nuts2_within_the_selection_nuts_lau(scalevalue, nuts, toCRS)
    result = query_geographic_database(sql_query)
    result = helper.retrieve_list_from_sql_result(result)
    result = helper.from_dict_to_unique_array(result,'nuts_id')
    return result

def nuts_within_the_selection(geom):
    toCRS = 4258
    sql_query = sql_queries.nuts_within_the_selection(geom,toCRS)
    result = query_geographic_database(sql_query)
    result = helper.retrieve_list_from_sql_result(result)
    result = helper.from_dict_to_unique_array(result,'nuts_id')
    return result

def retrieve_vector_data_for_calculation_module(vectors_needed, scalevalue, area_selected):
    """
    this function will return an array of vectors from the database
    :param vectors_needed:
    :param scalevalue:
    :param area_selected: list of nut or geometry
    :return:
    """
    inputs_vectors_selection = {}

    for vector_table_requested in vectors_needed:
        layer_path = ''
        layer_id = vector_table_requested['id']
        layer_type = vector_table_requested['layer_type']
        if layer_id == 0:
            if scalevalue == 'hectare':
                layer_path = ExportCut.cut_hectares(area_selected, layer_type + '_ha', 'public', '2012')
                print(layer_type + '_ha')
            else:
                layer_path = ExportCut.cut_nuts(layer_type + '_' + scalevalue, area_selected, 'public', '2012')
        else:

            upload = Uploads.query.filter_by(id=layer_id).first()
            path_to_dataset = upload.url
            layer_path = ExportCut.cut_personal_layer(scalevalue, path_to_dataset, area_selected)['path']
        inputs_vectors_selection[layer_type] = layer_path
        print(layer_path, layer_id, layer_type)
    return inputs_vectors_selection

def get_vectors_needed(cm_id):
    conn = myCMpool.connect()
    cursor = conn.cursor()
    vectors_needed = cursor.execute('select vectors_needed from calculation_module where cm_id = ?',
                            (cm_id))
    conn.commit()
    vectors_needed = vectors_needed.fetchone()[0]
    vectors_needed = helper.unicode_array_to_string(vectors_needed)
    conn.close()
    return vectors_needed


def query_geographic_database(sql_query):
    mypool = pool.QueuePool(getConnection_db_gis, max_overflow=100, pool_size=5)
    # get a connectioncommands_in_array
    conn = mypool.connect()
    # use it
    cursor = query(sql_query,conn)
    return cursor

def query_geographic_database_first(sql_query):
    cursor = query_geographic_database(sql_query)
    result = cursor.fetchone()
    return result

def check_table_existe(sql_query):
    return query_geographic_database_first(sql_query)

def query_calculation_module_database(sql_query):

    # get a connection
    conn = myCMpool.connect()
    # use it
    cursor = conn.cursor()

    cursor.execute(sql_query)
    conn.commit()
    conn.close()


    return cursor

def query(sql_query,conn):

    # use it
    cursor = conn.cursor()

    cursor.execute(sql_query)
    conn.commit()
    conn.close()


    return cursor

def get_cutline_input(areas, scalelevel, data_type):
    if scalelevel == 'hectare':
        areas = area_to_geom(areas)
        if data_type == 'raster':
            areas = projection_4326_to_3035(areas)

        return write_wkt_csv(generate_csv_name(constants.UPLOAD_DIRECTORY), areas)
    else:
        return get_shapefile_from_selection(scalelevel, areas,
                                                         constants.UPLOAD_DIRECTORY, '4326')
    # if data_type == 'raster':
    #     if scalelevel == 'hectare':
    #         areas = area_to_geom(areas)
    #         cutline_input = write_wkt_csv(generate_csv_name(constants.UPLOAD_DIRECTORY), projection_4326_to_3035(areas))  # TODO: Projection to 3035 if raster
    #     else:
    #         cutline_input = get_shapefile_from_selection(scalelevel, areas,
    #                                                            constants.UPLOAD_DIRECTORY, '4326')
    # elif data_type == 'vector':
    #     if scalelevel == 'hectare':
    #         areas = area_to_geom(areas)
    #         cutline_input = write_wkt_csv(generate_csv_name(constants.UPLOAD_DIRECTORY),
    #                                       areas)
    #     else:
    #         cutline_input = get_shapefile_from_selection(scalelevel, areas,
    #                                                      constants.UPLOAD_DIRECTORY, '4326')
    # return cutline_input

class ExportCut:
    @staticmethod
    def cut_nuts(layers: str, nuts: list, schema: str, year: str):
        """
        The method called to cut a given list of nuts into a csv
        :param layers: the layer selected
        :param nuts: the list of nuts to export
        :param schema: the DB schema
        :param year: the data year
        :return:
        """
        csv_result = get_csv_from_nuts(layers=layers, nuts=nuts, schema=schema, year=year)
        return ExportCut.save_file_csv_random_name(content=csv_result)

    @staticmethod
    def cut_personal_layer(scale_level, upload_url, areas):
        """
        The method called to cut a given list of nuts or a selection into a csv for a presonal layer
        :param scale_level: nuts, lau or hectare
        :param upload_url: the URL of the selected personal layer
        :param areas: the selection on the map
        :return:
        """
        if scale_level == 'hectare':
            areas = area_to_geom(areas)
            cutline_input = write_wkt_csv(generate_csv_name(UPLOAD_DIRECTORY), areas)
        else:
            cutline_input = get_shapefile_from_selection(scale_level[:-1], areas, UPLOAD_DIRECTORY, '4326')
        print(cutline_input)
        cmd_cutline, output_csv = prepare_clip_personal_layer(cutline_input, upload_url)
        args = app.helper.commands_in_array(cmd_cutline)
        app.helper.run_command(args)
        if not os.path.isfile(output_csv):
            return {
                'message': 'not a csv file'
            }
        return {
            'path': output_csv
        }

    @staticmethod
    def cut_hectares(areas: list, layers: str, schema: str, year: str):
        """
        The method called to cut a given selection of hectares into a csv
        :param areas: the area to cut
        :param layers: the layer to select
        :param schema: the DB schema
        :param year: the data_year
        :return:
        """
        csv_result = get_csv_from_hectare(areas=areas, layers=layers, schema=schema, year=year)
        return ExportCut.save_file_csv_random_name(content=csv_result)

    @staticmethod
    def save_file_csv_random_name(content):
        """
        Save a file into a temp folder with a random name
        :param content: the content of the file you want to write
        :return random_name: the name randomly generated
        """
        path = ExportCut.generate_random_file_name()
        content_str = content.getvalue()
        with open(path, 'w', encoding='utf8') as f:
            f.write(content_str)
        return path

    @staticmethod
    def generate_random_file_name(extension: str = '.csv'):
        """
        generate a random file name
        :param extension: the extension of the file, default to .csv
        :return: the path of the generated file name or None if extension doesn't start with a dot
        """
        # the extension must be an extension
        if not extension.startswith('.'):
            return None

        random_name = uuid.uuid4().hex + '.csv'
        path = UPLOAD_DIRECTORY + '/' + random_name
        return path


def get_csv_from_nuts(layers, nuts, schema, year):
    """
    This method will generate a CSV from a nuts or list of nuts
    :param layers: the layer selected
    :param nuts: the selection
    :param schema: the schema of the layer in the DB
    :param year: the year of the data
    :return:the csv containing the results
    """
    # We must determine if it is a nuts or a lau
    dateCol = 'year'
    schema2 = 'geo'
    if str(layers).endswith('lau2'):
        layer_type = 'lau'
        layer_name = layers[: -5]
        id_type = 'comm_id'
        layer_date = LAU_YEAR
        dateCol = 'date'
        schema2 = 'public'

    else:
        scale = str(layers)[-5:]
        layer_type = 'nuts'
        layer_name = str(layers)[: -6]
        id_type = 'nuts_id'
        layer_date = NUTS_YEAR
        if scale not in ['nuts3', 'nuts2', 'nuts1', 'nuts0']:
            # allow co2 emission factors layer
            if 'yearly_co2_emission_factors_view' in str(layers):
                layer_name = 'yearly_co2_emission_factors_view'
            else:
                raise HugeRequestException(message=scale)
    # handle special case of wwtp where geom column has a different name (manual integration)
    geom_col_name = 'geometry' if layer_name.startswith('wwtp') else 'geom'
    # check if year exists otherwise get most recent or fallback to default (1970)
    # timestamp to year if necessary: SELECT TO_CHAR(timestamp :: DATE, 'yyyy')
    date_sql = """SELECT timestamp FROM {0}.{1} GROUP BY timestamp ORDER BY timestamp DESC;""".format(schema,
                                                                                                      layer_name)
    try:
        results = db.engine.execute(date_sql)
    except:
        raise RequestException('Failed retrieving year in database')
    layer_year = year + '-01-01'
    dates = []
    for row in results:
        dates.append(row[0])
    if len(dates) == 0:
        layer_year = '1970-01-01'
    elif layer_year not in dates:
        layer_year = dates[0]
    # build query
    sql = """
    WITH _ as (SELECT geom as _ from {6}.{3} WHERE {4} IN ({5}) AND {7} = '{8}-01-01')
    SELECT ST_ASTEXT({9}) as geometry_wkt, ST_SRID({9}) as srid, {0}.{1}.*
    FROM {0}.{1}, _
    WHERE timestamp = '{2}' 
        AND ST_Within({0}.{1}.{9}, st_transform(
            _._, ST_SRID({9})
        ))
    ;""".format(
        schema,  # 0
        layer_name,  # 1
        layer_year,  # 2
        layer_type,  # 3
        id_type,  # 4
        ', '.join("'{0}'".format(n) for n in nuts),  # 5
        schema2,  # 6
        dateCol,  # 7
        layer_date,  # 8
        geom_col_name  # 9
    )
    # execute query
    try:
        result = db.engine.execute(sql)
    except:
        raise RequestException('Problem with your SQL query')

    # build CSV
    return generate_csv_string(result)


def get_csv_from_hectare(areas, layers, schema, year):
    """
    this method will generate a csv from hectare selection
    :param areas:  the selection
    :param layers: the layer selected
    :param schema: the schema of the layer in the db
    :param year: the year of the data
    :return: the csv containing the results
    """
    if not str(layers).endswith('_ha'):
        raise RequestException('this is not a correct layer for an hectare selection !')
    # format the layer_name to contain only the name
    layer_name = layers[:-3]
    # build request
    polyArray = []
    # convert to polygon format for each polygon and store them in polyArray
    try:
        for polygon in areas:
            po = shapely_geom.Polygon([[p['lng'], p['lat']] for p in polygon['points']])
            polyArray.append(po)
    except:
        raise NotEnoughPointsException
    # convert array of polygon into multipolygon
    multipolygon = shapely_geom.MultiPolygon(polyArray)
    # handle special case of wwtp where geom column has a different name (manual integration)
    geom_col_name = 'geometry' if layer_name.startswith('wwtp') else 'geom'
    # check if year exists otherwise get most recent or fallback to default (1970)
    date_sql = """SELECT timestamp FROM {0}.{1} GROUP BY timestamp ORDER BY timestamp DESC;""".format(schema,
                                                                                                      layer_name)
    try:
        results = db.engine.execute(date_sql)
    except:
        raise RequestException('Failed retrieving year in database')
    layer_year = year + '-01-01'
    dates = []
    for row in results:
        dates.append(row[0])
    if len(dates) == 0:
        layer_year = '1970-01-01'
    elif layer_year not in dates:
        layer_year = dates[0]
    # build query
    sql = """SELECT ST_ASTEXT({3}) as geometry_wkt, ST_SRID({3}) as srid, * 
             FROM {0}.{1} WHERE timestamp = '{2}' 
             AND ST_Within({0}.{1}.{3}, st_transform(st_geomfromtext('{4}', 4258), ST_SRID({3})
             ));""".format(schema, layer_name, layer_year, geom_col_name, str(multipolygon))
    # execute query
    try:
        result = db.engine.execute(sql)
    except:
        raise RequestException('Problem with your SQL query')


    return generate_csv_string(result)


def prepare_clip_personal_layer(cutline_input, upload_url):
    """
    Helper method to clip a personal layer
    :param cutline_input:
    :param upload_url: the url of the upload
    :return: a tuple containing the command to use later ant the output csv path
    """
    #upload_url += "data.csv"
    output_csv = generate_csv_name(constants.UPLOAD_DIRECTORY)
    cmd_cutline = "ogr2ogr -f 'CSV' -clipsrc {} {} {} -oo GEOM_POSSIBLE_NAMES=geometry_wkt -oo KEEP_GEOM_COLUMNS=NO".format(
        cutline_input, output_csv, upload_url)
    return cmd_cutline, output_csv
