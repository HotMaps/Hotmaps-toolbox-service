import logging
import re
from flask import request
from flask_restplus import Resource
from main_api.api.main.serializers import load_profile_aggregation_month, load_profile_aggregation_input, \
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


@ns.route('/aggregate/month')
@api.response(404, 'No data found')
class HeatLoadProfileAggregationMonth(Resource):
    @api.marshal_with(load_profile_aggregation_month)
    @api.expect(load_profile_aggregation_input)
    def post(self):
        """
        Returns the statistics for specific layers, point and year
        :return:
        """
        year = api.payload['year']
        nuts_id = api.payload['nuts_id']
        nuts_level = api.payload['nuts_level']

        output = HeatLoadProfileNuts.aggregate_for_month(nuts_id=nuts_id, year=year)

        return {
            'values': output
        }

@ns.route('/aggregate/hour')
@api.response(404, 'No data found')
class HeatLoadProfileAggregationMonth(Resource):
    @api.marshal_with(load_profile_aggregation_hour)
    @api.expect(load_profile_aggregation_hour_input)
    def post(self):
        """
        Returns the statistics for specific layers, point and year
        :return:
        """
        year = api.payload['year']
        month = api.payload['month']
        nuts_id = api.payload['nuts_id']
        nuts_level = api.payload['nuts_level']

        output = HeatLoadProfileNuts.aggregate_for_hour(nuts_id=nuts_id, year=year, month=month)

        return {
            'values': output
        }

