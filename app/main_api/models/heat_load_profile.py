import datetime, logging
from main_api.models import db
from main_api.models.nuts import Nuts
from main_api.models.time import Time
from geoalchemy2 import Geometry, Raster
from sqlalchemy import func
from sqlalchemy.sql import literal
from sqlalchemy.types import Unicode


#logging.basicConfig()
#logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


class HeatLoadProfileNuts(db.Model):
    __tablename__ = 'load_profile'
    __table_args__ = (
        db.ForeignKeyConstraint(['fk_nuts_gid'], ['geo.nuts.gid'], name='load_profile_nuts_gid_fkey'),
        db.ForeignKeyConstraint(['fk_time_id'], ['stat.time.id'], name='load_profile_time_id_fkey'),
        {"schema": 'stat'}
    )

    CRS = 4258

    id = db.Column(db.Integer, primary_key=True)
    nuts_id = db.Column(db.String(14))
    process_id = db.Column(db.Integer)
    process = db.Column(db.String())
    unit = db.Column(db.String())
    value = db.Column(db.Numeric(precision=30, scale=10))
    fk_nuts_gid = db.Column(db.BigInteger)
    fk_time_id = db.Column(db.BigInteger)

    nuts = db.relationship("Nuts")
    time = db.relationship("Time")

    def __repr__(self):
        return "<HeatLoadProfileNuts(nuts_id='%s', time='%s', value='%d', unit='%s')>" % (
        self.nuts_id, str(self.time), self.value, self.unit)

    @staticmethod
    def aggregate_for_month(nuts_id, year):
        query = db.session.query(
                func.avg(HeatLoadProfileNuts.value),
                HeatLoadProfileNuts.unit,
                Time.month,
                Time.year,
                literal("month", type_=Unicode).label('granularity'),
                Nuts.nuts_id,
                Nuts.name,
                Nuts.stat_levl_
            ). \
            join(Nuts, HeatLoadProfileNuts.nuts). \
            join(Time, HeatLoadProfileNuts.time). \
            filter(Time.year == year). \
            filter(Nuts.nuts_id == nuts_id). \
            group_by(Time.month, HeatLoadProfileNuts.unit, Time.year, Nuts.nuts_id, Nuts.name, Nuts.stat_levl_). \
            order_by(Time.month.asc()).all()


        if query == None or len(query) < 1:
            return []

        output = []
        for row in query:
            if (len(row) >= 8):
                output.append({
                    "value": row[0],
                    "unit": row[1],
                    "month": row[2],
                    "year": row[3],
                    "granularity": row[4],
                    "nuts_id": row[5],
                    "nuts_name": row[6],
                    "nuts_level": row[7]
                })

        return output


    @staticmethod
    def aggregate_for_hour(nuts_id, year, month):
        query = db.session.query(
                func.avg(HeatLoadProfileNuts.value),
                HeatLoadProfileNuts.unit,
                Time.hour_of_day,
                Time.month,
                Time.year,
                literal("hour", type_=Unicode).label('granularity'),
                Nuts.nuts_id,
                Nuts.name,
                Nuts.stat_levl_
            ). \
            join(Nuts, HeatLoadProfileNuts.nuts). \
            join(Time, HeatLoadProfileNuts.time). \
            filter(Time.year == year). \
            filter(Time.month == month). \
            filter(Nuts.nuts_id == nuts_id). \
            group_by(Time.hour_of_day, Time.month, HeatLoadProfileNuts.unit, Time.year, Nuts.nuts_id, Nuts.name, Nuts.stat_levl_). \
            order_by(Time.hour_of_day.asc()).all()


        if query == None or len(query) < 1:
            return []

        output = []
        for row in query:
            if (len(row) >= 8):
                output.append({
                    "value": row[0],
                    "unit": row[1],
                    "hour_of_day": row[2],
                    "month": row[3],
                    "year": row[4],
                    "granularity": row[5],
                    "nuts_id": row[6],
                    "nuts_name": row[7],
                    "nuts_level": row[8]
                })

        return output

