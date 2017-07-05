from main_api.models import db



class PopulationDensity(db.Model):
    __tablename__ = 'pop_density'
    __table_args__ = (
        db.ForeignKeyConstraint(['nuts_id'], ['geo.nuts_rg_01m.nuts_id']),
        {"schema": 'stat'}
    )

    id = db.Column(db.Integer, primary_key=True)
    nuts_id = db.Column(db.String(14))
    date = db.Column(db.Date)
    value = db.Column(db.BigInteger)

    nuts = db.relationship("Nuts")

    def __repr__(self):
        str_date = self.date.strftime("%Y-%m-%d")
        return "<PopDensity(nuts_id='%s', date='%s', value='%d', nuts='%s')>" % (self.nuts_id, str_date, self.value, str(self.nuts))
