import logging

from flask_restplus import Resource
from main_api.api.main.serializers import grid_feature_collection, area
from main_api.api.restplus import api
from main_api.models.grids import Grid1Km
from sqlalchemy import func, BigInteger, TypeDecorator
from main_api.models import db
import datetime
import shapely.geometry as shapely_geom
from geoalchemy2.shape import to_shape
from shapely.wkb import loads
from geojson import FeatureCollection, Feature, dumps

log = logging.getLogger(__name__)

ns = api.namespace('grids', description='Grids')


class CoerceToInt(TypeDecorator):
    impl = BigInteger

    def process_result_value(selfself, value, dialect):
        if value is not None:
            value = int(value)
        return value


@ns.route('/1km/area/')
@api.response(404, 'Grid not found for that specific area.')
class Grid1KmFromArea(Resource):

    @api.marshal_with(grid_feature_collection)
    @api.expect(area)
    def post(self):
        """
        Returns the total density for specific area and year
        :return:
        """
        points = api.payload['points']
        poly = shapely_geom.Polygon([[p['lng'], p['lat']] for p in points])
        geom = "SRID=4326;{}".format(poly.wkt)
        #grid = db.session.query(Grid1Km)#. \
            #filter(func.ST_Within(Grid1Km.geom, func.ST_Transform(func.ST_GeomFromEWKT(geom), 4258))).all()

        grid = db.session.query(Grid1Km). \
            filter(func.ST_Within(Grid1Km.geom, func.ST_Transform(func.ST_GeomFromEWKT(geom), 3035))).all()

        features = []
        for row in grid:
            geometry = to_shape(row.geom)
            feature = Feature(
                id=row.gid,
                geometry = geometry,
                properties={
                    'xmin': float(row.xmin),
                    'xmax': float(row.xmax),
                    'ymin': float(row.ymin),
                    'ymax': float(row.ymax)
                }
            )
            features.append(feature)

        return FeatureCollection(features)
