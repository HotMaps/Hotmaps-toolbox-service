from app import dbGIS as db
from geoalchemy2 import Raster
from decimal import *
"""
    Population Density layer as ha
"""
class PopulationDensityHaModel(db.Model):
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


"""
    Population Density layer as lau
"""
class PopulationDensityLauModel(db.Model):
    __tablename__ = 'pop_tot_curr_density_lau_test'

    """__table_args__ = (
        db.ForeignKeyConstraint(['fk_lau_gid'], ['geo.lau.gid']),
        db.ForeignKeyConstraint(['fk_time_id'], ['stat.time.id']),
        {"schema": 'stat'}
    )
"""
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
        return "<PopDensityLau(comm_id='%s', year='%s', sum='%d', lau='%s')>" % \
               (self.comm_id, self.time.year, self.sum, str(self.lau))


"""
    Population Density layer as nuts
"""
class PopulationDensityNutsModel(db.Model):
    __tablename__ = 'pop_tot_curr_density_tif_nuts'
    __table_args__ = (
        db.ForeignKeyConstraint(['nuts_id'], ['geo.nuts_rg_01m.nuts_id']),
        {"schema": 'stat'}
    )

    CRS = 4258

    id = db.Column(db.Integer, primary_key=True)
    nuts_id = db.Column(db.String(14))
    #date = db.Column(db.Date)
    count = db.Column(db.BigInteger)
    sum = db.Column(db.Numeric(precision=30, scale=10) )
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
        return "<PopDensity(nuts_id='%s', date='%s', value='%d', nuts='%s')>" % (self.nuts_id, str_date, self.value, str(self.nuts))

