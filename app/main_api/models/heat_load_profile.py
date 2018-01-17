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
    def aggregate_for_month(nuts, year):
        query = db.session.query(
                func.avg(HeatLoadProfileNuts.value),
                func.min(HeatLoadProfileNuts.value),
                func.max(HeatLoadProfileNuts.value),
                HeatLoadProfileNuts.unit,
                Time.month,
                Time.year,
                literal("month", type_=Unicode).label('granularity'),
                Nuts.stat_levl_
            ). \
            join(Nuts, HeatLoadProfileNuts.nuts). \
            join(Time, HeatLoadProfileNuts.time). \
            filter(Time.year == year). \
            filter(Nuts.nuts_id.in_(nuts)). \
            group_by(Time.month, HeatLoadProfileNuts.unit, Time.year, Nuts.stat_levl_). \
            order_by(Time.month.asc()).all()


        if query == None or len(query) < 1:
            return []
        output = []
        nuts_level = -1
        for row in query:
            if (len(row) >= 8):
                nuts_level = row[7]
                output.append({
                    "average": row[0],
                    "min": row[1],
                    "max": row[2],
                    "unit": row[3],
                    "month": row[4],
                    "year": row[5],
                    "granularity": row[6],
                })


        return {
            "values": output,
            "nuts": nuts,
            "nuts_level": nuts_level,
        }


    @staticmethod
    def aggregate_for_hour(nuts, year, month):
        query = db.session.query(
                func.avg(HeatLoadProfileNuts.value),
                func.min(HeatLoadProfileNuts.value),
                func.max(HeatLoadProfileNuts.value),
                HeatLoadProfileNuts.unit,
                Time.hour_of_day,
                Time.month,
                Time.year,
                literal("hour", type_=Unicode).label('granularity'),
                Nuts.stat_levl_
            ). \
            join(Nuts, HeatLoadProfileNuts.nuts). \
            join(Time, HeatLoadProfileNuts.time). \
            filter(Time.year == year). \
            filter(Time.month == month). \
            filter(Nuts.nuts_id.in_(nuts)). \
            group_by(Time.hour_of_day, Time.month, HeatLoadProfileNuts.unit, Time.year, Nuts.stat_levl_). \
            order_by(Time.hour_of_day.asc()).all()


        if query == None or len(query) < 1:
            return []

        output = []
        nuts_level = -1
        for row in query:
            if (len(row) >= 9):
                nuts_level = row[8]
                output.append({
                    "average": row[0],
                    "min": row[1],
                    "max": row[2],
                    "unit": row[3],
                    "hour_of_day": row[4],
                    "month": row[5],
                    "year": row[6],
                    "granularity": row[7],
                })

        return {
            "values": output,
            "nuts": [nuts,],
            "nuts_level": nuts_level,
        }

    @staticmethod
    def aggregate_for_month_hdm(nuts, year):
        query = db.session.query(
                func.avg(HeatLoadProfileNuts.value),
                func.min(HeatLoadProfileNuts.value),
                func.max(HeatLoadProfileNuts.value),
                HeatLoadProfileNuts.unit,
                Time.month,
                Time.year,
                literal("month", type_=Unicode).label('granularity'),
                Nuts.stat_levl_
            ). \
            join(Nuts, HeatLoadProfileNuts.nuts). \
            join(Time, HeatLoadProfileNuts.time). \
            filter(Time.year == year). \
            filter(Nuts.nuts_id.in_(nuts)). \
            group_by(Time.month, HeatLoadProfileNuts.unit, Time.year, Nuts.stat_levl_). \
            order_by(Time.month.asc()).all()


        if query == None or len(query) < 1:
            return []

        output = []
        nuts_level = -1
        for row in query:
            if (len(row) >= 8):
                nuts_level = row[7]
                output.append({
                    "average": row[0],
                    "min": row[1],
                    "max": row[2],
                    "unit": row[3],
                    "month": row[4],
                    "year": row[5],
                    "granularity": row[6],
                })


        return {
            "values": output,
            "nuts": nuts,
            "nuts_level": nuts_level,
        }

