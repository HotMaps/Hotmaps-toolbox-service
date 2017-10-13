import datetime
from main_api.models import db
from geoalchemy2 import Geometry
from main_api.models.nuts import Nuts
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

    def aggregate_for_selection(self, geometry, year):

        query = db.session.query(func.sum(Wwtp.power), func.sum(Wwtp.capacity), Wwtp.unit). \
            filter(Wwtp.date == datetime.datetime.strptime(str(year), '%Y')). \
            filter(func.ST_Within(Wwtp.geom, func.ST_Transform(func.ST_GeomFromEWKT(geometry), Wwtp.CRS))). \
            group_by(Wwtp.unit).first()

        if query == None or len(query) < 3:
            return []

        return [{
            'name': 'power',
            'value': query[0],
            'unit': query[2]
        }, {
            'name': 'capacity',
            'value': query[1],
            'unit': 'Person equivalent'
        }]