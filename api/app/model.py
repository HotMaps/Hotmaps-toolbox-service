
from flask import url_for
from app import dbGIS as db
import json
from app.decorators.exceptions import ValidationError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, Integer, String, Float, Boolean
from sqlalchemy import Index
from sqlalchemy.orm import relationship, backref
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
from app import constants
basedir = os.path.abspath(os.path.dirname(__file__))

db_path = os.path.join(basedir, '../data.sqlite')

DB_NAME = CM_DB_NAME




def addRegisterCalulationModule(data):

    cm_name = data['cm_name']
    category = data['category']
    cm_description = data['cm_description']
    cm_url = data['cm_url']
    cm_Id = data['id']
    layers_needed = data['layers_needed']
    updatedAt = datetime.utcnow()
    createdAt = datetime.utcnow()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    #c.execute("INSERT INTO calculation_module(cm_Id, cm_name, cm_description, category, cm_url, layers_needed, createdAt, updateAt) VALUES ({},{},{},{},{},{},{},{})".format(cm_Id, cm_name, cm_description, category, cm_url, layers_needed, createdAt, updatedAt))
    c.execute("INSERT INTO calculation_module (cm_id, cm_name, cm_description, category, cm_url, layers_needed, createdAt, updateAt) VALUES (?,?,?,?,?,?,?,?)", ( cm_Id, cm_name, cm_description, category, cm_url, layers_needed, createdAt, updatedAt ))
    c.close()

def init_sqlite_caculation_module_database(dbname=DB_NAME):
    conn = sqlite3.connect(dbname)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS calculation_module")
    cursor.execute("CREATE TABLE calculation_module (cm_id INTEGER NOT NULL, cm_name VARCHAR(255), "
                   "cm_description VARCHAR(255),cm_url VARCHAR(255),category VARCHAR(255),layers_needed VARCHAR(255),createdAt REAL(255),updatedAt REAL(255),"
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
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cm_name = data['cm_name']
        category = data['category']
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
            print ("layers_needed string",ln)
            cursor.execute("INSERT INTO calculation_module (cm_id, cm_name, cm_description, category, cm_url, layers_needed, createdAt, updatedAt) VALUES (?,?,?,?,?,?,?,?)", ( cm_id, cm_name, cm_description, category, cm_url, ln, createdAt, updatedAt ))
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
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                cursor.execute("INSERT INTO inputs_calculation_module (input_name, input_type, input_parameter_name, input_value, input_unit, input_min, input_max, cm_id, createdAt,updatedAt) VALUES (?,?,?,?,?,?,?,?,?,?)", (input_name, input_type, input_parameter_name, input_value, input_unit, input_min, input_max, cm_id, createdAt,updatedAt))

                conn.commit()
            conn.close()

        except ValidationError:
            pass
        except sqlite3.IntegrityError as e:
            update_calulation_module(cm_id, cm_name, cm_description, category, cm_url, layers_needed, createdAt, updatedAt,inputs_calculation_module,cursor,conn)


def update_calulation_module(cm_id, cm_name, cm_description, category, cm_url, layers_needed, createdAt, updatedAt,inputs_calculation_module,cursor,conn):
    try:

        ln = str(layers_needed)
        cursor.execute("UPDATE calculation_module SET cm_name = ?, cm_description = ?, category= ?,  cm_url= ?,  layers_needed= ?,  createdAt= ?,  updatedAt = ? WHERE cm_id = ? ", ( cm_name, cm_description, category, cm_url,ln , createdAt, updatedAt,cm_id ))
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
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cm_url = cursor.execute('select cm_url from calculation_module where cm_id = ?',
                                (cm_id))
        cm_url = str(cm_url.fetchone()[0])
        conn.close()
        return cm_url

    except ValidationError:
        print ('error')
    except sqlite3.IntegrityError as e:
        print (e)

def getLayerNeeded(cm_id):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cm_url = cursor.execute('select layers_needed from calculation_module where cm_id = ?',
                                (cm_id))
        cm_url = str(cm_url.fetchone()[0])
        conn.close()
        return cm_url

    except ValidationError:
        print ('error')
    except sqlite3.IntegrityError as e:
        print (e)

def getUI(cm_id):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        results = cursor.execute('select * from inputs_calculation_module where cm_id = ?',
                                (cm_id))
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

def delete_cm(cm_id):
    delete_cm_with_id(cm_id)
    delete_cm_ui_with_id(cm_id)

def delete_cm_ui_with_id(cm_id):
    try:
        conn = sqlite3.connect(DB_NAME)
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
        conn = sqlite3.connect(DB_NAME)
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
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        results = cursor.execute('select * from calculation_module ')
        response = []
        for row in results:
            response.append({'cm_id':row[0],
                             'cm_name':row[1],
                             'cm_description':row[2],
                             'cm_url':row[3],
                             'category':row[4],
                             'layers_needed':row[5],
                             'createdAt':row[6],
                             'updatedAt':row[7],

                            })

        conn.close()
        return response

    except ValidationError:
        print ('error')
    except sqlite3.IntegrityError as e:
        print (e)
class RasterManager:

    @staticmethod
    @celery.task(name = 'task-getRasterID')
    def getRasterID(rasterTable, geom,directory):

        sql_query = "SET postgis.gdal_enabled_drivers = 'ENABLE_ALL'; SELECT oid, lowrite(lo_open(oid, 131072), tiff) As num_bytes " \
                    "FROM ( VALUES (lo_create(0)," \
                    "ST_Astiff((" \
                    "Select ST_UNION(ST_Clip("+rasterTable+".rast, "+ geom +"))" \
              " from geo."+rasterTable+" where ST_Intersects("+ geom +","+rasterTable+".rast)) ) " \
                ")) As v(oid,tiff) ;"


        mypool = pool.QueuePool(getConnection_db_gis, max_overflow=10, pool_size=5)
        # get a connection
        conn = mypool.connect()
        # use it
        cursor = conn.cursor()
        cursor.execute(sql_query)
        result = cursor.fetchone()
        iod = result[0]
        lo = conn.lobject(iod)
        filename = str(uuid.uuid4()) + '.tif'
        #save the raster in the working directory and retrieve filename
        lo.export(directory+'/'+filename)
        # "close" the connection.  Returns
        # it to the pool.
        conn.close()
        return filename
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

def get_shapefile_from_selection(nuts,ouput_directory):
    print ('nuts selected before', nuts)
    nuts = helper.adapt_nuts_list(nuts)
    print ('nuts selected after', nuts)
    output_shapefile = helper.generate_shapefile_name(ouput_directory)
    con = "host=hotmapsdev.hevs.ch user=hotmaps dbname=toolboxdb port=32768 password=Dractwatha9"
    com_string = 'ogr2ogr -overwrite -f "ESRI Shapefile" '+output_shapefile+' PG:"'+get_connection_string()+'" -sql "select ST_Transform(geom,3035) from geo.nuts where nuts_id IN ('+ nuts +') AND year = date({})"'.format("'2013-01-01'")
    print (com_string)
    os.system(com_string)
    return output_shapefile


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

def clip_raster_from_database( geom,layer_needed,output_directory):
    inputs_raster_selection = {}
    # retrieve all layer neeeded
    for layer in layer_needed:
        # create a file name as output
        filename_tif = retrieve_raster_clipped_in_database(layer,geom,output_directory)
        inputs_raster_selection[layer] = filename_tif
    return inputs_raster_selection
def transformGeo(geometry):
    return 'st_transform(st_geomfromtext(\''+ geometry +'\'::text,4326),' + str(constants.CRS) + ')'

def retrieve_raster_clipped_in_database(rasterTable, geom,directory):

    geom = transformGeo(geom)

    sql_query = "SET postgis.gdal_enabled_drivers = 'ENABLE_ALL'; SELECT oid, lowrite(lo_open(oid, 131072), tiff) As num_bytes " \
                "FROM ( VALUES (lo_create(0)," \
                "ST_Astiff((" \
                "Select ST_UNION(ST_Clip("+rasterTable+".rast, "+ geom +"))" \
                                                                        " from geo."+rasterTable+" where ST_Intersects("+ geom +","+rasterTable+".rast)) ) " \
                                                                                                                                                ")) As v(oid,tiff) ;"
    mypool = pool.QueuePool(getConnection_db_gis, max_overflow=10, pool_size=5)
    # get a connection
    conn = mypool.connect()
    # use it
    cursor = conn.cursor()
    cursor.execute(sql_query)
    result = cursor.fetchone()
    iod = result[0]
    lo = conn.lobject(iod)
    filename = str(uuid.uuid4()) + '.tif'
    #save the raster in the working directory and retrieve filename
    lo.export(directory+'/'+filename)
    # "close" the connection.  Returns
    # it to the pool.
    conn.close()
    return filename


