



from app.decorators.exceptions import ValidationError



from app import secrets
from datetime import datetime
import os
import psycopg2
import sqlalchemy.pool as pool
import sqlite3
import uuid
from app import celery
from app.constants import CM_DB_NAME
from app import helper
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
    c = sqlite3.connect(DB_NAME, check_same_thread=False)
    return c


myCMpool = pool.QueuePool(getConnection_db_CM, max_overflow=10, pool_size=15)


def addRegisterCalulationModule(data):

    cm_name = data['cm_name']
    category = data['category']
    type_layer_needed = data['type_layer_needed']
    cm_description = data['cm_description']
    cm_url = data['cm_url']
    cm_Id = data['id']
    layers_needed = data['layers_needed']
    updatedAt = datetime.utcnow()
    createdAt = datetime.utcnow()
    conn = myCMpool.connect()
    cursor = conn.cursor()
    #c.execute("INSERT INTO calculation_module(cm_Id, cm_name, cm_description, category, cm_url, layers_needed, createdAt, updateAt) VALUES ({},{},{},{},{},{},{},{})".format(cm_Id, cm_name, cm_description, category, cm_url, layers_needed, createdAt, updatedAt))
    cursor.execute("INSERT INTO calculation_module (cm_id, cm_name, cm_description, category, cm_url, layers_needed, createdAt, updateAt,type_layer_needed) VALUES (?,?,?,?,?,?,?,?)", ( cm_Id, cm_name, cm_description, category, cm_url, layers_needed, createdAt, updatedAt ,type_layer_needed))
    cursor.close()

def init_sqlite_caculation_module_database(dbname=DB_NAME):
    conn = sqlite3.connect(dbname)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS calculation_module")
    cursor.execute("CREATE TABLE calculation_module (cm_id INTEGER NOT NULL, cm_name VARCHAR(255), "
                   "cm_description VARCHAR(255),cm_url VARCHAR(255),category VARCHAR(255),layers_needed VARCHAR(255),createdAt REAL(255),updatedAt REAL(255),type_layer_needed REAL(255),"
                   " PRIMARY KEY(cm_id))")
    conn.commit()
    cursor.execute("DROP TABLE IF EXISTS inputs_calculation_module")
    cursor.execute("CREATE TABLE inputs_calculation_module (input_id INTEGER NOT NULL, input_name VARCHAR(255), "
                   "input_type VARCHAR(255),input_parameter_name VARCHAR(255),input_value INTEGER, input_unit VARCHAR(255),"
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
        print ("layers_needed",layers_needed)
        updatedAt = datetime.utcnow()
        createdAt = datetime.utcnow()
        inputs_calculation_module = data['inputs_calculation_module']
        try:

            ln = str(layers_needed)
            tn = str(type_layer_needed)
            type_layer_needed
            print ("layers_needed string",ln)
            cursor.execute("INSERT INTO calculation_module (cm_id, cm_name, cm_description, category, cm_url, layers_needed, createdAt, updatedAt, type_layer_needed) VALUES (?,?,?,?,?,?,?,?,?)", ( cm_id, cm_name, cm_description, category, cm_url, ln, createdAt, updatedAt,tn ))
            conn.commit()
            for value in inputs_calculation_module:
                input_name = value['input_name']
                input_type = value['input_type']
                input_parameter_name = value['input_parameter_name']
                input_value = value['input_value']
                input_unit = value['input_unit']
                input_min = value['input_min']
                input_max = value['input_max']
                cm_id = value['cm_id']
                conn = myCMpool.connect()
                cursor = conn.cursor()
                cursor.execute("INSERT INTO inputs_calculation_module (input_name, input_type, input_parameter_name, input_value, input_unit, input_min, input_max, cm_id, createdAt,updatedAt) VALUES (?,?,?,?,?,?,?,?,?,?)", (input_name, input_type, input_parameter_name, input_value, input_unit, input_min, input_max, cm_id, createdAt,updatedAt))

                conn.commit()
            conn.close()

        except ValidationError:
            pass
        except sqlite3.IntegrityError as e:
            update_calulation_module(cm_id, cm_name, cm_description, category, cm_url, layers_needed, createdAt, updatedAt,type_layer_needed,inputs_calculation_module,cursor,conn)


def update_calulation_module(cm_id, cm_name, cm_description, category, cm_url, layers_needed, createdAt, updatedAt, type_layer_needed, inputs_calculation_module,cursor,conn):
    try:

        ln = str(layers_needed)
        cursor.execute("UPDATE calculation_module SET cm_name = ?, cm_description = ?, category= ?,  cm_url= ?,  layers_needed= ?,  createdAt= ?,  updatedAt = ? ,  type_layer_needed = ?  WHERE cm_id = ? ", ( cm_name, cm_description, category, cm_url,ln , createdAt, updatedAt, type_layer_needed,cm_id, ))
        conn.commit()
        cursor.execute("DELETE FROM inputs_calculation_module WHERE cm_id = ? ", (str(cm_id)))
        conn.commit()
        for value in inputs_calculation_module:
            input_name = value['input_name']
            input_type = value['input_type']
            input_parameter_name = value['input_parameter_name']
            input_value = value['input_value']
            input_unit = value['input_unit']
            input_min = value['input_min']
            input_max = value['input_max']
            cm_id = value['cm_id']
            cursor.execute("INSERT INTO inputs_calculation_module (input_name, input_type, input_parameter_name, input_value, input_unit, input_min, input_max, cm_id, createdAt,updatedAt) VALUES (?,?,?,?,?,?,?,?,?,?)", (input_name, input_type, input_parameter_name, input_value, input_unit, input_min, input_max, cm_id, createdAt,updatedAt))
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

def getLayerNeeded(cm_id):
    try:
        conn = myCMpool.connect()
        cursor = conn.cursor()

        cm_url = cursor.execute('select layers_needed from calculation_module where cm_id = ?',
                                (cm_id))
        conn.commit()
        cm_url = str(cm_url.fetchone()[0])
        conn.close()
        return cm_url

    except ValidationError:
        print ('error')
    except sqlite3.IntegrityError as e:
        print (e)

def getUI(cm_id):
    try:
        conn = myCMpool.connect()
        cursor = conn.cursor()

        results = cursor.execute('select * from inputs_calculation_module where cm_id = ?',
                                (cm_id))
        conn.commit()
        response = []
        for row in results:
            response.append({'input_id':row[0],
             'input_name':row[1],
             'input_type':row[2],
             'input_parameter_name':row[3],
             'input_value':row[4],
             'input_unit':row[5],
             'input_min':row[6],
             'input_max':row[7],
             'createdAt':row[8],
             'updatedAt':row[9],
             'cm_id':row[10]})


        conn.close()
        return response

    except ValidationError:
        print ('error')
    except sqlite3.IntegrityError as e:
        print (e)
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
    try:
        results = query_calculation_module_database('select * from calculation_module ')
        response = []


        for row in results:
            print ('row ',row[8])
            print ('type_layer_needed', helper.unicode_string_to_string(row[8]))
            response.append({'cm_id':row[0],
                             'cm_name':row[1],
                             'cm_description':row[2],
                             'cm_url':row[3],
                             'category':row[4],
                             'layers_needed':row[5],
                             'createdAt':row[6],
                             'updatedAt':row[7],
                             'type_layer_needed':helper.unicode_array_to_string(row[8]),


                            })

        return response
        print ('response ' , response)

    except ValidationError:
        print ('error')
    except sqlite3.IntegrityError as e:
        print (e)

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
    print ('id_selected_list selected before', id_selected_list)
    id_selected_list = helper.adapt_nuts_list(id_selected_list)
    print ('id_selected_list selected after', id_selected_list)
    output_shapefile = helper.generate_shapefile_name(ouput_directory)
    com_string = None
    if scalevalue == 'nuts':
        com_string = 'ogr2ogr -overwrite -f "ESRI Shapefile" '+output_shapefile+' PG:"'+get_connection_string()+'" -sql "select ST_Transform(geom,3035) from geo.nuts where nuts_id IN ('+ id_selected_list +') AND year = date({})"'.format("'2013-01-01'")
    else:
        com_string = 'ogr2ogr -overwrite -f "ESRI Shapefile" '+output_shapefile+' PG:"'+get_connection_string()+'" -sql "select ST_Transform(geom,3035) from geo.lau where comm_id IN ('+ id_selected_list +') AND year = date({})"'.format("'2013-01-01'")
    os.system(com_string)
    return output_shapefile

def get_raster_from_csv(datasets_directory ,wkt_point,layer_needed, output_directory):
    inputs_raster_selection = {}
    wkt_point_3035 = helper.projection_4326_to_3035(wkt_point)
    #print ('wkt_point_3035 ',wkt_point_3035)

    filename_csv = helper.write_wkt_csv(helper.generate_csv_name(output_directory),wkt_point_3035)
    print ('filename_csv ',filename_csv)
    # retrieve all layer neeeded
    for layer in layer_needed:
        path_to_dataset = datasets_directory + layer + "/data/" + layer + ".tif"
        # create a file name as output
        print ('path_to_dataset ',path_to_dataset)
        filename_tif = helper.generate_geotif_name(output_directory)
        com_string = "gdalwarp -dstnodata 0 -cutline {} -crop_to_cutline -of GTiff {} {} -tr 100 100 -co COMPRESS=DEFLATE".format(filename_csv,path_to_dataset,filename_tif)
        os.system(com_string)
        print ('com_string ',filename_tif)
        inputs_raster_selection[layer] = filename_tif
    return inputs_raster_selection

def clip_raster_from_shapefile(datasets_directory ,shapefile_path,layer_needed, output_directory):
    inputs_raster_selection = {}
    # retrieve all layer neeeded
    for layer in layer_needed:
        path_to_dataset = datasets_directory + layer + "/data/" + layer + ".tif"
        # create a file name as output
        print ('path_to_dataset ',path_to_dataset)
        filename_tif = helper.generate_geotif_name(output_directory)
        com_string = "gdalwarp -dstnodata 0 -cutline {} -crop_to_cutline -of GTiff {} {} -tr 100 100 -co COMPRESS=DEFLATE".format(shapefile_path,path_to_dataset,filename_tif)

        os.system(com_string)
        print ('com_string ',filename_tif)
        inputs_raster_selection[layer] = filename_tif
    return inputs_raster_selection


def transformGeo(geometry):
    return 'st_transform(st_geomfromtext(\''+ geometry +'\'::text,4326),' + str(constants.CRS) + ')'




def query_geographic_database(sql_query):

    mypool = pool.QueuePool(getConnection_db_gis, max_overflow=10, pool_size=5)
    # get a connection
    conn = mypool.connect()
    # use it
    cursor = query(sql_query,conn)

    return cursor

def query_calculation_module_database(sql_query):


    # get a connection
    conn = myCMpool.connect()

    # use it
    cursor = query(sql_query,conn)

    return cursor

def query(sql_query,conn):

    # use it
    cursor = conn.cursor()

    cursor.execute(sql_query)
    conn.commit()
    conn.close()

    return cursor

def query_geographic_database_first(sql_query):
    cursor = query_geographic_database(sql_query)

    result = cursor.fetchone()

    #result = helper.remove_None_in_turple(result)


    return result





