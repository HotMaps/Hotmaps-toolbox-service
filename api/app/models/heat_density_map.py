from app.models import db
from geoalchemy2 import Raster
from decimal import *
#import logging
#logging.basicConfig()
#logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)



class HeatDensityMapModel(db.Model):
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

class HeatDensityHaModel(db.Model):
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


class HeatDensityLauModel(db.Model):
    __tablename__ = 'heat_tot_curr_density_tif_lau'
    __table_args__ = (
        db.ForeignKeyConstraint(['fk_lau_gid'], ['public.lau.gid']),
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
    #fk_time_id = db.Column(db.BigInteger)


    lau = db.relationship("Lau")
    #time = db.relationship("Time")

    def __repr__(self):
        return "<HeatDensityLau(comm_id='%s', year='%s', sum='%d', lau='%s')>" % \
               (self.comm_id, self.time.year, self.sum, str(self.lau))


class HeatDensityNutsModel(db.Model):
    # the former table name was __tablename__ = 'heat_density_nuts'

    """@staticmethod
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
                                  func.ST_Transform(func.ST_GeomFromEWKT(geometry), HeatDensityNuts.CRS))).first()"""
    __tablename__ = 'heat_tot_curr_density_tif_nuts'
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
