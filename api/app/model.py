from app.decorators.exceptions import ValidationError


import json
from app import secrets
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
    #c.execute("INSERT INTO calculation_module(cm_Id, cm_name, cm_description, category, cm_url, layers_needed, createdAt, updateAt) VALUES ({},{},{},{},{},{},{},{})".format(cm_Id, cm_name, cm_description, category, cm_url, layers_needed, createdAt, updatedAt))
    cursor.execute("INSERT INTO calculation_module (cm_id, cm_name, cm_description, category, cm_url, layers_needed, createdAt, updateAt,type_layer_needed,authorized_scale,vectors_needed) VALUES (?,?,?,?,?,?,?,?,?,?)", ( cm_Id, cm_name, cm_description, category, cm_url, layers_needed, createdAt, updatedAt ,type_layer_needed,authorized_scale,vectors_needed))
    cursor.close()

def init_sqlite_caculation_module_database(dbname=DB_NAME):
    conn = sqlite3.connect(dbname)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS calculation_module")
    cursor.execute("CREATE TABLE calculation_module (cm_id INTEGER NOT NULL, cm_name VARCHAR(255), "
                   "cm_description VARCHAR(255),cm_url VARCHAR(255),category VARCHAR(255),layers_needed VARCHAR(255),authorized_scale VARCHAR(255),createdAt REAL(255),updatedAt REAL(255),type_layer_needed REAL(255),vectors_needed REAL(255),"
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
        vectors_needed = "[]"
        try:
            vectors_needed = data['vectors_needed']
        except:
            pass



        print ("layers_needed",layers_needed)
        updatedAt = datetime.utcnow()
        createdAt = datetime.utcnow()
        inputs_calculation_module = data['inputs_calculation_module']
        try:

            ln = str(layers_needed)
            tn = str(type_layer_needed)
            authorized_scale = str(authorized_scale)
            vectors_needed = str(vectors_needed)


            print ("layers_needed string",ln)
            cursor.execute("INSERT INTO calculation_module (cm_id, cm_name, cm_description, category, cm_url, layers_needed, createdAt, updatedAt, type_layer_needed,authorized_scale,vectors_needed) VALUES (?,?,?,?,?,?,?,?,?,?,?)", ( cm_id, cm_name, cm_description, category, cm_url, ln, createdAt, updatedAt,tn,authorized_scale,vectors_needed ))
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
            update_calulation_module(cm_id, cm_name, cm_description, category, cm_url, layers_needed, createdAt, updatedAt,type_layer_needed,authorized_scale,vectors_needed,inputs_calculation_module,cursor,conn)


def update_calulation_module(cm_id, cm_name, cm_description, category, cm_url, layers_needed, createdAt, updatedAt, type_layer_needed,authorized_scale,vectors_needed ,inputs_calculation_module,cursor,conn):
    try:

        ln = str(layers_needed)
        tn = str(type_layer_needed)
        auth_s = str(authorized_scale)
        vn = str(vectors_needed)


        cursor.execute("UPDATE calculation_module SET cm_name = ?, cm_description = ?, category= ?,  cm_url= ?,  layers_needed= ?,  createdAt= ?,  updatedAt = ? ,  type_layer_needed = ?, authorized_scale = ?, vectors_needed = ?   WHERE cm_id = ? ", ( cm_name, cm_description, category, cm_url,ln , createdAt, updatedAt, tn,auth_s, vn,cm_id ))
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
        print (e)




def getCMUrl(cm_id):

    try:
        conn = myCMpool.connect()
        cursor = conn.cursor()

        cm_url = cursor.execute('select cm_url from calculation_module where cm_id = ?',
                                (cm_id))
        conn.commit()
        cm_url = str(cm_url.fetchone()[0])
        conn.close()
        return cm_url

    except ValidationError:
        print ('error')
    except sqlite3.IntegrityError as e:
        print (e)

def get_type_layer_needed(cm_id):
    try:
        conn = myCMpool.connect()
        cursor = conn.cursor()

        result = cursor.execute('select type_layer_needed from calculation_module where cm_id = ?',
                                (cm_id))
        conn.commit()
        cm_url = str(result.fetchone()[0])
        conn.close()
        return cm_url

    except ValidationError:
        print ('error')
    except sqlite3.IntegrityError as e:
        print (e)

def getUI(cm_id):

        conn = myCMpool.connect()
        cursor = conn.cursor()
        results = cursor.execute('select * from inputs_calculation_module where cm_id = ?',
                                (cm_id))
        conn.commit()
        response = helper.retrieve_list_from_sql_result(results)
        conn.close()
        return response

def get_parameters_needed(cm_id):
    try:
        conn = myCMpool.connect()
        cursor = conn.cursor()

        results = cursor.execute('select input_parameter_name from inputs_calculation_module where cm_id = ?',
                                 (cm_id))
        conn.commit()
        response = []
        print ('results', results)
        for row in results:
            response.append(row[0])

        conn.close()
        return response

    except ValidationError:
        print ('error')
    except sqlite3.IntegrityError as e:
        print (e)
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
        print ('error')
    except sqlite3.IntegrityError as e:
        print (e)

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
        print ('error')
    except sqlite3.IntegrityError as e:
        print (e)
def getCMList():
    response = helper.retrieve_list_from_sql_result(query_calculation_module_database('select * from calculation_module '))
    print ('response ' , response)
    return response

@celery.task(name = 'task-getConnection_db_gis')
def getConnection_db_gis():
    c = psycopg2.connect(get_connection_string())
    return c

def get_connection_string():
    user = secrets.dev_user
    host = secrets.dev_host
    password = secrets.dev_password
    port = secrets.dev_port
    database = secrets.dev_database
    con = "host=" + host + " user=" + user + " dbname=" + database + " port=" + port + " password=" + password + ""
    return con

def get_shapefile_from_selection(scalevalue,id_selected_list,ouput_directory):
    id_selected_list = helper.adapt_nuts_list(id_selected_list)
    output_shapefile = helper.generate_shapefile_name(ouput_directory)
    com_string = None
    if scalevalue == 'nuts':
        com_string = 'ogr2ogr -overwrite -f "ESRI Shapefile" '+output_shapefile+' PG:"'+get_connection_string()+'" -sql "select ST_Transform(geom,3035) from geo.nuts where nuts_id IN ('+ id_selected_list +') AND year = date({})"'.format("'2013-01-01'")
    else:
        com_string = 'ogr2ogr -overwrite -f "ESRI Shapefile" '+output_shapefile+' PG:"'+get_connection_string()+'" -sql "select ST_Transform(geom,3035) from geo.lau where comm_id IN ('+ id_selected_list +') AND year = date({})"'.format("'2013-01-01'")
    os.system(com_string)
    return output_shapefile

def get_raster_from_csv(datasets_directory ,wkt_point,layer_needed,type_needed, output_directory):
    inputs_raster_selection = {}
    wkt_point_3035 = helper.projection_4326_to_3035(wkt_point)
    #print ('wkt_point_3035 ',wkt_point_3035)

    filename_csv = helper.write_wkt_csv(helper.generate_csv_name(output_directory),wkt_point_3035)
    print ('filename_csv ',filename_csv)
    # retrieve all layer neeeded
    for layer in layer_needed:
        cpt_type = 0
        type = type_needed[cpt_type]
        directory = layer.replace('_tif', '')
        path_to_dataset = datasets_directory + layer.replace('_tif', '')+ "/data/" + layer + ".tif"
        # create a file name as output
        print ('path_to_dataset ',path_to_dataset)
        filename_tif = helper.generate_geotif_name(output_directory)
        com_string = "gdalwarp -dstnodata 0 -cutline {} -crop_to_cutline -of GTiff {} {} -tr 100 100 -co COMPRESS=DEFLATE".format(filename_csv,path_to_dataset,filename_tif)
        os.system(com_string)
        print ('com_string ',filename_tif)
        inputs_raster_selection[type] = filename_tif
        cpt_type = cpt_type + 1
    return inputs_raster_selection

def clip_raster_from_shapefile(datasets_directory ,shapefile_path,layer_needed,type_needed, output_directory):
    print('clip_raster_from_shapefile/layer_needed',layer_needed)
    print('clip_raster_from_shapefile/type_needed',type_needed)
    inputs_raster_selection = {}
    # retrieve all layer neeeded
    for layer in layer_needed:
        cpt_type = 0
        type = type_needed[cpt_type]
        directory = layer.replace('_tif', '')
        path_to_dataset = datasets_directory + directory + "/data/" + layer + ".tif"
        # create a file name as output
        print ('path_to_dataset ',path_to_dataset)
        filename_tif = helper.generate_geotif_name(output_directory)
        com_string = "gdalwarp -dstnodata 0 -cutline {} -crop_to_cutline -of GTiff {} {} -tr 100 100 -co COMPRESS=DEFLATE".format(shapefile_path,path_to_dataset,filename_tif)

        os.system(com_string)
        print ('com_string ',filename_tif)
        inputs_raster_selection[type] = filename_tif
        cpt_type = cpt_type + 1
    return inputs_raster_selection




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
        result = query_geographic_database(sql_query)
        result = helper.retrieve_list_from_sql_result(result)
        print("result type", result)
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
    # get a connection
    conn = mypool.connect()
    # use it
    cursor = query(sql_query,conn)
    return cursor
def query_geographic_database_first(sql_query):
    cursor = query_geographic_database(sql_query)
    result = cursor.fetchone()
    #result = helper.remove_None_in_turple(result)
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






