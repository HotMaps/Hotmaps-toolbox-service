import logging

from flask import request
from flask_restplus import Resource
from main_api.api.main.serializers import population_density, total_density_for_nuts_area, \
    total_density_for_nuts_area_input
from main_api.api.restplus import api
from main_api.models.population_density import PopulationDensityNuts
from main_api.models.nuts import Nuts
from sqlalchemy import func, BigInteger, TypeDecorator
from main_api.models import db
import datetime
import shapely.geometry as shapely_geom
from geojson import FeatureCollection, Feature
from geoalchemy2.shape import to_shape



log = logging.getLogger(__name__)

ns = api.namespace('population', description='Operations related to population')


class CoerceToInt(TypeDecorator):
    impl = BigInteger

    def process_result_value(selfself, value, dialect):
        if value is not None:
            value = int(value)
        return value


@ns.route('/density/nuts/area/')
@api.response(404, 'Density not found for that specific area.')
class PopDensityNutsInArea(Resource):

    #@api.marshal_with(total_density_for_nuts_area)
    @api.expect(total_density_for_nuts_area_input)
    def post(self):
        """
        Returns the total density for specific area and year
        :return:
        """
        year = api.payload['year']
        nuts_level = api.payload['nuts_level']
        points = api.payload['points']
        poly = shapely_geom.Polygon([[p['lng'], p['lat']] for p in points])
        geom = "SRID=4326;{}".format(poly.wkt)
        query = db.session.query(PopulationDensityNuts, \
                                 func.ST_Area(func.ST_Transform(Nuts.geom, 3035))). \
            join(Nuts, PopulationDensityNuts.nuts). \
            filter(PopulationDensityNuts.date == datetime.datetime.strptime(str(year), '%Y')). \
            filter(Nuts.stat_levl_ == nuts_level). \
            filter(func.ST_Within(Nuts.geom, func.ST_Transform(func.ST_GeomFromEWKT(geom), PopulationDensityNuts.CRS))).all()

        output = {
            'year': year,
            'nuts_level': nuts_level,
            'sum_density': query[0],
            'geometries': query[1]
        }
        area = 0.0
        density = 0
        features = []
        for row in query:
            pop_dens = row[0]
            nuts = pop_dens.nuts

            # sum area + density
            density += pop_dens.value
            area += row[1]

            # create feature
            geometry = to_shape(nuts.geom)
            feature = Feature(
                id=nuts.gid,
                geometry=geometry,
                properties={
                    'density': float(pop_dens.value),
                }
            )
            features.append(feature)

        properties = {
            'year': year,
            'nuts_level': nuts_level,
            'sum_density': density,
            'area': area
        }

        crs = {
            "type": "name",
            "properties": {
                "name": "EPSG:%d" % Nuts.CRS
            }
        }

        return FeatureCollection(features, properties=properties, crs=crs)

