from app import create_app
import unittest
from app import dbGIS as db
import os.path
from ..test_client import TestClient
from app.model import query_geographic_database
from app.models.indicators import layersData
from app.sql_queries import get_exists_table_query
from .payloads import nuts3_stat

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
        """
            These tests call the API and try to get result from a specific payload and endpoint. 
            These tests control the functionality of the indicator, as on the client part.
            It create the payload, and send it to the API ('api/stats/layers/nuts-lau') from each layer.
        """
        for layer in layersData:
            if('NUTS 3' in layersData[layer]['data_lvl']):
                nuts3_stat['layers'] = [layer]
                #print(nuts3_stat)
                
                with self.subTest(layer=layer, payload=nuts3_stat):
                    try:
                        rv, json = self.client.post('api/stats/layers/nuts-lau', data=nuts3_stat)
                        self.assertTrue(rv.status_code == 200)
                    except Exception as e:
                        #print(e)
                        self.assertTrue(False)
    
    def test_aggregateddata_statlvl_nutslau(self):
        """
        This function test if aggregated data are in the database. 
        The test runs over all indicators and check data in with schema_scalelvl (the schema) and the tablename (tablename of the dataset). 
        For the tablename, "_lau" and "_nuts" are added are added at the end of the tablename. 

        At nuts level, every stat level are tested (column name: stat_levl_), from 0 to 3.
            0=NUTS 0
            1=NUTS 1
            2=NUTS 2
            3=NUTS 3
        The query return the count of rows available in the table. 
        Result:
            Query returns 0 => No data avalaible for the specific scale
            Query return >= 1 => Data are available in the specific scale
        """
        for layer in layersData:
            if layersData[layer]['data_aggregated'] == True:
                sql_querie = "select count(*) from "+layersData[layer]['schema_scalelvl']+"."+layersData[layer]['tablename']
                sql_querie_lau = sql_querie + "_lau limit 100"
                #print(sql_querie_lau)
                with self.subTest(stat_levl_='lau',tablename=layersData[layer]['schema_scalelvl']+"."+layersData[layer]['tablename']+"_lau"):
                    try:
                        query = query_geographic_database(sql_querie_lau).fetchone()
                        self.assertTrue(int(query[0]) >= 1)
                    except Exception as e:
                        #print(e)
                        self.assertTrue(False)
                for i in range(0,4):
                    sql_querie_nuts = sql_querie + "_nuts where stat_levl_ = "+str(i)
                    #print(sql_querie_nuts)
                    with self.subTest(stat_levl_=i,tablename=layersData[layer]['schema_scalelvl']+"."+layersData[layer]['tablename']+"_nuts"):
                        try:
                            query = query_geographic_database(sql_querie_nuts).fetchone()
                            self.assertTrue(int(query[0]) >= 1)
                        except Exception as e:
                            #print(e)
                            self.assertTrue(False)
                    
            

    def test_tablenameschema_exists(self):
        """
        This test controls if the table exist in the specified schema.
        The query returns True or False.
            True=Tablename exists in the schema
            False=Tablename does'nt exist in the schema
        """
        for layer in layersData:
            """
                Subtest only available on python 3.4
            """

            with self.subTest(tablename=layersData[layer]['tablename'],schema_hectare=layersData[layer]['schema_hectare']):
                sql_query = get_exists_table_query(tbname=layersData[layer]['tablename'], schema=layersData[layer]['schema_hectare'])
                query = query_geographic_database(sql_query).fetchone()
                #print("schema_hectare:"+layersData[layer]['schema_hectare'] + ", tablename:" + layersData[layer]['tablename'] + " => result:" + str(query[0]))
                self.assertTrue(bool(query[0]) == True)

            if layersData[layer]['data_aggregated'] == True:
                with self.subTest(tablename=layersData[layer]['tablename']+"_nuts",schema_scalelvl=layersData[layer]['schema_scalelvl']):
                    sql_query = get_exists_table_query(tbname=layersData[layer]['tablename']+"_nuts", schema=layersData[layer]['schema_scalelvl'])
                    query = query_geographic_database(sql_query).fetchone()
                    #print("schema_scalelvl:"+layersData[layer]['schema_scalelvl'] + ", tablename:" + layersData[layer]['tablename']+"_nuts => result:" + str(query[0]))
                    self.assertTrue(bool(query[0]) == True)
                with self.subTest(tablename=layersData[layer]['tablename']+"_lau",schema_scalelvl=layersData[layer]['schema_scalelvl']):
                    sql_query = get_exists_table_query(tbname=layersData[layer]['tablename']+"_lau", schema=layersData[layer]['schema_scalelvl'])
                    query = query_geographic_database(sql_query).fetchone()
                    #print("schema_scalelvl:"+layersData[layer]['schema_scalelvl'] + ", tablename:" + layersData[layer]['tablename']+"_lau => result:" + str(query[0]))
                    self.assertTrue(bool(query[0]) == True)