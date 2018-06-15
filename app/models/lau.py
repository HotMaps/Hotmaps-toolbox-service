import datetime

from app import dbGIS as db
from geoalchemy2 import Geometry
from sqlalchemy import func
from geojson import FeatureCollection, Feature
from geoalchemy2.shape import to_shape


class Lau(db.Model):
    __tablename__ = 'lau'
    __table_args__ = (
        {"schema": 'public'}
    )

    CRS = 3035

    gid = db.Column(db.Integer, primary_key=True)
    comm_id = db.Column(db.String(14))
    #name = db.Column(db.String(255))
    stat_levl_ = db.Column(db.Integer)
    shape_area = db.Column(db.Numeric)
    shape_leng = db.Column(db.Numeric)
    geom = db.Column(Geometry('GEOMETRY', 4258))
    year = db.Column(db.Date)

    def __repr__(self):
        return "<Lau(comm_id='%s', level='%s')>" % (
            self.comm_id, self.stat_levl_)

 
