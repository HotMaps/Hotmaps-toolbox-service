from app import dbGIS as db


class Time(db.Model):
    __tablename__ = 'time'
    __table_args__ = (
        {"schema": 'stat'}
    )

    id = db.Column(db.Integer, primary_key=True)
    granularity = db.Column(db.String(14))
    date = db.Column(db.Date)
    hour_of_year = db.Column(db.BigInteger)
    hour_of_day = db.Column(db.SmallInteger)
    season = db.Column(db.String(14))
    weekday = db.Column(db.String(14))
    day = db.Column(db.SmallInteger)
    month = db.Column(db.SmallInteger)
    year = db.Column(db.SmallInteger)
    timestamp = db.Column(db.DateTime(timezone=False))

    def __repr__(self):
        return "<Time(%s)>" % (self.timestamp.strftime("%Y-%m-%d %H:%M"))
