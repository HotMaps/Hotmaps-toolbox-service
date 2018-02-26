import datetime, logging
from main_api import settings
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
	def aggregate_for_year(nuts, year):
		print ('nuts {} '.format(nuts))
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
	def aggregate_for_month(nuts, year, month):
		query = db.session.query(
				func.avg(HeatLoadProfileNuts.value),
				func.min(HeatLoadProfileNuts.value),
				func.max(HeatLoadProfileNuts.value),
				HeatLoadProfileNuts.unit,
				Time.day,
				Time.month,
				Time.year,
				literal("day", type_=Unicode).label('granularity'),
				Nuts.stat_levl_
			). \
			join(Nuts, HeatLoadProfileNuts.nuts). \
			join(Time, HeatLoadProfileNuts.time). \
			filter(Time.year == year). \
			filter(Time.month == month). \
			filter(Nuts.nuts_id.in_(nuts)). \
			group_by(Time.day, Time.month, HeatLoadProfileNuts.unit, Time.year, Nuts.stat_levl_). \
			order_by(Time.day.asc()).all()


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
					"day": row[4],
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
	def aggregate_for_day(nuts, year, month, day, nuts_level):
		query = db.session.query(
				func.sum(HeatLoadProfileNuts.value),
				HeatLoadProfileNuts.unit,
				Time.hour_of_day,
				Time.day,
				Time.month,
				Time.year,
				literal("hour", type_=Unicode).label('granularity'),
			). \
			join(Nuts, HeatLoadProfileNuts.nuts). \
			join(Time, HeatLoadProfileNuts.time). \
			filter(Time.year == year). \
			filter(Time.month == month). \
			filter(Time.day == day). \
			filter(Nuts.nuts_id.in_(nuts)). \
			group_by(Time.hour_of_day, Time.day, Time.month, HeatLoadProfileNuts.unit, Time.year). \
			order_by(Time.hour_of_day.asc()).all()
		if query == None or len(query) < 1:
			return []

		output = []
		for row in query:
			if (len(row) >= 7):

				output.append({
					"value": row[0],
					"unit": row[1],
					"hour_of_day": row[2],
					"day": row[3],
					"month": row[4],
					"year": row[5],
					"granularity": row[6]
				})

		return {
			"values": output,
			"nuts": [nuts,],
			"nuts_level": nuts_level,
		}

	@staticmethod
	def aggregate_by_hectare(year, month, day, geometry):

		# Check the type of the query
		if month != 0 and day != 0:
			by = 'byDay'
		elif month != 0:
			by = 'byMonth'
		else:
			by = 'byYear'
		

		# Custom Query
		sql_query = "with subAreas as (SELECT ST_Intersection(ST_Transform(ST_GeomFromText(\'" + geometry +"\',4326),4258),nuts.geom) as soustracteGeom, " +\
							"nuts.gid " +\
							"FROM geo.nuts " +\
							"where ST_Intersects(nuts.geom,ST_Transform(ST_GeomFromText(\'" + geometry +"\',4326),4258)) " + \
							"AND STAT_LEVL_=2 AND year = to_date('" + str(year) + "','YYYY')), " +\
						"statBySubAreas as (SELECT (ST_SummaryStatsAgg(ST_Clip(heat_tot_curr_density.rast,1, " +\
							"ST_Transform(subAreas.soustracteGeom,3035),0,true),1,true)).* as stat, subAreas.gid " +\
							"FROM subAreas, geo.heat_tot_curr_density " +\
							"WHERE ST_Intersects(heat_tot_curr_density.rast,ST_Transform(subAreas.soustracteGeom,3035)) group by subAreas.gid), " +\
						"statLoadProfilBySubarea as (select stat.load_profile.nuts_id as load_profile_nutsid, stat.load_profile.value as val_load_profile, " +\
							"stat.time.month as month_of_year, " +\
							"stat.time.hour_of_year as hour_of_year, " +\
							"stat.time.day as day_of_month, " +\
    						"stat.time.hour_of_day as hour_of_day, " +\
							"statBySubAreas.count as statCount, statBySubAreas.sum as statSum_HD " +\
							"from stat.load_profile " +\
							"left join statBySubAreas on statBySubAreas.gid = stat.load_profile.fk_nuts_gid " +\
							"inner join stat.time on stat.load_profile.fk_time_id = stat.time.id " +\
							"WHERE fk_nuts_gid is not null and fk_time_id is not null " +\
							"AND statBySubAreas.gid = stat.load_profile.fk_nuts_gid AND stat.time.year = " + str(year) + " " +\
							"order by stat.time.hour_of_year), " +\
						"totalLoadprofile as ( " +\
							"select sum(val_load_profile) as tot_load_profile,load_profile_nutsid " +\
							"from statLoadProfilBySubarea group by load_profile_nutsid), " +\
						"normalizedData as (select sum(val_load_profile/tot_load_profile*statSum_HD) as normalizedCalutation, " +\
							"hour_of_year, month_of_year, day_of_month, hour_of_day " +\
							"from statLoadProfilBySubarea " +\
							"inner join totalLoadprofile on statLoadProfilBySubarea.load_profile_nutsid = totalLoadprofile.load_profile_nutsid " +\
							"group by hour_of_year, month_of_year, hour_of_day, day_of_month " +\
							"order by hour_of_year) " +\
						"select "

		if by == 'byYear':
			sql_query += "min(normalizedCalutation), max(normalizedCalutation), avg(normalizedCalutation), month_of_year " +\
						"from normalizedData " +\
						"group by month_of_year " +\
						"order by month_of_year"
		elif by == 'byMonth':
			sql_query += "min(normalizedCalutation), max(normalizedCalutation), avg(normalizedCalutation), day_of_month " +\
						"from normalizedData " +\
						"where month_of_year = " + str(month) + " " +\
						"group by day_of_month, month_of_year " +\
						"order by day_of_month"
		else:
			sql_query += "normalizedCalutation, hour_of_day " +\
						"from normalizedData " +\
						"where day_of_month = " + str(day) + " " +\
						"and month_of_year = " + str(month) + " " +\
						"group by normalizedCalutation, hour_of_day " +\
						"order by hour_of_day"		

		# Execution of the query
		query = db.session.execute(sql_query)

		# Storing the results
		output = []
		if by == 'byYear':
			for c, q in enumerate(query):
				output.append({
					'year': year,
					'month': q[3],
					'granularity': 'month',
					'unit': 'kW',
					'min': q[0],
					'max': q[1],
					'average': q[2]
					})
		elif by == 'byMonth':
			for c, q in enumerate(query):
				output.append({
					'year': year,
					'month': month,
					'day': q[3],
					'granularity': 'day',
					'unit': 'kW',
					'min': q[0],
					'max': q[1],
					'average': q[2]
					})
		else:
			for c, q in enumerate(query):
				output.append({
					'year': year,
					'month': month,
					'day': day,
					'hour_of_day': q[1],
					'granularity': 'hour',
					'unit': 'kW',
					'value': q[0]
					})

		'''for c, o in enumerate(output):
			print(output[c])'''
		
		return {
			"values": output
		}
		


	@staticmethod
	def duration_curve(year, nuts):

		# Custom Query
		sql_query = "WITH nutsSelection as (select gid from geo.nuts " +\
						"WHERE nuts_id IN ("+nuts+") AND geo.nuts.year = to_date('" + str(year) + "','YYYY')) " +\
					"SELECT sum(stat.load_profile.value) as val, stat.time.hour_of_year as hoy from stat.load_profile " +\
						"INNER JOIN nutsSelection on stat.load_profile.fk_nuts_gid = nutsSelection.gid " +\
						"INNER JOIN stat.time on stat.load_profile.fk_time_id = stat.time.id " +\
						"WHERE fk_nuts_gid is not null and fk_time_id is not null " +\
						"AND stat.load_profile.fk_nuts_gid = nutsSelection.gid " +\
						"GROUP BY hoy " +\
						"HAVING	COUNT(value)=COUNT(*) " +\
						"ORDER BY val DESC;"

		# Execution of the query
		query = db.session.execute(sql_query)

		# Store query results in a list
		listAllValues = []
		for q in query:
			listAllValues.append(q[0])

		# Creation of points and sampling of the values
		finalListPoints = HeatLoadProfileNuts.sampling_data(listAllValues)

		return finalListPoints


	@staticmethod
	def duration_curve_hectares(year, geometry):

		sql_query = "with subAreas as (SELECT ST_Intersection(ST_Transform(ST_GeomFromText(\'" + geometry +"\',4326),4258),nuts.geom) as soustracteGeom, " +\
							"nuts.gid " +\
							"FROM geo.nuts " +\
							"where ST_Intersects(nuts.geom,ST_Transform(ST_GeomFromText(\'" + geometry +"\',4326),4258)) " + \
							"AND STAT_LEVL_=2 AND year = to_date('" + str(year) + "','YYYY')), " +\
						"statBySubAreas as (SELECT (ST_SummaryStatsAgg(ST_Clip(heat_tot_curr_density.rast,1, " +\
							"ST_Transform(subAreas.soustracteGeom,3035),0,true),1,true)).* as stat, subAreas.gid " +\
							"FROM subAreas, geo.heat_tot_curr_density " +\
							"WHERE ST_Intersects(heat_tot_curr_density.rast,ST_Transform(subAreas.soustracteGeom,3035)) group by subAreas.gid), " +\
						"statLoadProfilBySubarea as (select stat.load_profile.nuts_id as load_profile_nutsid, stat.load_profile.value as val_load_profile, " +\
							"stat.time.month as month_of_year, " +\
							"stat.time.hour_of_year as hour_of_year, " +\
							"stat.time.day as day_of_month, " +\
    						"stat.time.hour_of_day as hour_of_day, " +\
							"statBySubAreas.count as statCount, statBySubAreas.sum as statSum_HD " +\
							"from stat.load_profile " +\
							"left join statBySubAreas on statBySubAreas.gid = stat.load_profile.fk_nuts_gid " +\
							"inner join stat.time on stat.load_profile.fk_time_id = stat.time.id " +\
							"WHERE fk_nuts_gid is not null and fk_time_id is not null " +\
							"AND statBySubAreas.gid = stat.load_profile.fk_nuts_gid AND stat.time.year = " + str(year) + " " +\
							"order by stat.time.hour_of_year), " +\
						"totalLoadprofile as ( " +\
							"select sum(val_load_profile) as tot_load_profile,load_profile_nutsid " +\
							"from statLoadProfilBySubarea group by load_profile_nutsid) " +\
						"select sum(val_load_profile/tot_load_profile*statSum_HD) as normalizedCalutation,hour_of_year " +\
							"from statLoadProfilBySubarea " +\
							"inner join totalLoadprofile on statLoadProfilBySubarea.load_profile_nutsid = totalLoadprofile.load_profile_nutsid " +\
							"group by hour_of_year " +\
							"order by normalizedCalutation DESC;"


		# Execution of the query
		query = db.session.execute(sql_query)

		# Store query results in a list
		listAllValues = []
		for q in query:
			listAllValues.append(q[0])

		# Creation of points and sampling of the values
		finalListPoints = HeatLoadProfileNuts.sampling_data(listAllValues)

		return finalListPoints


	@staticmethod
	def sampling_data(listValues):
		# Get number of values
		numberOfValues = len(listValues)

		# Create the points for the curve with the X and Y axis
		listPoints = []
		for n, l in enumerate(listValues):
			listPoints.append({
				'X':n+1,
				'Y':listValues[n]
			})

		# Sampling of the values
		cut1 = int(numberOfValues*settings.POINTS_FIRST_GROUP_PERCENTAGE) 
		cut2 = int(cut1+(numberOfValues*settings.POINTS_SECOND_GROUP_PERCENTAGE)) 
		cut3 = int(cut2+(numberOfValues*settings.POINTS_THIRD_GROUP_PERCENTAGE)) 

		firstGroup = listPoints[0:cut1:settings.POINTS_FIRST_GROUP_STEP]
		secondGroup = listPoints[cut1:cut2:settings.POINTS_SECOND_GROUP_STEP]
		thirdGroup = listPoints[cut2:cut3:settings.POINTS_THIRD_GROUP_STEP]
		fourthGroup = listPoints[cut3:numberOfValues:settings.POINTS_FOURTH_GROUP_STEP]

		# Get min and max values needed for the sampling list
		maxValue = min(listPoints)
		minValue = max(listPoints)

		# Concatenate the groups to a new list of points (sampling list)
		finalListPoints = firstGroup+secondGroup+thirdGroup+fourthGroup

		# Add max value at the beginning if the list doesn't contain it
		if maxValue not in finalListPoints:
			finalListPoints.insert(0, maxValue)

		# Add min value at the end if the list doesn't contain it
		if minValue not in finalListPoints:
			finalListPoints.append(minValue)

		return finalListPoints

"""    @staticmethod
	def aggregate_for_month_hdm(nuts, year):
		query = db.session.query(
				func.avg(HeatLoadProfileNuts.value),
				func.min(HeatLoadProfileNuts.value),
				func.max(HeatLoadProfileNuts.valuesalue),
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

"""