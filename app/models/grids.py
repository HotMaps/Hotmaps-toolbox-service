from app.models import   dbGIS as db
from geoalchemy2 import Geometry


class Grid1Km(db.Model):
    __tablename__ = 'grid_1km'
    __table_args__ = (
        {"schema": 'geo'}
    )

    CRS = 3035

    gid = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.Numeric)
    xmin = db.Column('__xmin', db.Numeric)
    xmax = db.Column('__xmax', db.Numeric)
    ymin = db.Column(db.Numeric)
    ymax = db.Column(db.Numeric)
    geom = db.Column(Geometry('GEOMETRY', CRS))

    def __repr__(self):
        return "<Grid1km(gid= '%d', id='%d', xmin='%d', xmax='%d',ymin='%d',ymax='%d',)>" % (
            self.gid, self.id, self.xmin, self.xmax, self.ymin, self.ymax)

