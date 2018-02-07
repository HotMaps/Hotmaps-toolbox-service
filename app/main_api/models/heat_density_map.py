import datetime
from main_api.models import db
from main_api.models.nuts import NutsRG01M
from main_api.models.lau import Lau
from main_api.models.time import Time
from geoalchemy2 import Geometry, Raster
from sqlalchemy import func
import json
import sys
#import logging
#logging.basicConfig()
#logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)



class HeatDensityMap(db.Model):
    __tablename__ = 'heat_density_map'
    __table_args__ = (
        {"schema": 'geo'}
    )

    CRS = 3035

    rid = db.Column(db.Integer, primary_key=True)
    rast = db.Column(Raster)
    filename = db.Column(db.String)
    date = db.Column(db.Date)

    def __repr__(self):
        str_date = self.date.strftime("%Y-%m-%d")
        return "<HeatDensityMap(rid= '%d', rast='%s', filename='%s', date='%s')>" % (
            self.rid, self.rast, self.filename, str_date)

    def aggregate_for_selection(self, geometry, year):
        # filter(HeatDensityMap.date == datetime.datetime.strptime(str(year), '%Y')). \
        # Custom query
        # todo: add support for year selection
        sql_query = "SELECT (stats).sum, (stats).mean FROM (" + \
            "SELECT ST_SummaryStatsAgg(raster_clip, 1, TRUE, 1) AS stats FROM (" + \
            "SELECT ST_Union(ST_Clip(rast, 1, buf.geom, FALSE)) AS raster_clip " + \
            "FROM " + HeatDensityMap.__table_args__['schema'] + "." + \
                    HeatDensityMap.__tablename__ + " " + \
            "INNER JOIN (SELECT ST_Buffer(ST_Transform(ST_GeomFromText('" + geometry + "'), " + \
                    str(HeatDensityMap.CRS) + "), 100) AS geom) AS buf " + \
            "ON ST_Intersects(rast, buf.geom)) AS foo) bar;"

        query = db.session.execute(sql_query).first()

        if query == None:
            return []

        return [{
            'name': 'heat_consumption',
            'value': str(query[0] or 0),
            'unit': 'GWh'
        },{
            'name': 'heat_density',
            'value': str(query[1] or 0),
            'unit': 'GWh/ha'
        }]

class HeatDensityHa(db.Model):
    __tablename__ = 'heat_tot_curr_density'
    __table_args__ = (
        {"schema": 'geo'}
    )
    CRS = 3035
    rid = db.Column(db.Integer, primary_key=True)
    rast = db.Column(Raster)
    filename = db.Column(db.String)
    date = db.Column(db.Date)
    def __repr__(self):
        str_date = self.date.strftime("%Y-%m-%d")
        return "<HeatDensityHa(rid= '%d', rast='%s', filename='%s', date='%s')>" % (
            self.rid, self.rast, self.filename, str_date)
    @staticmethod
    def aggregate_for_selection(geometry, year):
        # filter(HeatDensityMap.date == datetime.datetime.strptime(str(year), '%Y')). \
        # Custom query
        sql_query = \
            "WITH buffer AS (SELECT ST_Buffer(ST_Transform(ST_GeomFromText('" + \
            geometry + "'), " + \
            str(HeatDensityHa.CRS) + "), 0) AS buffer_geom " + \
            ") " + \
            "SELECT (stats).sum, (stats).mean, (stats).count " + \
            "FROM ( " + \
            "SELECT ST_SummaryStats(ST_Union(ST_Clip(rast, 1, buffer_geom, TRUE))) AS stats " + \
            "FROM " + HeatDensityHa.__table_args__['schema'] + "." + \
            HeatDensityHa.__tablename__ + ", buffer " + \
            "WHERE ST_Intersects(rast, buffer_geom) " + \
            "AND date = to_date('" + str(year) + "', 'YYYY') " + \
            ") AS foo " + \
            ";"
        query = db.session.execute(sql_query).first()
        if query == None or len(query) < 3:
            return []
        return [{
            'name': 'heat_consumption',
            'value': str(query[0] or 0),
            'unit': 'MWh'
        },{
            'name': 'heat_density',
            'value': str(query[1] or 0),
            'unit': 'MWh/ha'
        },{
            'name': 'count',
            'value': str(query[2] or 0),
            'unit': 'cell'
        }]
    @staticmethod
    def centroid_for_selection(geometry):
        sql_query = \
            "SELECT ST_AsGeoJSON(st_transform((st_pixelascentroids(ST_Clip(heat_tot_curr_density.rast, 1, st_transform(st_geomfromtext( 'Polygon (("+ geometry +"))'::text, 4326),3035), true), 1, true)).geom ,4326)) AS geoJson " + \
            "FROM geo.heat_tot_curr_density " + \
            "WHERE " +  "st_intersects(heat_tot_curr_density.rast,st_transform(st_geomfromtext( 'Polygon(("+ geometry +"))'::text, 4326),3035));"
        query = db.session.execute(sql_query)
        print >> sys.stderr, query
        result = json.dumps([dict(r) for r in query])
        result = json.loads(result)
        print >> sys.stderr, result
        return result

    @staticmethod
    def centroid_for_hectare(point):
        sql_query = \
            "SELECT ST_AsGeoJSON(st_transform((st_pixelascentroids(heat_tot_curr_density.rast, 1, false)).geom ,4326)) AS geoJson," + \
            " ST_Distance((st_pixelascentroids(heat_tot_curr_density.rast, 1, false)).geom, " + \
            "st_transform(st_geomfromtext('POINT("+ point +")'::text, 4326),3035)) as distance " + \
            "FROM geo.heat_tot_curr_density " + \
            "WHERE " +  "st_intersects(heat_tot_curr_density.rast,st_transform(st_geomfromtext('POINT("+ point +")'::text, 4326),3035)) ORDER BY distance ASC limit 1;"
        query = db.session.execute(sql_query)
        #print >> sys.stderr, query
        result = json.dumps([dict(r) for r in query])
        #result = json.loads(result)
        #print >> sys.stderr, result
        return result

    @staticmethod
    def number_of_centroid_for_hectare(geometry):
        sql_query = "SELECT sum(ST_Count(ST_Clip(heat_tot_curr_density.rast, 1, st_transform(st_geomfromtext( 'Polygon (("+ geometry +"))'::text, 4326),3035), true), 1, true)) " + \
                    "FROM geo.heat_tot_curr_density " + \
                    "WHERE " +  "st_intersects(heat_tot_curr_density.rast,st_transform(st_geomfromtext( 'Polygon(("+ geometry +"))'::text, 4326),3035));"
        query = db.session.execute(sql_query).first()
        if query == None :
            result = 0
        else:
            result = str(query[0] or 0)



        return result



class HeatDensityLau(db.Model):
    __tablename__ = 'heat_density_lau'
    __table_args__ = (
        db.ForeignKeyConstraint(['fk_lau_gid'], ['geo.lau.gid']),
        db.ForeignKeyConstraint(['fk_time_id'], ['stat.time.id']),
        {"schema": 'stat'}
    )

    CRS = 3035

    id = db.Column(db.Integer, primary_key=True)
    comm_id = db.Column(db.String(14))
    count = db.Column(db.BigInteger)
    sum = db.Column(db.Numeric(precision=30, scale=10))
    mean = db.Column(db.Numeric(precision=30, scale=10))
    median = db.Column(db.Numeric(precision=30, scale=10))
    min = db.Column(db.Numeric(precision=30, scale=10))
    max = db.Column(db.Numeric(precision=30, scale=10))
    std = db.Column(db.Numeric(precision=30, scale=10))
    variance = db.Column(db.Numeric(precision=30, scale=10))
    range = db.Column(db.Numeric(precision=30, scale=10))
    fk_lau_gid = db.Column(db.BigInteger)
    fk_time_id = db.Column(db.BigInteger)


    lau = db.relationship("Lau")
    time = db.relationship("Time")

    def __repr__(self):
        return "<HeatDensityLau(comm_id='%s', year='%s', sum='%d', lau='%s')>" % \
               (self.comm_id, self.time.year, self.sum, str(self.lau))

    @staticmethod
    def aggregate_for_selection(geometry, year, level):
        query = db.session.query(
                func.sum(HeatDensityLau.sum),
                func.avg(HeatDensityLau.sum),
                func.sum(HeatDensityLau.count)
            ). \
            join(Lau, HeatDensityLau.lau). \
            join(Time, HeatDensityLau.time). \
            filter(Time.year == year). \
            filter(Time.granularity == 'year'). \
            filter(Lau.stat_levl_ == level). \
            filter(func.ST_Within(Lau.geom,
                                  func.ST_Transform(func.ST_GeomFromEWKT(geometry), HeatDensityLau.CRS))).first()

        if query == None or len(query) < 3:
            return []

        return [{
            'name': 'heat_consumption',
            'value': str(query[0] or 0),
            'unit': 'MWh'
        },{
            'name': 'heat_density',
            'value': str(query[1] or 0),
            'unit': 'MWh/ha'
        },{
            'name': 'count',
            'value': str(query[2] or 0),
            'unit': 'cell'
        }]

    @staticmethod
    def aggregate_for_nuts_selection(nuts, year, level):
        query = db.session.query(
                func.sum(HeatDensityLau.sum),
                func.avg(HeatDensityLau.sum),
                func.sum(HeatDensityLau.count)
            ). \
            join(Lau, HeatDensityLau.lau). \
            join(Time, HeatDensityLau.time). \
            filter(Time.year == year). \
            filter(Time.granularity == 'year'). \
            filter(Lau.stat_levl_ == level). \
            filter(Lau.comm_id.in_(nuts)).first()

        if query == None or len(query) < 3:
                return []

        return [{
            'name': 'heat_consumption',
            'value': str(query[0] or 0),
            'unit': 'MWh'
        }, {
            'name': 'heat_density',
            'value': str(query[1] or 0),
            'unit': 'MWh/ha'
        }, {
            'name': 'count',
            'value': str(query[2] or 0),
            'unit': 'cell'
        }]



class HeatDensityNuts(db.Model):
    __tablename__ = 'heat_density_nuts'
    __table_args__ = (
        db.ForeignKeyConstraint(['nuts_id'], ['geo.nuts_rg_01m.nuts_id']),
        {"schema": 'stat'}
    )

    CRS = 4258

    id = db.Column(db.Integer, primary_key=True)
    nuts_id = db.Column(db.String(14))
    date = db.Column(db.Date)
    count = db.Column(db.BigInteger)
    sum = db.Column(db.Numeric(precision=30, scale=10))
    mean = db.Column(db.Numeric(precision=30, scale=10))
    median = db.Column(db.Numeric(precision=30, scale=10))
    min = db.Column(db.Numeric(precision=30, scale=10))
    max = db.Column(db.Numeric(precision=30, scale=10))
    std = db.Column(db.Numeric(precision=30, scale=10))
    variance = db.Column(db.Numeric(precision=30, scale=10))
    range = db.Column(db.Numeric(precision=30, scale=10))


    nuts = db.relationship("NutsRG01M")

    def __repr__(self):
        str_date = self.date.strftime("%Y-%m-%d")
        return "<HeatDensityNuts(nuts_id='%s', date='%s', sum='%d', nuts='%s')>" % (
        self.nuts_id, str_date, self.sum, str(self.nuts))

    @staticmethod
    def aggregate_for_selection(geometry, year, nuts_level):
        query = db.session.query(
                func.sum(HeatDensityNuts.sum),
                func.avg(HeatDensityNuts.sum),
                func.count(HeatDensityNuts.sum)
            ). \
            join(NutsRG01M, HeatDensityNuts.nuts). \
            filter(HeatDensityNuts.date == datetime.datetime.strptime(str(year), '%Y')). \
            filter(NutsRG01M.stat_levl_ == nuts_level). \
            filter(func.ST_Within(NutsRG01M.geom,
                                  func.ST_Transform(func.ST_GeomFromEWKT(geometry), HeatDensityNuts.CRS))).first()


        if query == None or len(query) < 3:
            return []

        return [{
            'name': 'heat_consumption',
            'value': str(query[0] or 0),
            'unit': 'MWh'
        },{
            'name': 'heat_density',
            'value': str(query[1] or 0),
            'unit': 'MWh/ha'
        },{
            'name': 'count',
            'value': str(query[2] or 0),
            'unit': 'nuts'
        }]

    @staticmethod
    def aggregate_for_nuts_selection(nuts, year, nuts_level):
        query = db.session.query(
                func.sum(HeatDensityNuts.sum),
                func.avg(HeatDensityNuts.sum),
                func.sum(HeatDensityNuts.count)
            ). \
            join(NutsRG01M, HeatDensityNuts.nuts). \
            filter(HeatDensityNuts.date == datetime.datetime.strptime(str(year), '%Y')). \
            filter(NutsRG01M.stat_levl_ == nuts_level). \
            filter(NutsRG01M.nuts_id.in_(nuts)).first()

        if query == None or len(query) < 3:
            return []

        return [{
            'name': 'heat_consumption',
            'value': str(query[0] or 0),
            'unit': 'MWh'
        },{
            'name': 'heat_density',
            'value': str(query[1] or 0),
            'unit': 'MWh/ha'
        },{
            'name': 'count',
            'value': str(query[2] or 0),
            'unit': 'cell'
        }]

"""
    HeatDensityNuts classes for each nuts/lau level
"""
class HeatDensityLau2():
    @staticmethod
    def aggregate_for_selection(geometry, year):
        return HeatDensityLau.aggregate_for_selection(geometry=geometry, year=year, level=2)
    @staticmethod
    def aggregate_for_nuts_selection(nuts, year):
        return HeatDensityLau.aggregate_for_nuts_selection(nuts=nuts, year=year, level=2)

class HeatDensityNuts3():
    @staticmethod
    def aggregate_for_selection(geometry, year):
        return HeatDensityNuts.aggregate_for_selection(geometry=geometry, year=year, nuts_level=3)
    @staticmethod
    def aggregate_for_nuts_selection(nuts, year):
        return HeatDensityNuts.aggregate_for_nuts_selection(nuts=nuts, year=year, nuts_level=3)

class HeatDensityNuts2():
    @staticmethod
    def aggregate_for_selection(geometry, year):
        return HeatDensityNuts.aggregate_for_selection(geometry=geometry, year=year, nuts_level=2)
    @staticmethod
    def aggregate_for_nuts_selection(nuts, year):
        return HeatDensityNuts.aggregate_for_nuts_selection(nuts=nuts, year=year, nuts_level=2)

class HeatDensityNuts1():
    @staticmethod
    def aggregate_for_selection(geometry, year):
        return HeatDensityNuts.aggregate_for_selection(geometry=geometry, year=year, nuts_level=1)
    @staticmethod
    def aggregate_for_nuts_selection(nuts, year):
        return HeatDensityNuts.aggregate_for_nuts_selection(nuts=nuts, year=year, nuts_level=1)

class HeatDensityNuts0():
    @staticmethod
    def aggregate_for_selection(geometry, year):
        return HeatDensityNuts.aggregate_for_selection(geometry=geometry, year=year, nuts_level=0)
    @staticmethod
    def aggregate_for_nuts_selection(nuts, year):
        return HeatDensityNuts.aggregate_for_nuts_selection(nuts=nuts, year=year, nuts_level=0)
