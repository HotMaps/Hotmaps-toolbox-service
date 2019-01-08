from app import create_app
import unittest
from app import dbGIS as db
import os.path
from ..test_client import TestClient
from app.model import query_geographic_database
from app.models.indicators import layersData
from app.sql_queries import get_exists_table_query
from .payloads import nuts3_stat
from flask import request
class TestIndicators(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.app = create_app(os.environ.get('FLASK_CONFIG', 'development'))
        cls.ctx = cls.app.app_context()
        cls.ctx.push()
        cls.client = TestClient(cls.app)

    @classmethod
    def tearDownClass(cls):
        cls.ctx.pop()
    

    
    
    def test_indicators_nutslau(self):
        for layer in layersData:
            nuts3_stat['layers'] = [layer]
            print(nuts3_stat)

            rv, json = self.client.post('http://0.0.0.0/api/stats/layers/nuts-lau', data=nuts3_stat)
            with self.subTest(layer=layer, payload=nuts3_stat):
                self.assertTrue(rv.status_code == 200)


    def test_tablenameschema_exists(self):
        for layer in layersData:
            """
            Subtest only available on python 3.4
            """

            with self.subTest(tablename=layersData[layer]['tablename'],schema_hectare=layersData[layer]['schema_hectare']):
                sql_query = get_exists_table_query(tbname=layersData[layer]['tablename'], schema=layersData[layer]['schema_hectare'])
                query = query_geographic_database(sql_query).fetchone()
                print("schema_hectare:"+layersData[layer]['schema_hectare'] + ", tablename:" + layersData[layer]['tablename'] + " => result:" + str(query[0]))
                self.assertTrue(bool(query[0]) == True)

            if layersData[layer]['data_aggregated'] == True:
                with self.subTest(tablename=layersData[layer]['tablename']+"_nuts",schema_scalelvl=layersData[layer]['schema_scalelvl']):
                    sql_query = get_exists_table_query(tbname=layersData[layer]['tablename']+"_nuts", schema=layersData[layer]['schema_scalelvl'])
                    query = query_geographic_database(sql_query).fetchone()
                    print("schema_scalelvl:"+layersData[layer]['schema_scalelvl'] + ", tablename:" + layersData[layer]['tablename']+"_nuts => result:" + str(query[0]))
                    self.assertTrue(bool(query[0]) == True)
                with self.subTest(tablename=layersData[layer]['tablename']+"_lau",schema_scalelvl=layersData[layer]['schema_scalelvl']):
                    sql_query = get_exists_table_query(tbname=layersData[layer]['tablename']+"_lau", schema=layersData[layer]['schema_scalelvl'])
                    query = query_geographic_database(sql_query).fetchone()
                    print("schema_scalelvl:"+layersData[layer]['schema_scalelvl'] + ", tablename:" + layersData[layer]['tablename']+"_lau => result:" + str(query[0]))
                    self.assertTrue(bool(query[0]) == True)