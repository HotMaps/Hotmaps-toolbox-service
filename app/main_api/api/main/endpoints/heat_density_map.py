import logging
from main_api.api.main.serializers import number_of_centroid_area_output, stats_layers_nuts_input
import datetime
from flask_restplus import Resource
from main_api.api.main.serializers import raster_for_area_input,centroid_from_polygon_input
from main_api.api.restplus import api
from main_api.models.heat_density_map import HeatDensityMap,HeatDensityHa
from sqlalchemy import func, BigInteger, TypeDecorator
from main_api.models import db
import shapely.geometry as shapely_geom
from geoalchemy2.shape import to_shape
from geojson import FeatureCollection, Feature
import json, sys


log = logging.getLogger(__name__)

ns = api.namespace('raster', description='Heat density map')


class CoerceToInt(TypeDecorator):
    impl = BigInteger

    def process_result_value(selfself, value, dialect):
        if value is not None:
            value = int(value)
        return value


