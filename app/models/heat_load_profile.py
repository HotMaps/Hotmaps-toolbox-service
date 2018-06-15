
from app import dbGIS as db


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