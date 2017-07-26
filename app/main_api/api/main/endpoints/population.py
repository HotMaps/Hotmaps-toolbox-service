import logging

from flask import request
from flask_restplus import Resource
from main_api.api.main.serializers import population_density, total_density_for_nuts_area, \
    total_density_for_nuts_area_input
from main_api.api.restplus import api
from main_api.models.population_density import PopulationDensity
from main_api.models.nuts import Nuts
from sqlalchemy import func, BigInteger, TypeDecorator
from main_api.models import db
import datetime
import shapely.geometry as shapely_geom

log = logging.getLogger(__name__)

ns = api.namespace('population', description='Operations related to population')


class CoerceToInt(TypeDecorator):
    impl = BigInteger

    def process_result_value(selfself, value, dialect):
        if value is not None:
            value = int(value)
        return value


@ns.route('/density/nuts/<string:nuts_id>')
@api.response(404, 'Density not found for that specific nuts id.')
class PopulationDensityByNuts(Resource):

    @api.marshal_with(population_density)
    def get(self, nuts_id):
        """
        Returns a population density for specific nuts
        :param nuts_id:
        :return:
        """
        return PopulationDensity.query.filter_by(nuts_id=nuts_id).all()


@ns.route('/density/area/<string:geometry>/<int:nuts_level>/<int:year>')
@api.response(404, 'Density not found for that specific area.')
class PopDensityInArea(Resource):

    @api.marshal_with(total_density_for_nuts_area)
    def get(self, geometry, nuts_level, year):
        """
        Returns the total density for specific area and year
        :param geometry:
        :param nuts_level:
        :param year:
        :return:
        """
        density = db.session.query(func.sum(PopulationDensity.value, type_=CoerceToInt), \
                                   func.ST_AsGeoJSON(func.ST_Collect(Nuts.geom))).\
            join(Nuts, PopulationDensity.nuts).\
            filter(PopulationDensity.date == datetime.datetime.strptime(str(year), '%Y')).\
            filter(Nuts.stat_levl_ == nuts_level).\
            filter(func.ST_Within(Nuts.geom, func.ST_GeomFromEWKT(geometry))).first()
        output = {
            'sum_density': density[0],
            'geometries': density[1]
        }
        return output


@ns.route('/density/area/')
@api.response(404, 'Density not found for that specific area.')
class PopDensityInArea(Resource):

    @api.marshal_with(total_density_for_nuts_area)
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
        density = db.session.query(func.sum(PopulationDensity.value, type_=CoerceToInt), \
                                   func.ST_AsGeoJSON(func.ST_Collect(Nuts.geom))). \
            join(Nuts, PopulationDensity.nuts). \
            filter(PopulationDensity.date == datetime.datetime.strptime(str(year), '%Y')). \
            filter(Nuts.stat_levl_ == nuts_level). \
            filter(func.ST_Within(Nuts.geom, func.ST_Transform(func.ST_GeomFromEWKT(geom), 4258))).first()

        """featureCollection = {
            'features': [{
                'properties': {
                    'density': density[0],
                    'year': year,
                    'nuts_level': nuts_level
                },
                'geometry': density[1]
            }]
        }"""

        output = {
            'year': year,
            'nuts_level': nuts_level,
            'sum_density': density[0],
            'geometries': density[1]
        }
        return output
