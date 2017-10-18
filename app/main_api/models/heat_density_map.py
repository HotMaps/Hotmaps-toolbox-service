import datetime
from main_api.models import db
from geoalchemy2 import Geometry, Raster
from sqlalchemy import func


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
            'value': query[0],
            'unit': 'GWh'
        },{
            'name': 'heat_density',
            'value': query[1],
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

    def aggregate_for_selection(self, geometry, year):

        # filter(HeatDensityMap.date == datetime.datetime.strptime(str(year), '%Y')). \
        # Custom query
        sql_query = "SELECT (stats).sum, (stats).mean, (stats).count FROM (" + \
            "SELECT ST_SummaryStatsAgg(raster_clip, 1, FALSE, 1) AS stats FROM (" + \
                "SELECT ST_Union(ST_Clip(rast, 1, buf.geom, TRUE)) AS raster_clip " + \
                "FROM " + HeatDensityHa.__table_args__['schema'] + "." + \
                    HeatDensityHa.__tablename__ + " " + \
                "INNER JOIN (SELECT ST_Buffer(ST_Transform(ST_GeomFromText('" + geometry + "'), " + \
                        str(HeatDensityHa.CRS) + "), 0) AS geom) AS buf " + \
                "ON ST_Intersects(rast, buf.geom) " + \
                "WHERE date = to_date('" + str(year) + "', 'YYYY') " + \
            ") AS foo) bar ;"


        query = db.session.execute(sql_query).first()

        if query == None or len(query) < 2:
            return []

        return [{
            'name': 'heat_consumption',
            'value': query[0],
            'unit': 'MWh'
        },{
            'name': 'heat_density',
            'value': query[1],
            'unit': 'MWh/ha'
        }]