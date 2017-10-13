import logging

from flask import request
from flask_restplus import Resource
from main_api.api.main.serializers import stats_layers_area_input, stats_layers_area
from main_api.api.restplus import api
from main_api.models.wwtp import Wwtp
from main_api.models.heat_density_map import HeatDensityMap, HeatDensityHa
from main_api.models.population_density import PopulationDensity, PopulationDensityHa
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
    'population_density_ha': PopulationDensityHa,
    'heat_density_map': HeatDensityMap,
    'heat_density_ha': HeatDensityHa
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

        # for each layer,
        # try to match layer name with layer class
        # run aggregate_for_selection method
        for layer in layers:
            try:
                a = layers_ref[layer]()
            except KeyError:
                continue

            output.append({
                'name': layer,
                'values': a.aggregate_for_selection(geometry=geom, year=year)
            })

        pop1ha_name = 'pop_tot_curr_density'
        hdm_name = 'heat_density_map'
        if pop1ha_name in layers and hdm_name in layers:
            hdm = None
            heat_cons = None
            population = None

            for l in output:
                if l.get('name') == hdm_name:
                    hdm = l
                    for v in l.get('values', []):
                        if v.get('name') == 'heat_consumption':
                            heat_cons = v
                if l.get('name') == pop1ha_name:
                    for v in l.get('values', []):
                        if v.get('name') == 'population_density_sum':
                            population = v

            v = {
                'name': 'consumption_per_citizen',
                'value': heat_cons.get('value', 0) / population.get('value', 1),
                'unit': heat_cons.get('unit') + '/' + population.get('unit')
            }

            hdm.get('values').append(v)

        return {"layers": output}

