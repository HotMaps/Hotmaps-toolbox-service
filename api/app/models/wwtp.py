from app import dbGIS as db
from geoalchemy2 import Geometry


class WwtpModel(db.Model):
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

