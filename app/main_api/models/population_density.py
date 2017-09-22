import datetime
from main_api.models import db
from main_api.models.nuts import Nuts
from sqlalchemy import func


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
