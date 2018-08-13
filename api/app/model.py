
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
from constants import CM_DB_NAME
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
    print 'register_calulation_module'
    if data is not None:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cm_name = data['cm_name']
        category = data['category']
        cm_description = data['cm_description']
        cm_url = data['cm_url']
        cm_id = data['cm_id']
        layers_needed = data['layers_needed']
        updatedAt = datetime.utcnow()
        createdAt = datetime.utcnow()
        inputs_calculation_module = data['inputs_calculation_module']
        try:

            ln = str(layers_needed)
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
            print 'error'
        except sqlite3.IntegrityError as e:
            print e
            update_calulation_module(cm_id, cm_name, cm_description, category, cm_url, layers_needed, createdAt, updatedAt,inputs_calculation_module,cursor,conn)


def update_calulation_module(cm_id, cm_name, cm_description, category, cm_url, layers_needed, createdAt, updatedAt,inputs_calculation_module,cursor,conn):
    print 'update_calulation_module'
    try:

        ln = str(layers_needed)
        cursor.execute("UPDATE calculation_module SET cm_name = ?, cm_description = ?, category= ?,  cm_url= ?,  layers_needed= ?,  createdAt= ?,  updatedAt = ? WHERE cm_id = ? ", ( cm_name, cm_description, category, cm_url,ln , createdAt, updatedAt,cm_id ))
        print 'results= ', cursor.fetchone()
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
        print 'error'
    except sqlite3.IntegrityError as e:
        print e



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
        print 'error'
    except sqlite3.IntegrityError as e:
        print e

def getUI(cm_id):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        results = cursor.execute('select * from inputs_calculation_module where cm_id = ?',
                                (cm_id))
        response = []
        for row in results:
            print row
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
        print 'error'
    except sqlite3.IntegrityError as e:
        print e

def delete_cm(cm_id):
    print cm_id
    delete_cm_with_id(cm_id)
    delete_cm_ui_with_id(cm_id)

def delete_cm_ui_with_id(cm_id):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        results = cursor.execute('DELETE FROM inputs_calculation_module WHERE cm_id = ?',
                                 (cm_id))
        print results
        conn.commit()
        conn.close()
        return results

    except ValidationError:
        print 'error'
    except sqlite3.IntegrityError as e:
        print e

def delete_cm_with_id(cm_id):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        results = cursor.execute('DELETE FROM calculation_module WHERE cm_id = ?',
                                 (cm_id))
        print results
        conn.commit()
        conn.close()
        return results

    except ValidationError:
        print 'error'
    except sqlite3.IntegrityError as e:
        print e
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
        print 'error'
    except sqlite3.IntegrityError as e:
        print e
class RasterManager:

    @staticmethod
    @celery.task(name = 'task-getRasterID')
    def getRasterID(rasterTable, geom,directory):
        print geom
        sql_query = "SET postgis.gdal_enabled_drivers = 'ENABLE_ALL'; SELECT oid, lowrite(lo_open(oid, 131072), tiff) As num_bytes " \
                    "FROM ( VALUES (lo_create(0)," \
                    "ST_Astiff((" \
                    "Select ST_UNION(ST_Clip("+rasterTable+".rast, "+ geom +"))" \
              " from geo."+rasterTable+" where ST_Intersects("+ geom +","+rasterTable+".rast)) ) " \
                ")) As v(oid,tiff) ;"
        print sql_query


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
    user = secrets.dev_user
    host = secrets.dev_host
    password = secrets.dev_password
    port = secrets.dev_port
    database = secrets.dev_database

    conn_string= "host='" + host + "' " + \
                 "port='" + port + "' " + \
                 "dbname='" + database + "' " + \
                 "user='" + user + "' " + \
                 "password='" + password + "'"

    c = psycopg2.connect(conn_string)
    return c


