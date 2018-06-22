import datetime

from app import dbGIS as db
from geoalchemy2 import Geometry
from sqlalchemy import func
from geojson import FeatureCollection, Feature
from geoalchemy2.shape import to_shape


class Nuts(db.Model):
    __tablename__ = 'nuts'
    __table_args__ = (
        {"schema": 'geo'}
    )

    CRS = 4258

    gid = db.Column(db.Integer, primary_key=True)
    nuts_id = db.Column(db.String(14))
    name = db.Column(db.String(255))
    stat_levl_ = db.Column(db.Integer)
    shape_area = db.Column(db.Numeric)
    shape_len = db.Column(db.Numeric)
    geom = db.Column(Geometry('GEOMETRY', 4258))
    year = db.Column(db.Date)

    def __repr__(self):
        return "<Nuts(nuts_id='%s', name='%s', level='%s')>" % (
            self.nuts_id, self.name, self.stat_levl_)


class NutsRG01M(db.Model):
    __tablename__ = 'nuts_rg_01m'
    __table_args__ = (
        db.UniqueConstraint('nuts_id'),
        {"schema": 'geo'}
    )

    CRS = 4258

    gid = db.Column(db.Integer, primary_key=True)
    nuts_id = db.Column(db.String(14))
    name = db.Column(db.String(255))
    stat_levl_ = db.Column(db.Integer)
    shape_area = db.Column(db.Numeric)
    shape_len = db.Column(db.Numeric)
    geom = db.Column(Geometry('GEOMETRY', 4258))

    def __repr__(self):
        return "<Nuts(nuts_id='%s', name='%s', level='%s')>" % (
            self.nuts_id, self.name, self.stat_levl_)
