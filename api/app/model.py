
from flask import url_for


from app.decorators.exceptions import ValidationError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, Integer, String, Float, Boolean
from sqlalchemy import Index
from sqlalchemy.orm import relationship, backref
from datetime import datetime
import os

import sqlite3
basedir = os.path.abspath(os.path.dirname(__file__))

db_path = os.path.join(basedir, '../data.sqlite')

DB_NAME="calculation_module.db"




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
                   "cm_description VARCHAR(255),cm_url VARCHAR(255),category VARCHAR(255),layers_needed VARCHAR(255),createdAt REAL(255),updateAt REAL(255),"
                   " PRIMARY KEY(cm_id))")
    conn.commit()
    return conn

def register_calulation_module(data):
    conn = sqlite3.connect(DB_NAME)

    cm_name = data['cm_name']
    category = data['category']
    cm_description = data['cm_description']
    cm_url = data['cm_url']
    cm_Id = data['id']
    layers_needed = data['layers_needed']
    input_components = data['input_components']
    print 'input_components',input_components
    updatedAt = datetime.utcnow()
    createdAt = datetime.utcnow()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO calculation_module (cm_id, cm_name, cm_description, category, cm_url, layers_needed, createdAt, updateAt) VALUES (?,?,?,?,?,?,?,?)", ( cm_Id, cm_name, cm_description, category, cm_url, layers_needed, createdAt, updatedAt ))
    conn.commit()


