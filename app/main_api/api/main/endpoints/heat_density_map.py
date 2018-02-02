import logging

import datetime
from flask_restplus import Resource
from main_api.api.main.serializers import raster_for_area_input
from main_api.api.restplus import api
from main_api.models.heat_density_map import HeatDensityMap
from sqlalchemy import func, BigInteger, TypeDecorator
from main_api.models import db
import shapely.geometry as shapely_geom
from geoalchemy2.shape import to_shape
from geojson import FeatureCollection, Feature
from main_api.api.main.serializers import stats_layers_area_input, stats_layers_output, stats_layers_nuts_input, stats_layers_nuts_output, stats_layer_point_input, stats_layers_area_nuts_input,points_geometry
from main_api.models.heat_density_map import HeatDensityHa
import sys
import json
log = logging.getLogger(__name__)

ns = api.namespace('raster', description='raster request')


class CoerceToInt(TypeDecorator):
    impl = BigInteger

    def process_result_value(selfself, value, dialect):
        if value is not None:
            value = int(value)
        return value


#@ns.route('/100m/area/')
@api.response(404, 'Heat density not found for that specific area.')
class Grid1KmFromArea(Resource):

    #@api.marshal_with(grid_feature_collection)
    @api.expect(raster_for_area_input)
    def post(self):
        """
        Returns the heat density map for specific area and year
        :return:
        """
        points = api.payload['points']
        year = api.payload['year']
        poly = shapely_geom.Polygon([[p['lng'], p['lat']] for p in points])
        geom = "SRID=4326;{}".format(poly.wkt)

        query = db.session.query(func.ST_Union(HeatDensityMap.rast)). \
            filter(HeatDensityMap.date == datetime.datetime.strptime(str(year), '%Y')). \
            filter(func.ST_Intersects(HeatDensityMap.rast, func.ST_Transform(func.ST_GeomFromEWKT(geom), HeatDensityMap.CRS))).all()


        return query


@ns.route('/layers/area/centroids')

@api.response(404, 'No data found for that specific hectare.')

class CentroidsLayersInArea(Resource):
    @api.expect(stats_layers_nuts_input)
    def post(self):
        """
        Returns the centroid of the hectares selected
        :return:
        """
        geometry = api.payload['centroids']



        result = HeatDensityHa.centroid_for_selection(geometry)
        response = []
        for x in result:
            response.append(   json.loads(x['geojson']))

        print >> sys.stderr, response

        # output
        return {
            "centroids": response,
        }

@ns.route('/layers/hectare/centroid')

@api.response(404, 'No data found for that specific hectare.')

class CentroidLayersInHectare(Resource):
    @api.expect(stats_layers_nuts_input)
    def post(self):
        """
        Returns the centroid of the hectares selected
        :return:
        """
        point = api.payload['point']
        print >> sys.stderr, point
        result = HeatDensityHa.centroid_for_hectare(point)
        response = []
        for x in result:
            response.append(   json.loads(x['geojson']))

        print >> sys.stderr, response

        # output
        return {
            "point": response,
        }




