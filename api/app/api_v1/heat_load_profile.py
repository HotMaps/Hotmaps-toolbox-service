from app import celery
import logging
from flask_restplus import Resource
from app.decorators.serializers import  load_profile_aggregation_day_input, \
    load_profile_aggregation_curve_output, load_profile_aggregation_curve, load_profile_aggregation_hectares, \
    load_profile_aggregation_curve_hectares
from app.decorators.restplus import api
from app.decorators.exceptions import IntersectionException, HugeRequestException, ParameterException
from app.models.heatloadQueries import HeatLoadProfile



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
@api.response(500, 'Missing parameter.')
class HeatLoadProfileAggregation(HeatLoadProfileResource):
    @api.marshal_with(load_profile_aggregation_curve_output)
    @api.expect(load_profile_aggregation_curve)
    def post(self):
        """
        Returns the statistics for specific layers, area and year
        :return:
        """
        # Entries

        wrong_parameter = [];
        try:
            year = api.payload['year']
        except:
            wrong_parameter.append('year')
        try:
            nuts = api.payload['nuts']
        except:
            wrong_parameter.append('nuts')
        # raise exception if parameters are false
        if len(wrong_parameter) > 0:
            exception_message = ''
            for i in range(len(wrong_parameter)):
                exception_message += wrong_parameter[i]
                if (i != len(wrong_parameter) - 1):
                    exception_message += ', '
            raise ParameterException(exception_message + '')

        # Stop execution if nuts list is empty 
        if not nuts:
            return

        nuts = generalData.transform_nuts_list(nuts)

        output = {}

        output = HeatLoadProfile.duration_curve_nuts_lau(year=year, nuts=nuts)
        result = {
            "points": output
        }

        return result

@celery.task(name = 'duration_curve_nuts_lau')
def durationCurveNutsLau(year, nuts):
    if not nuts and year:
        return
    output = HeatLoadProfile.duration_curve_nuts_lau(year=year, nuts=nuts)
    print ("duration_curve_nuts_lau task ",output)

    return output


@ns.route('/duration-curve/hectares')
@api.response(404, 'No data found')
@api.response(500, 'Missing parameter.')
@api.response(502, 'SQL Error.')
class HeatLoadProfileAggregation(HeatLoadProfileResource):
    @api.marshal_with(load_profile_aggregation_curve_output)
    @api.expect(load_profile_aggregation_curve_hectares)
    def post(self):
        """
        Returns the statistics for specific layers, area and year
        :return:
        """
        #Entries
        wrong_parameter = [];
        try:
            year = api.payload['year']
        except:
            wrong_parameter.append('year')
        try:
            areas = api.payload['areas']
            for test_area in areas:
                try:
                    for test_point in test_area['points']:
                        try:
                            test_lng = test_point['lng']
                        except:
                            wrong_parameter.append('lng')
                        try:
                            test_lat = test_point['lat']
                        except:
                            wrong_parameter.append('lat')
                except:
                    wrong_parameter.append('points')
        except:
            wrong_parameter.append('areas')
        #raise exception if parameters are false
        if len(wrong_parameter) > 0:
            exception_message = ''
            for i in range(len(wrong_parameter)):
                exception_message += wrong_parameter[i]
                if (i != len(wrong_parameter) - 1):
                    exception_message += ', '
            raise ParameterException(exception_message + '')

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
        try:
            output = HeatLoadProfile.duration_curve_hectares(year=year, geometry=geom)
        except:

            raise IntersectionException()
        result = {
            "points": output
        }
        return result

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
@api.response(0, 'Request too big')
@api.response(404, 'No data found')
@api.response(500, 'Missing parameter.')
@api.response(502, 'SQL Error.')
class HeatLoadProfileAggregationHectares(HeatLoadProfileResource):
    #@api.marshal_with(load_profile_aggregation_hectares_output)
    @api.expect(load_profile_aggregation_hectares)
    def post(self):
        """
        Returns the heat load data by hectare
        :return:
        """

        # Entrees
        wrong_parameter = [];
        try:
            year = api.payload['year']
        except:
            wrong_parameter.append('year')
        try:
            areas = api.payload['areas']
            for test_area in areas:
                try:
                    for test_point in test_area['points']:
                        try:
                            test_lng = test_point['lng']
                        except:
                            wrong_parameter.append('lng')
                        try:
                            test_lat = test_point['lat']
                        except:
                            wrong_parameter.append('lat')
                except:
                    wrong_parameter.append('points')
        except:
            wrong_parameter.append('areas')
        # raise exception if parameters are false
        if len(wrong_parameter) > 0:
            exception_message = ''
            for i in range(len(wrong_parameter)):
                exception_message += wrong_parameter[i]
                if (i != len(wrong_parameter) - 1):
                    exception_message += ', '
            raise ParameterException(exception_message + '')

        # Stop execution if areas list is empty
        if not areas:
            return
        # TODO no error management on month & day entry
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
        try:
            res = HeatLoadProfile.heatloadprofile_hectares(year=year, month=month, day=day, geometry=geom)
        except:
            print('IntersectionException')
            raise IntersectionException()
        return res





@ns.route('/nuts-lau')
@api.response(404, 'No data found')
@api.response(500, 'Missing parameter.')
class HeatLoadProfileAggregationNuts(HeatLoadProfileResource):
    #@api.marshal_with(load_profile_aggregation_hectares_output)
    @api.expect(load_profile_aggregation_day_input) #TODO Nuts level asked but not used in the app
    def post(self):
        """
        Returns the heat load data by nuts or lau
        :return:
        """

        # Entrees
        wrong_parameter = [];
        try:
            year = api.payload['year']
        except:
            wrong_parameter.append('year')
        try:
            nuts = api.payload['nuts']
        except:
            wrong_parameter.append('nuts')
        # raise exception if parameters are false
        if len(wrong_parameter) > 0:
            exception_message = ''
            for i in range(len(wrong_parameter)):
                exception_message += wrong_parameter[i]
                if (i != len(wrong_parameter) - 1):
                    exception_message += ', '
            raise ParameterException(exception_message + '')
        # Stop execution if nuts list is empty 
        if not nuts:
            return
            
        nuts = generalData.transform_nuts_list(nuts)
        
        if 'month' in api.payload.keys():
          month = api.payload["month"]
        else:
          month = 0

        if 'day' in api.payload.keys():
          day = api.payload["day"]
        else:
          day = 0

        output = {}

        res = HeatLoadProfile.heatloadprofile_nuts_lau(nuts=nuts, year=year, month=month, day=day)

        output = res

        return output