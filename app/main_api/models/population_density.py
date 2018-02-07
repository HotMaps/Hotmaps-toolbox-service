import datetime
from main_api.models import db
from main_api.models.nuts import NutsRG01M
from sqlalchemy import func
from geoalchemy2 import Raster
from main_api.models.lau import Lau
from main_api.models.time import Time

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
        sql_query = \
            "WITH buffer AS (SELECT ST_Buffer(ST_Transform(ST_GeomFromText('" + \
                            geometry + "'), " + \
                            str(PopulationDensityHa.CRS) + "), 0) AS buffer_geom " + \
            ") " + \
            "SELECT (stats).sum, (stats).mean, (stats).count " + \
            "FROM ( " + \
                "SELECT ST_SummaryStats(ST_Union(ST_Clip(rast, 1, buffer_geom, TRUE))) AS stats " + \
                "FROM " + PopulationDensityHa.__table_args__['schema'] + "." + \
                PopulationDensityHa.__tablename__ + ", buffer " + \
                "WHERE ST_Intersects(rast, buffer_geom) " + \
                "AND date = to_date('" + str(year) + "', 'YYYY') " + \
            ") AS foo " + \
            ";"


        query = db.session.execute(sql_query).first()

        if query == None or len(query) < 3:
            return []

        return [{
            'name': 'population',
            'value': str(query[0] or 0),
            'unit': 'person'
        },{
            'name': 'population_density',
            'value': str(query[1] or 0),
            'unit': 'person/ha'
        },{
            'name': 'count',
            'value': str(query[2] or 0),
            'unit': 'cell'
        }]

"""
    Population Density layer as lau
"""
class PopulationDensityLau(db.Model):
    __tablename__ = 'pop_density_lau'
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
        return "<PopDensityLau(comm_id='%s', year='%s', sum='%d', lau='%s')>" % \
               (self.comm_id, self.time.year, self.sum, str(self.lau))

    @staticmethod
    def aggregate_for_selection(geometry, year, level):

        query = db.session.query(
                func.sum(PopulationDensityLau.sum),
                func.avg(PopulationDensityLau.sum),
                func.sum(PopulationDensityLau.count)
            ). \
            join(Lau, PopulationDensityLau.lau). \
            join(Time, PopulationDensityLau.time). \
            filter(Time.year == year). \
            filter(Time.granularity == 'year'). \
            filter(Lau.stat_levl_ == level). \
            filter(func.ST_Within(Lau.geom,
                                  func.ST_Transform(func.ST_GeomFromEWKT(geometry), PopulationDensityLau.CRS))).first()

        if query == None or len(query) < 3:
            return []

        return [{
            'name': 'population',
            'value': str(query[0] or 0),
            'unit': 'person'
        }, {
            'name': 'population_density',
            'value': str(query[1] or 0),
            'unit': 'person'
        }, {
            'name': 'count',
            'value': str(query[2] or 0),
            'unit': 'cell'
        }]

    @staticmethod
    def aggregate_for_nuts_selection(nuts, year, level):
        query = db.session.query(
                func.sum(PopulationDensityLau.sum),
                func.avg(PopulationDensityLau.sum),
                func.sum(PopulationDensityLau.count)
            ). \
            join(Lau, PopulationDensityLau.lau). \
            join(Time, PopulationDensityLau.time). \
            filter(Time.year == year). \
            filter(Time.granularity == 'year'). \
            filter(Lau.stat_levl_ == level). \
            filter(Lau.comm_id.in_(nuts)).first()

        if query == None or len(query) < 3:
                return []

        return [{
            'name': 'population',
            'value': str(query[0] or 0),
            'unit': 'person'
        }, {
            'name': 'population_density',
            'value': str(query[1] or 0),
            'unit': 'person'
        }, {
            'name': 'count',
            'value': str(query[2] or 0),
            'unit': 'cell'
        }]


"""
    Population Density layer as nuts
"""
class PopulationDensityNuts(db.Model):
    __tablename__ = 'pop_density_nuts'
    __table_args__ = (
        db.ForeignKeyConstraint(['nuts_id'], ['geo.nuts_rg_01m.nuts_id']),
        {"schema": 'stat'}
    )

    CRS = 4258

    id = db.Column(db.Integer, primary_key=True)
    nuts_id = db.Column(db.String(14))
    date = db.Column(db.Date)
    count = db.Column(db.BigInteger, name ='_count')
    sum = db.Column(db.Numeric(precision=30, scale=10), name ='_sum' )
    mean = db.Column(db.Numeric(precision=30, scale=10), name ='_mean')
    median = db.Column(db.Numeric(precision=30, scale=10), name ='_median')
    min = db.Column(db.Numeric(precision=30, scale=10), name ='_min')
    max = db.Column(db.Numeric(precision=30, scale=10), name ='_max')
    std = db.Column(db.Numeric(precision=30, scale=10), name ='_std')
    variance = db.Column(db.Numeric(precision=30, scale=10), name ='_variance')
    range = db.Column(db.Numeric(precision=30, scale=10), name ='_range')
    nuts = db.relationship("NutsRG01M")

    def __repr__(self):
        str_date = self.date.strftime("%Y-%m-%d")
        return "<PopDensity(nuts_id='%s', date='%s', value='%d', nuts='%s')>" % (self.nuts_id, str_date, self.value, str(self.nuts))

    @staticmethod
    def aggregate_for_selection(geometry, year, nuts_level):
        query = db.session.query(
                func.sum(PopulationDensityNuts.sum),
                func.avg(PopulationDensityNuts.sum),
                func.count(PopulationDensityNuts.sum)
            ). \
            join(NutsRG01M, PopulationDensityNuts.nuts). \
            filter(PopulationDensityNuts.date == datetime.datetime.strptime(str(year), '%Y')). \
            filter(NutsRG01M.stat_levl_ == nuts_level). \
            filter(func.ST_Within(NutsRG01M.geom, func.ST_Transform(func.ST_GeomFromEWKT(geometry), PopulationDensityNuts.CRS))).first()

        if query == None or len(query) < 3:
            return []

        return [{
            'name': 'population',
            'value': str(query[0] or 0),
            'unit': 'person'
        }, {
            'name': 'population_density',
            'value': str(query[1] or 0),
            'unit': 'person'
        }, {
            'name': 'count',
            'value': str(query[2] or 0),
            'unit': 'nuts'
        }]

    @staticmethod
    def aggregate_for_nuts_selection(nuts, year, nuts_level):
        query = db.session.query(
            func.sum(PopulationDensityNuts.sum),
            func.avg(PopulationDensityNuts.sum),
            func.sum(PopulationDensityNuts.count)
        ). \
            join(NutsRG01M, PopulationDensityNuts.nuts). \
            filter(PopulationDensityNuts.date == datetime.datetime.strptime(str(year), '%Y')). \
            filter(NutsRG01M.stat_levl_ == nuts_level). \
            filter(NutsRG01M.nuts_id.in_(nuts)).first()

        if query == None or len(query) < 3:
                return []

        return [{
            'name': 'population',
            'value': str(query[0] or 0),
            'unit': 'person'
        }, {
            'name': 'population_density',
            'value': str(query[1] or 0),
            'unit': 'person'
        }, {
            'name': 'count',
            'value': str(query[2] or 0),
            'unit': 'cell'
        }]

"""
    PopulationDensityNuts classes for each nuts/lau level
"""
class PopulationDensityLau2():
    @staticmethod
    def aggregate_for_selection(geometry, year):
        return PopulationDensityLau.aggregate_for_selection(geometry=geometry, year=year, level=2)
    @staticmethod
    def aggregate_for_nuts_selection(nuts, year):
        return PopulationDensityLau.aggregate_for_nuts_selection(nuts=nuts, year=year, level=2)

class PopulationDensityNuts3():
    @staticmethod
    def aggregate_for_selection(geometry, year):
        return PopulationDensityNuts.aggregate_for_selection(geometry=geometry, year=year, nuts_level=3)
    @staticmethod
    def aggregate_for_nuts_selection(nuts, year):
        return PopulationDensityNuts.aggregate_for_nuts_selection(nuts=nuts, year=year, nuts_level=3)

class PopulationDensityNuts2():
    @staticmethod
    def aggregate_for_selection(geometry, year):
        return PopulationDensityNuts.aggregate_for_selection(geometry=geometry, year=year, nuts_level=2)
    @staticmethod
    def aggregate_for_nuts_selection(nuts, year):
        return PopulationDensityNuts.aggregate_for_nuts_selection(nuts=nuts, year=year, nuts_level=2)

class PopulationDensityNuts1():
    @staticmethod
    def aggregate_for_selection(geometry, year):
        return PopulationDensityNuts.aggregate_for_selection(geometry=geometry, year=year, nuts_level=1)
    @staticmethod
    def aggregate_for_nuts_selection(nuts, year):
        return PopulationDensityNuts.aggregate_for_nuts_selection(nuts=nuts, year=year, nuts_level=1)

class PopulationDensityNuts0():
    @staticmethod
    def aggregate_for_selection(geometry, year):
        return PopulationDensityNuts.aggregate_for_selection(geometry=geometry, year=year, nuts_level=0)
    @staticmethod
    def aggregate_for_nuts_selection(nuts, year):
        return PopulationDensityNuts.aggregate_for_nuts_selection(nuts=nuts, year=year, nuts_level=0)
