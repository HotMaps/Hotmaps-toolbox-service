import datetime
from main_api.models import db
from main_api.models.nuts import Nuts
from sqlalchemy import func
from geoalchemy2 import Raster


class PopulationDensity(db.Model):
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


    def aggregate_for_selection(self, geometry, year):

        query = db.session.query(func.sum(PopulationDensity.value)). \
            join(Nuts, PopulationDensity.nuts). \
            filter(PopulationDensity.date == datetime.datetime.strptime(str(year), '%Y')). \
            filter(Nuts.stat_levl_ == 3). \
            filter(func.ST_Within(Nuts.geom, func.ST_Transform(func.ST_GeomFromEWKT(geometry), PopulationDensity.CRS))).first()

        return [{
            'name': 'density',
            'value': query[0],
            'unit': 'citizens'
        }]


class PopulationDensity1ha(db.Model):
    __tablename__ = 'population_1ha'
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


    def aggregate_for_selection(self, geometry, year):

        # Custom query
        # todo: add support for year selection
        sql_query = "SELECT (stats).sum, (stats).mean FROM (" + \
            "SELECT ST_SummaryStatsAgg(raster_clip, 1, TRUE, 1) AS stats FROM (" + \
            "SELECT ST_Union(ST_Clip(rast, 1, buf.geom, FALSE)) AS raster_clip " + \
            "FROM " + PopulationDensity1ha.__table_args__['schema'] + "." + \
                    PopulationDensity1ha.__tablename__ + " " + \
            "INNER JOIN (SELECT ST_Buffer(ST_Transform(ST_GeomFromText('" + geometry + "'), " + \
                    str(PopulationDensity1ha.CRS) + "), 100) AS geom) AS buf " + \
            "ON ST_Intersects(rast, buf.geom)) AS foo) bar;"

        query = db.session.execute(sql_query).first()

        if query == None:
            return []

        return [{
            'name': 'population_density_sum',
            'value': query[0],
            'unit': 'citizens'
        },{
            'name': 'population_density_avg',
            'value': query[1],
            'unit': 'citizens'
        }]


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


    def aggregate_for_selection(self, geometry, year):

        # Custom query
        # todo: add support for year selection
        sql_query = "SELECT (stats).sum, (stats).mean FROM (" + \
            "SELECT ST_SummaryStatsAgg(raster_clip, 1, TRUE, 1) AS stats FROM (" + \
                "SELECT ST_Union(ST_Clip(rast, 1, buf.geom, FALSE)) AS raster_clip " + \
                "FROM " + PopulationDensity1ha.__table_args__['schema'] + "." + \
                        PopulationDensity1ha.__tablename__ + " " + \
                "INNER JOIN (SELECT ST_Buffer(ST_Transform(ST_GeomFromText('" + geometry + "'), " + \
                        str(PopulationDensity1ha.CRS) + "), 100) AS geom) AS buf " + \
                "ON ST_Intersects(rast, buf.geom) " + \
                "WHERE date = to_date('" + str(year) + "', 'YYYY') " + \
            ") AS foo) bar ;"

        query = db.session.execute(sql_query).first()

        if query == None:
            return []

        return [{
            'name': 'population_density_sum',
            'value': query[0],
            'unit': 'Inhabitants'
        },{
            'name': 'population_density_avg',
            'value': query[1],
            'unit': 'Inhabitants/ha'
        }]
