from app import celery
import logging
from flask_restplus import Resource
from app.decorators.serializers import  load_profile_aggregation_day_input, \
    load_profile_aggregation_curve_output, load_profile_aggregation_curve, load_profile_aggregation_hectares, \
    load_profile_aggregation_curve_hectares
from app.decorators.restplus import api

from app.models.heatloadQueries import HeatLoadProfile
from .. import helper



import shapely.geometry as shapely_geom

from app.models import generalData


log = logging.getLogger(__name__)

load_profile_namespace = api.namespace('heat-load-profile', description='Operations related to heat load profile')

ns = load_profile_namespace
class HeatLoadProfileResource(Resource):
    def normalize_nuts(self, nuts):
        list_nuts_id = []
        for nuts_id in nuts:
            nuts_id = nuts_id[:4]
            if nuts_id not in list_nuts_id:
                list_nuts_id.append(nuts_id)
        return list_nuts_id



@ns.route('/duration-curve/nuts-lau')
@api.response(404, 'No data found')
class HeatLoadProfileAggregation(HeatLoadProfileResource):
    @api.marshal_with(load_profile_aggregation_curve_output)
    @api.expect(load_profile_aggregation_curve)
    def post(self):
        """
        Returns the statistics for specific layers, area and year
        :return:
        """
        year = api.payload['year']
        nuts = api.payload['nuts']

        # Stop execution if nuts list is empty 
        if not nuts:
            return

        nuts = helper.transform_nuts_list(nuts)

        output = {}

        output = HeatLoadProfile.duration_curve_nuts_lau(year=year, nuts=nuts)

        return {
            "points": output
        }

@celery.task(name = 'duration_curve_nuts_lau')
def durationCurveNutsLau(year, nuts):
    if not nuts and year:
        return
    output = HeatLoadProfile.duration_curve_nuts_lau(year=year, nuts=nuts)

    return output


@ns.route('/duration-curve/hectares')
@api.response(404, 'No data found')
class HeatLoadProfileAggregation(HeatLoadProfileResource):
    @api.marshal_with(load_profile_aggregation_curve_output)
    @api.expect(load_profile_aggregation_curve_hectares)
    def post(self):
        """
        Returns the statistics for specific layers, area and year
        :return:
        """
        year = api.payload['year']
        areas = api.payload['areas']

        # Stop execution if areas list is empty 

        polyArray = []
        output = {}
        # TODO: this part must be one methods same in /aggregate/hectares Rules 1 NO DUPLICATE
        # convert to polygon format for each polygon and store them in polyArray
        for polygon in areas:
            po = shapely_geom.Polygon([[p['lng'], p['lat']] for p in polygon['points']])
            polyArray.append(po)


        # convert array of polygon into multipolygon
        multipolygon = shapely_geom.MultiPolygon(polyArray)

        #geom = "SRID=4326;{}".format(multipolygon.wkt)
        geom = multipolygon.wkt

        output = HeatLoadProfile.duration_curve_hectares(year=year, geometry=geom)
        return {
            "points": output
        }
@celery.task(name = 'duration_curve_hectare')
def durationCurveHectare(areas,year):
    if not areas:
        return

    polyArray = []
    output = {}
    # TODO: this part must be one methods same in /aggregate/hectares Rules 1 NO DUPLICATE
    # convert to polygon format for each polygon and store them in polyArray
    for polygon in areas:
        po = shapely_geom.Polygon([[p['lng'], p['lat']] for p in polygon['points']])
        polyArray.append(po)


    # convert array of polygon into multipolygon
    multipolygon = shapely_geom.MultiPolygon(polyArray)

    #geom = "SRID=4326;{}".format(multipolygon.wkt)
    geom = multipolygon.wkt

    output = HeatLoadProfile.duration_curve_hectares(year=year, geometry=geom)

    return output

@ns.route('/hectares')
@api.response(404, 'No data found')
class HeatLoadProfileAggregationHectares(HeatLoadProfileResource):
    #@api.marshal_with(load_profile_aggregation_hectares_output)
    @api.expect(load_profile_aggregation_hectares)
    def post(self):
        """
        Returns the heat load data by hectare
        :return:
        """

        # Entrees
        year = api.payload['year']
        areas = api.payload['areas']

        # Stop execution if areas list is empty
        if not areas:
            return

        if 'month' in api.payload.keys():
            month = api.payload["month"]
        else:
            month = 0

        if 'day' in api.payload.keys():
            day = api.payload["day"]
        else:
            day = 0


        polyArray = []
        output = {}
        # TODO: this part must be one methods same in /aggregate/duration_curve/hectares Rules 1 NO DUPLICATE
        # convert to polygon format for each polygon and store them in polyArray
        for polygon in areas:
            po = shapely_geom.Polygon([[p['lng'], p['lat']] for p in polygon['points']])
            polyArray.append(po)


        # convert array of polygon into multipolygon
        multipolygon = shapely_geom.MultiPolygon(polyArray)

        #geom = "SRID=4326;{}".format(multipolygon.wkt)
        geom = multipolygon.wkt

        res = HeatLoadProfile.heatloadprofile_hectares.delay(year=year, month=month, day=day, geometry=geom)

        return res.get()





@ns.route('/nuts-lau')
@api.response(404, 'No data found')
class HeatLoadProfileAggregationNuts(HeatLoadProfileResource):
    #@api.marshal_with(load_profile_aggregation_hectares_output)
    @api.expect(load_profile_aggregation_day_input)
    def post(self):
        """
        Returns the heat load data by nuts or lau
        :return:
        """

        # Entrees
        year = api.payload['year']
        nuts = api.payload['nuts']

        # Stop execution if nuts list is empty 
        if not nuts:
            return
            
        nuts = helper.transform_nuts_list(nuts)
        
        if 'month' in api.payload.keys():
          month = api.payload["month"]
        else:
          month = 0

        if 'day' in api.payload.keys():
          day = api.payload["day"]
        else:
          day = 0

        output = {}

        res = HeatLoadProfile.heatloadprofile_nuts_lau.delay(nuts=nuts, year=year, month=month, day=day)

        output = res.get()

        return output