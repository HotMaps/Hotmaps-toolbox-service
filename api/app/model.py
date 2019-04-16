from app.decorators.exceptions import ValidationError
from shlex import split
try:
    from shlex import quote
except ImportError:
    from pipes import quote
import subprocess
from app.secrets import user_db,host_db,password_db,port_db,database_db
from datetime import datetime
import psycopg2
import sqlalchemy.pool as pool
import sqlite3
from app import celery
from app.constants import CM_DB_NAME
from app import helper
from app import sql_queries
import os
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

    cm_name = data['cm_name']
    category = data['category']
    type_layer_needed = data['type_layer_needed']
    authorized_scale = "[]"
    try:
        authorized_scale = data['authorized_scale']
    except:
        pass
    description_link = ""
    try:
        description_link = data['description_link']
    except:
        pass
    vectors_needed = "[]"
    try:
        vectors_needed = data['vectors_needed']
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
    cursor.execute("INSERT INTO calculation_module (cm_id, cm_name, cm_description, category, cm_url, layers_needed, createdAt, updateAt,type_layer_needed,authorized_scale,description_link,vectors_needed) VALUES (?,?,?,?,?,?,?,?,?,?,?)", ( cm_Id, cm_name, cm_description, category, cm_url, layers_needed, createdAt, updatedAt ,type_layer_needed,authorized_scale,description_link,vectors_needed))
    cursor.close()

def init_sqlite_caculation_module_database(dbname=DB_NAME):
    conn = sqlite3.connect(dbname)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS calculation_module")
    cursor.execute("CREATE TABLE calculation_module (cm_id INTEGER NOT NULL, cm_name VARCHAR(255), "
                   "cm_description VARCHAR(255),cm_url VARCHAR(255),category VARCHAR(255),layers_needed VARCHAR(255),authorized_scale VARCHAR(255),description_link VARCHAR(255),createdAt REAL(255),updatedAt REAL(255),type_layer_needed REAL(255),vectors_needed REAL(255),"
                   " PRIMARY KEY(cm_id))")
    conn.commit()
    cursor.execute("DROP TABLE IF EXISTS inputs_calculation_module")
    cursor.execute("CREATE TABLE inputs_calculation_module (input_id INTEGER NOT NULL, input_name VARCHAR(255), "
                   "input_type VARCHAR(255),input_parameter_name VARCHAR(255),input_value  VARCHAR(255),input_priority INTEGER, input_unit VARCHAR(255),"
                   "input_min INTEGER,input_max INTEGER,createdAt REAL(255),updatedAt REAL(255),cm_id INTEGER NOT NULL,"
                   " PRIMARY KEY(input_id),FOREIGN KEY(cm_id) REFERENCES calculation_module(cm_id))")
    conn.commit()
    return conn

def register_calulation_module(data):
    if data is not None:
        conn = myCMpool.connect()
        cursor = conn.cursor()
        cm_name = data['cm_name']
        category = data['category']
        type_layer_needed = data['type_layer_needed']

        cm_description = data['cm_description']
        cm_url = data['cm_url']
        cm_id = data['cm_id']
        layers_needed = data['layers_needed']
        authorized_scale = "[]"
        try:
            authorized_scale = data['authorized_scale']
        except:
            pass

        description_link = ""
        try:
            description_link = data['description_link']
        except:
            pass
        vectors_needed = "[]"
        try:
            vectors_needed = data['vectors_needed']
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
            cursor.execute("INSERT INTO calculation_module (cm_id, cm_name, cm_description, category, cm_url, layers_needed, createdAt, updatedAt, type_layer_needed,authorized_scale,description_link,vectors_needed) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", ( cm_id, cm_name, cm_description, category, cm_url, ln, createdAt, updatedAt,tn,authorized_scale,description_link,vectors_needed ))
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
                cursor.execute("INSERT INTO inputs_calculation_module (input_name, input_type, input_parameter_name, input_value,input_priority, input_unit, input_min, input_max, cm_id, createdAt,updatedAt) VALUES (?,?,?,?,?,?,?,?,?,?,?)", (input_name, input_type, input_parameter_name, input_value,input_priority, input_unit, input_min, input_max, cm_id, createdAt,updatedAt))

                conn.commit()
            conn.close()

        except ValidationError:
            pass
        except sqlite3.IntegrityError as e:
            update_calulation_module(cm_id, cm_name, cm_description, category, cm_url, layers_needed, createdAt, updatedAt,type_layer_needed,authorized_scale,description_link,vectors_needed,inputs_calculation_module,cursor,conn)


def update_calulation_module(cm_id, cm_name, cm_description, category, cm_url, layers_needed, createdAt, updatedAt, type_layer_needed,authorized_scale,description_link,vectors_needed ,inputs_calculation_module,cursor,conn):
    try:
        ln = str(layers_needed)
        tn = str(type_layer_needed)
        auth_s = str(authorized_scale)
        description_link = str(description_link)
        vn = str(vectors_needed)
        cursor.execute("UPDATE calculation_module SET cm_name = ?, cm_description = ?, category= ?,  cm_url= ?,  layers_needed= ?,  createdAt= ?,  updatedAt = ? ,  type_layer_needed = ?, authorized_scale = ?,description_link = ?, vectors_needed = ?   WHERE cm_id = ? ", ( cm_name, cm_description, category, cm_url,ln , createdAt, updatedAt, tn,auth_s,description_link, vn,cm_id ))
        conn.commit()
        cursor.execute("DELETE FROM inputs_calculation_module WHERE cm_id = ? ", (str(cm_id)))
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

            cursor.execute("INSERT INTO inputs_calculation_module (input_name, input_type, input_parameter_name, input_value, input_priority, input_unit, input_min, input_max, cm_id, createdAt,updatedAt) VALUES (?,?,?,?,?,?,?,?,?,?,?)", (input_name, input_type, input_parameter_name, input_value,input_priority, input_unit, input_min, input_max, cm_id, createdAt,updatedAt))
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
                                (cm_id))
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
    con = "host=" + host_db + " user=" + user_db + " dbname=" + database_db + " port=" + port_db + " password=" + password_db + ""
    return con

def get_shapefile_from_selection(scalevalue,id_selected_list,ouput_directory):
    id_selected_list = helper.adapt_nuts_list(id_selected_list)
    print('id_selected_list ',id_selected_list)
    output_shapefile = quote(helper.generate_shapefile_name(ouput_directory))
    if scalevalue == 'nuts':
        subprocess.call('ogr2ogr -overwrite -f "ESRI Shapefile" '+output_shapefile+' PG:"'+get_connection_string()+'" -sql "select ST_Transform(geom,3035) from geo.nuts where nuts_id IN ('+ id_selected_list +') AND year = date({})"'.format("'2013-01-01'"), shell=True)
    else:
        subprocess.call('ogr2ogr -overwrite -f "ESRI Shapefile" '+output_shapefile+' PG:"'+get_connection_string()+'" -sql "select ST_Transform(geom,3035) from public.tbl_lau1_2 where comm_id IN ('+ id_selected_list +')"', shell=True)
    print('output_shapefile ',output_shapefile)
    return output_shapefile

def get_raster_from_csv(datasets_directory ,wkt_point,layer_needed,type_needed, output_directory):
    inputs_raster_selection = {}
    wkt_point_3035 = helper.projection_4326_to_3035(wkt_point)
    filename_csv = helper.write_wkt_csv(helper.generate_csv_name(output_directory),wkt_point_3035)
    for layer in layer_needed:
        cpt_type = 0
        type = type_needed[cpt_type]
        directory = layer.replace('_tif', '')
        root_path = datasets_directory + directory + "/data/"
        path_to_dataset = root_path + layer + ".tif"
        if not os.path.abspath(path_to_dataset).startswith(root_path):
            raise Exception("directory traversal denied")
    # create a file name as output
        filename_tif = helper.generate_geotif_name(output_directory)

        args = commands_in_array("gdalwarp -dstnodata 0 -cutline {} -crop_to_cutline -of GTiff {} {} -tr 100 100 -co COMPRESS=DEFLATE".format(filename_csv,path_to_dataset,filename_tif))
        run_command(args)
        #os.system(com_string)
        inputs_raster_selection[type] = filename_tif
        cpt_type = cpt_type + 1
    return inputs_raster_selection

def clip_raster_from_shapefile(datasets_directory ,shapefile_path,layer_needed,type_needed, output_directory):
    """

    :param datasets_directory: input dataset directory
    :param shapefile_path:  input shapefile path
    :param layer_needed: list of layer need for the CM
    :param type_needed:  list of type needed from the CM
    :param output_directory: output directory where we c
    :return: dictionnary
    """
    inputs_raster_selection = {}
    # retrieve all layer neeeded
    for layer in layer_needed:
        cpt_type = 0
        type = type_needed[cpt_type]
        directory = layer.replace('_tif', '')
        root_path = datasets_directory + directory + "/data/"
        path_to_dataset = root_path + layer + ".tif"
        if not os.path.abspath(path_to_dataset).startswith(root_path):
            raise Exception("directory traversal denied")
        # create a file name as output
        filename_tif = helper.generate_geotif_name(output_directory)
        args = commands_in_array("gdalwarp -dstnodata 0 -cutline {} -crop_to_cutline -of GTiff {} {} -tr 100 100 -co COMPRESS=DEFLATE".format(shapefile_path,path_to_dataset,filename_tif))
        run_command(args)
        #os.system(com_string)
        inputs_raster_selection[type] = filename_tif
        cpt_type = cpt_type + 1
    return inputs_raster_selection

def commands_in_array(com_string):
    return split(com_string)

def run_command(arr):

    process = subprocess.Popen(arr, shell=False)
    process.communicate()

def nuts2_within_the_selection_nuts_lau(scalevalue, nuts):
    toCRS = 4258
    sql_query = sql_queries.nuts2_within_the_selection_nuts_lau(scalevalue, nuts, toCRS)
    print ("sql_query ",sql_query)
    result = query_geographic_database(sql_query)
    print ("result ",result)
    result = helper.retrieve_list_from_sql_result(result)
    result = helper.from_dict_to_unique_array(result,'nuts_id')
    return result

def nuts_within_the_selection(geom):
    toCRS = 4258
    sql_query = sql_queries.nuts_within_the_selection(geom,toCRS)
    print ("sql_query ",sql_query)
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
        toCRS = 4258
        sql_query = sql_queries.vector_query(scalevalue,vector_table_requested, area_selected,toCRS)
        print ("sql_query ",sql_query)
        result = query_geographic_database(sql_query)
        result = helper.retrieve_list_from_sql_result(result)
        inputs_vectors_selection[vector_table_requested] = result
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






