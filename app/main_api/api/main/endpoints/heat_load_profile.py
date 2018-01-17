import logging
import re
from flask import request
from flask_restplus import Resource
from main_api.api.main.serializers import load_profile_aggregation_month, load_profile_aggregation_month_input, \
    load_profile_aggregation_hour, load_profile_aggregation_hour_input
from main_api.api.restplus import api
from main_api.models.nuts import Nuts
from main_api.models.heat_load_profile import HeatLoadProfileNuts
from sqlalchemy import func, BigInteger, TypeDecorator
from main_api.models import db
import datetime
import shapely.geometry as shapely_geom
from geojson import FeatureCollection, Feature
from geoalchemy2.shape import to_shape


log = logging.getLogger(__name__)

ns = api.namespace('load-profile', description='Operations related to heat load profile')


class HeatLoadProfileResource(Resource):
    def normalize_nuts(self, nuts):
        list_nuts_id = []
        for nuts_id in nuts:
            nuts_id = nuts_id[:4]
            if nuts_id not in list_nuts_id:
                list_nuts_id.append(nuts_id)
        return list_nuts_id

@ns.route('/aggregate/month')
@api.response(404, 'No data found')
class HeatLoadProfileAggregationMonth(HeatLoadProfileResource):
    @api.marshal_with(load_profile_aggregation_month)
    @api.expect(load_profile_aggregation_month_input)
    def post(self):
        """
        Returns the statistics for specific layers, point and year
        :return:
        """
        year = api.payload['year']
        nuts = api.payload['nuts']
        try:
            nuts_level = int(api.payload['nuts_level'])
        except ValueError:
            nuts_level = 2

        output = {}
        if nuts_level >= 2:
            output = HeatLoadProfileNuts.aggregate_for_month(nuts=self.normalize_nuts(nuts), year=2010)

        return output

@ns.route('/aggregate/hour')
@api.response(404, 'No data found')
class HeatLoadProfileAggregationHour(HeatLoadProfileResource):
    @api.marshal_with(load_profile_aggregation_hour)
    @api.expect(load_profile_aggregation_hour_input)
    def post(self):
        """
        Returns the statistics for specific layers, point and year
        :return:
        """
        year = api.payload['year']
        month = api.payload['month']
        nuts = api.payload['nuts']
        try:
            nuts_level = int(api.payload['nuts_level'])
        except ValueError:
            nuts_level = 2

        output = {}
        if nuts_level >= 2:
            output = HeatLoadProfileNuts.aggregate_for_hour(nuts=self.normalize_nuts(nuts), year=2010, month=month)

        return output


