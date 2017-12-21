import datetime
from main_api.models import db
from geoalchemy2 import Geometry
from main_api.models.nuts import Nuts
from main_api.models.lau import Lau
from sqlalchemy import func



class Wwtp(db.Model):
    __tablename__ = 'wwtp'
    __table_args__ = (
        {"schema": 'geo'}
    )

    CRS = 3035

    gid = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    capacity = db.Column(db.Numeric)
    power = db.Column(db.Numeric)
    unit = db.Column(db.String(255))
    geom = db.Column(Geometry('GEOMETRY', 4258))

    def __repr__(self):
        str_date = self.date.strftime("%Y-%m-%d")
        return "<Wwtp(gid= '%d', date='%s', capacity='%d', power='%d', unit='%s', geom='%s')>" % (
            self.gid, str_date, self.capacity, self.power, self.unit, self.geom)

    @staticmethod
    def aggregate_for_selection(geometry, year):

        query = db.session.query(func.sum(Wwtp.power), func.sum(Wwtp.capacity), Wwtp.unit). \
            filter(Wwtp.date == datetime.datetime.strptime(str(year), '%Y')). \
            filter(func.ST_Within(Wwtp.geom, func.ST_Transform(func.ST_GeomFromEWKT(geometry), Wwtp.CRS))). \
            group_by(Wwtp.unit).first()

        if query == None or len(query) < 3:
            return []

        return [{
            'name': 'power',
            'value': str(query[0] or 0),
            'unit': str(query[2])
        }, {
            'name': 'capacity',
            'value': str(query[1] or 0),
            'unit': 'Person equivalent'
        }]

    @staticmethod
    def aggregate_for_nuts_selection(nuts, year, type, level):
        if type == 'lau':
            try:
                # create subquery to get lau geometries inside
                nuts_geom_query = db.session.query(func.ST_Union(Lau.geom).label('nuts_geom')). \
                    filter(Lau.stat_levl_ == level). \
                    filter(Lau.comm_id.in_(nuts)). \
                    subquery('nuts_geom_query')
            except KeyError:
                return []
        elif type  == 'nuts':
            try:
                # create subquery to get nuts geometries inside
                nuts_geom_query = db.session.query(func.ST_Union(Nuts.geom).label('nuts_geom')). \
                    filter(Nuts.stat_levl_ == level). \
                    filter(Nuts.nuts_id.in_(nuts)). \
                    subquery('nuts_geom_query')
            except KeyError:
                return []
        else:
            return []

        query = db.session.query(func.sum(Wwtp.power), func.sum(Wwtp.capacity), Wwtp.unit). \
            filter(Wwtp.date == datetime.datetime.strptime(str(year), '%Y')). \
            filter(func.ST_Within(Wwtp.geom, func.ST_Transform(nuts_geom_query.c.nuts_geom, Wwtp.CRS))). \
            group_by(Wwtp.unit).first()

        if query == None or len(query) < 3:
            return []

        return [{
            'name': 'power',
            'value': str(query[0] or 0),
            'unit': str(query[2])
        }, {
            'name': 'capacity',
            'value': str(query[1] or 0),
            'unit': 'Person equivalent'
        }]


"""
    WwtpNuts classes for each nuts/lau level
"""
class WwtpLau2():
    @staticmethod
    def aggregate_for_selection(geometry, year):
        return Wwtp.aggregate_for_selection(geometry=geometry, year=year)

    @staticmethod
    def aggregate_for_nuts_selection(nuts, year):
        return Wwtp.aggregate_for_nuts_selection(nuts=nuts, year=year, type='lau', level=2)

class WwtpNuts3():
    @staticmethod
    def aggregate_for_selection(geometry, year):
        return Wwtp.aggregate_for_selection(geometry=geometry, year=year)

    @staticmethod
    def aggregate_for_nuts_selection(nuts, year):
        return Wwtp.aggregate_for_nuts_selection(nuts=nuts, year=year, type='nuts', level=3)

class WwtpNuts2():
    @staticmethod
    def aggregate_for_selection(geometry, year):
        return Wwtp.aggregate_for_selection(geometry=geometry, year=year)

    @staticmethod
    def aggregate_for_nuts_selection(nuts, year):
        return Wwtp.aggregate_for_nuts_selection(nuts=nuts, year=year, type='nuts', level=2)

class WwtpNuts1():
    @staticmethod
    def aggregate_for_selection(geometry, year):
        return Wwtp.aggregate_for_selection(geometry=geometry, year=year)

    @staticmethod
    def aggregate_for_nuts_selection(nuts, year):
        return Wwtp.aggregate_for_nuts_selection(nuts=nuts, year=year, type='nuts', level=1)

class WwtpNuts0():
    @staticmethod
    def aggregate_for_selection(geometry, year):
        return Wwtp.aggregate_for_selection(geometry=geometry, year=year)

    @staticmethod
    def aggregate_for_nuts_selection(nuts, year):
        return Wwtp.aggregate_for_nuts_selection(nuts=nuts, year=year, type='nuts', level=0)
