import logging

from flask import request
from flask_restplus import Resource
from main_api.api.main.serializers import stats_layers_area_input, stats_layers_area
from main_api.api.restplus import api
from main_api.models.wwtp import Wwtp
from main_api.models.heat_density_map import HeatDensityMap
from main_api.models.population_density import PopulationDensity
from sqlalchemy import func, BigInteger, TypeDecorator
from main_api.models import db
import datetime
import shapely.geometry as shapely_geom
from geojson import FeatureCollection, Feature
from geoalchemy2.shape import to_shape



log = logging.getLogger(__name__)

ns = api.namespace('stats', description='Operations related to statistics')


layers_ref = {
    'wwtp': Wwtp,
    'population': PopulationDensity,
    'heat_density_map': HeatDensityMap
}

@ns.route('/layers/area/')
@api.response(404, 'Density not found for that specific area.')
class StatsLayersInArea(Resource):

    @api.marshal_with(stats_layers_area)
    @api.expect(stats_layers_area_input)
    def post(self):
        """
        Returns the total density for specific area and year
        :return:
        """
        year = api.payload['year']
        layers = api.payload['layers']
        points = api.payload['points']
        poly = shapely_geom.Polygon([[p['lng'], p['lat']] for p in points])
        geom = "SRID=4326;{}".format(poly.wkt)

        output = []

        for layer in layers:
            a = layers_ref[layer]()
            output.append({
                'name': layer,
                'values': a.aggregate_for_selection(geometry=geom, year=year)
            })


        return {"layers": output}

