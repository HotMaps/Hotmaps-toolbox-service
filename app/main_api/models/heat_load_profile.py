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
	def aggregate_for_day(nuts, year, month, day):
		query = db.session.query(
				HeatLoadProfileNuts.value,
				HeatLoadProfileNuts.unit,
				Time.hour_of_day,
				Time.day,
				Time.month,
				Time.year,
				literal("hour", type_=Unicode).label('granularity'),
				Nuts.stat_levl_
			). \
			join(Nuts, HeatLoadProfileNuts.nuts). \
			join(Time, HeatLoadProfileNuts.time). \
			filter(Time.year == year). \
			filter(Time.month == month). \
			filter(Time.day == day). \
			filter(Nuts.nuts_id.in_(nuts)). \
			group_by(HeatLoadProfileNuts.value, Time.hour_of_day, Time.day, Time.month, HeatLoadProfileNuts.unit, Time.year, Nuts.stat_levl_). \
			order_by(Time.hour_of_day.asc()).all()

		print(query)
		if query == None or len(query) < 1:
			return []

		output = []
		nuts_level = -1
		for row in query:
			if (len(row) >= 8):
				nuts_level = row[7]
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
	def duration_curve(year, nuts):

		listAllValues = []
		valuesByNuts = {}
		listOfNuts = []
		valuesToSample = []

		# Store nuts in new custom list
		nutsPayload = []
		for n in nuts:
			n = n[:4]
			if n not in nutsPayload:
				nutsPayload.append(str(n))

		# Adapt format of list for the query
		nutsListQuery = str(nutsPayload)
		nutsListQuery = nutsListQuery[1:]
		nutsListQuery = nutsListQuery[:-1]

		# Query
		'''sql_query = "select t.val, t.nuts, t.hoy " +\
						"from (select stat.load_profile.value as val, " +\
						"       stat.load_profile.nuts_id as nuts, stat.time.hour_of_year as hoy " +\
						"       from stat."+ HeatLoadProfileNuts.__tablename__+", stat.time " +\
						"           WHERE stat.load_profile.fk_time_id = stat.time.id " +\
						"           AND stat.load_profile.nuts_id IN ("+str(nutsListQuery)+") " +\
						"           AND stat.time.year = " + str(year) + ") as t " +\
						"GROUP BY t.hoy, t.nuts, t.val " +\
						"ORDER BY t.nuts;"'''
  
		sql_query = "select stat.load_profile.value as val, stat.load_profile.nuts_id as nutsid, stat.time.hour_of_year as hod " +\
						"from stat.load_profile inner join stat.time on stat.load_profile.fk_time_id = stat.time.id " +\
						"WHERE stat.load_profile.nuts_id IN ("+str(nutsListQuery)+") AND stat.time.year = " + str(year) + " " +\
						"order by nutsid, hour_of_year;"


		# Execution of the query
		query = db.session.execute(sql_query)
		
		# Store query results in list
		for q in query:
			listAllValues.append(q)
			listOfNuts.append(q[1])
		
		# Get unique nuts values and store them back into a list
		listOfNuts = set(listOfNuts)
		listOfNuts = list(listOfNuts)

		# Get number of nuts
		nbNuts = len(listOfNuts)

		# Store values in dictionary by nuts
		for n in range(nbNuts):
			val = []
			hours = []

			for v in listAllValues:
				if v[1] == listOfNuts[n]:
					val.append(v[0])
					hours.append(v[2])
			
			valuesByNuts[listOfNuts[n]] = {}
			valuesByNuts[listOfNuts[n]]['val'] = []
			valuesByNuts[listOfNuts[n]]['val'] = val
			valuesByNuts[listOfNuts[n]]['hours'] = []
			valuesByNuts[listOfNuts[n]]['hours'] = hours

			# Remove nuts from dictionary if less than 4000 values
			if len(valuesByNuts[listOfNuts[n]]['hours']) < settings.LIMIT_VALUES_PER_NUTS:
				del valuesByNuts[listOfNuts[n]]

		# Check if modulo is not 0 
		if len(listAllValues)%settings.HOURS_PER_YEAR != 0 and nbNuts > 1:
			# Check which value is missing
			hourToDelete = []
			for n in range(nbNuts):
				for hour in range(settings.HOURS_PER_YEAR):
					if hour+1 not in valuesByNuts[listOfNuts[n]]['hours']:
						hourToDelete.append(hour) # Store index of hour(line) to delete
			
			# Delete same line for each nuts
			for h in hourToDelete:
				for n in range(nbNuts):
					if h in valuesByNuts[listOfNuts[n]]['hours']:
						valuesByNuts[listOfNuts[n]]['hours'].pop(h)
						valuesByNuts[listOfNuts[n]]['val'].pop(h)


		# Get number of values for each nuts
		numberOfValues = len(valuesByNuts[listOfNuts[0]]['val'])

		# Check if more than one nuts		
		if nbNuts > 1:
			# Calculate the sum of each hour of nuts
			for c in range(numberOfValues):
				val = 0
				for n in range(nbNuts):
					val += valuesByNuts[listOfNuts[n]]['val'][c]
				valuesToSample.append(val)
		else:
			valuesToSample = valuesByNuts[listOfNuts[0]]['val']


		# Sort the values list in descending order
		valuesToSample = sorted(valuesToSample, reverse=True)

		# Create the points for the curve with the X and Y axis
		listPoints = []
		for n, l in enumerate(valuesToSample):
			listPoints.append({
				'X':n+1,
				'Y':valuesToSample[n]
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

		for c, l in enumerate(finalListPoints):
			print(finalListPoints[c])

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