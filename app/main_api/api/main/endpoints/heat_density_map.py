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

log = logging.getLogger(__name__)

ns = api.namespace('heat-density-map', description='Heat density map')


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

