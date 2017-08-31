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
@ns.deprecated
@api.response(404, 'Grid not found for that specific area.')
class Grid1KmFromArea(Resource):

    @api.marshal_with(grid_feature_collection)
    @api.expect(area)
    def post(self):
        """
        Returns the reference grid for 1kmx1km
        This method has been deprecated and will be removed in the next release
        :return:
        """
        points = api.payload['points']
        poly = shapely_geom.Polygon([[p['lng'], p['lat']] for p in points])
        geom = "SRID=4326;{}".format(poly.wkt)

        grid = db.session.query(Grid1Km). \
            filter(func.ST_Within(Grid1Km.geom, func.ST_Transform(func.ST_GeomFromEWKT(geom), Grid1Km.CRS))).all()

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

        crs = {
            "type": "name",
            "properties": {
                "name": "EPSG:%d" % Grid1Km.CRS
            }
        }

        return FeatureCollection(features, crs=crs)
