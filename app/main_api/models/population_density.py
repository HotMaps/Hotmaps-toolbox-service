import datetime
from main_api.models import db
from main_api.models.nuts import Nuts
from sqlalchemy import func
from geoalchemy2 import Raster


"""
    Population Density layer as ha
"""
class PopulationDensityHa(db.Model):
    __tablename__ = 'pop_tot_curr_density'
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
        return "<PopDensity1ha(rid='%s', date='%s', filename='%d', rast='%s')>" % (self.rid, str_date, self.filename, str(self.rast))

    @staticmethod
    def aggregate_for_selection(geometry, year):

        # Custom query
        sql_query = "SELECT (stats).sum, (stats).mean, (stats).count FROM (" + \
            "SELECT ST_SummaryStatsAgg(raster_clip, 1, FALSE, 1) AS stats FROM (" + \
                "SELECT ST_Union(ST_Clip(rast, 1, buf.geom, TRUE)) AS raster_clip " + \
                "FROM " + PopulationDensityHa.__table_args__['schema'] + "." + \
                    PopulationDensityHa.__tablename__ + " " + \
                "INNER JOIN (SELECT ST_Buffer(ST_Transform(ST_GeomFromText('" + geometry + "'), " + \
                        str(PopulationDensityHa.CRS) + "), 0) AS geom) AS buf " + \
                "ON ST_Intersects(rast, buf.geom) " + \
                "WHERE date = to_date('" + str(year) + "', 'YYYY') " + \
            ") AS foo) bar ;"

        query = db.session.execute(sql_query).first()

        if query == None or len(query) < 3:
            return []

        return [{
            'name': 'population',
            'value': str(query[0]),
            'unit': 'person'
        },{
            'name': 'population_density',
            'value': str(query[1]),
            'unit': 'person/ha'
        },{
            'name': 'count',
            'value': str(query[2]),
            'unit': 'cell'
        }]

"""
    Population Density layer as nuts
"""
class PopulationDensityNuts(db.Model):
    __tablename__ = 'pop_density'
    __table_args__ = (
        db.ForeignKeyConstraint(['nuts_id'], ['geo.nuts_rg_01m.nuts_id']),
        {"schema": 'stat'}
    )

    CRS = 4258

    id = db.Column(db.Integer, primary_key=True)
    nuts_id = db.Column(db.String(14))
    date = db.Column(db.Date)
    value = db.Column(db.BigInteger)

    nuts = db.relationship("Nuts")

    def __repr__(self):
        str_date = self.date.strftime("%Y-%m-%d")
        return "<PopDensity(nuts_id='%s', date='%s', value='%d', nuts='%s')>" % (self.nuts_id, str_date, self.value, str(self.nuts))

    @staticmethod
    def aggregate_for_selection(geometry, year, nuts_level):

        query = db.session.query(
                func.sum(PopulationDensityNuts.value),
                func.avg(PopulationDensityNuts.value),
                func.count(PopulationDensityNuts.value)
            ). \
            join(Nuts, PopulationDensityNuts.nuts). \
            filter(PopulationDensityNuts.date == datetime.datetime.strptime(str(year), '%Y')). \
            filter(Nuts.stat_levl_ == nuts_level). \
            filter(func.ST_Within(Nuts.geom, func.ST_Transform(func.ST_GeomFromEWKT(geometry), PopulationDensityNuts.CRS))).first()

        if query == None or len(query) < 3:
            return []

        return [{
            'name': 'population',
            'value': str(query[0]),
            'unit': 'person'
        }, {
            'name': 'population_density',
            'value': str(query[1]),
            'unit': 'person'
        }, {
            'name': 'count',
            'value': str(query[2]),
            'unit': 'nuts'
        }]

"""
    PopulationDensityNuts classes for each nuts level
"""

class PopulationDensityNuts3():
    @staticmethod
    def aggregate_for_selection(geometry, year):
        return PopulationDensityNuts.aggregate_for_selection(geometry=geometry, year=year, nuts_level=3)

class PopulationDensityNuts2():
    @staticmethod
    def aggregate_for_selection(geometry, year):
        return PopulationDensityNuts.aggregate_for_selection(geometry=geometry, year=year, nuts_level=2)

class PopulationDensityNuts1():
    @staticmethod
    def aggregate_for_selection(geometry, year):
        return PopulationDensityNuts.aggregate_for_selection(geometry=geometry, year=year, nuts_level=1)

class PopulationDensityNuts0():
    @staticmethod
    def aggregate_for_selection(geometry, year):
        return PopulationDensityNuts.aggregate_for_selection(geometry=geometry, year=year, nuts_level=0)