import logging
import re
from flask import request
from flask_restplus import Resource
from main_api.api.main.serializers import stats_layers_area_input, stats_layers_output, stats_layer_point_input, stats_layers_area_nuts_input
from main_api.api.restplus import api
from main_api.models.wwtp import Wwtp
from main_api.models.heat_density_map import HeatDensityMap, HeatDensityHa, HeatDensityNuts3
from main_api.models.population_density import PopulationDensityHa, PopulationDensityNuts3
from main_api.models.nuts import Nuts, NutsRG01M
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
    'population': PopulationDensityNuts3,
    'population_density_nuts3': PopulationDensityNuts3,
    'population_density_ha': PopulationDensityHa,
    'heat_density_map': HeatDensityMap,
    'heat_density_ha': HeatDensityHa,
    'heat_density_nuts3': HeatDensityNuts3
}

@ns.route('/layer/point')
@api.response(404, 'No data found for that specific point')
class StatsLayersInArea(Resource):
    @api.marshal_with(stats_layers_output)
    @api.expect(stats_layer_point_input)
    def post(self):
        """
        Returns the statistics for specific layers, point and year
        :return:
        """
        year = api.payload['year']
        layers = api.payload['layers']
        point = api.payload['point']
        poly = shapely_geom.Point(point['lng'], point['lat'])
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

        # compute heat consumption/person if both layers are selected
        pop_nuts_name = 'population_density_nuts3'
        heat_nuts_name = 'heat_density_nuts3'
        if pop_nuts_name in layers and heat_nuts_name in layers:
            hdm = None
            heat_cons = None
            population = None

            for l in output:
                if l.get('name') == heat_nuts_name:
                    hdm = l
                    for v in l.get('values', []):
                        if v.get('name') == 'heat_consumption':
                            heat_cons = v
                if l.get('name') == pop_nuts_name:
                    for v in l.get('values', []):
                        if v.get('name') == 'population':
                            population = v

            if heat_cons != None and population != None:
                pop_val = float(population.get('value', 1))
                pop_val = pop_val if pop_val > 0 else 1
                hea_val = float(heat_cons.get('value', 0))

                v = {
                    'name': 'consumption_per_citizen',
                    'value': hea_val / pop_val,
                    'unit': heat_cons.get('unit') + '/' + population.get('unit')
                }

                hdm.get('values').append(v)

        # compute heat consumption/person if both layers are selected
        pop1ha_name = 'population_density_ha'
        hdm_name = 'heat_density_ha'
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
                        if v.get('name') == 'population':
                            population = v

            if heat_cons != None and population != None:
                pop_val = float(population.get('value', 1))
                pop_val = pop_val if pop_val > 0 else 1
                hea_val = float(heat_cons.get('value', 0))

                v = {
                    'name': 'consumption_per_citizen',
                    'value': hea_val / pop_val,
                    'unit': heat_cons.get('unit') + '/' + population.get('unit')
                }

                hdm.get('values').append(v)

        nuts = None
        r = re.compile("^.*_nuts[0-3]$")
        nuts_layers = list(filter(r.match, layers))
        if nuts_layers != None and hasattr(nuts_layers, '__len__') and len(nuts_layers) > 0:
            nuts_levels = []
            for l in nuts_layers:
                try:
                    nuts_levels.append(int(re.search("^.*nuts([0-3])$", l).group(1)))
                except (AttributeError, ValueError):
                    pass

            nuts = NutsRG01M.nuts_in_geometry(geometry=geom, year=year, nuts_level=max(nuts_levels))

        return {
            "layers": output,
            "feature_collection": nuts
        }


@ns.route('/layers/area/')
@api.response(404, 'No data found for that specific area.')
class StatsLayersInArea(Resource):

    @api.marshal_with(stats_layers_output)
    @api.expect(stats_layers_area_input)
    def post(self):
        """
        Returns the statistics for specific layers, area and year
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

        # compute heat consumption/person if both layers are selected
        pop_nuts_name = 'population_density_nuts3'
        heat_nuts_name = 'heat_density_nuts3'
        if pop_nuts_name in layers and heat_nuts_name in layers:
            hdm = None
            heat_cons = None
            population = None

            for l in output:
                if l.get('name') == heat_nuts_name:
                    hdm = l
                    for v in l.get('values', []):
                        if v.get('name') == 'heat_consumption':
                            heat_cons = v
                if l.get('name') == pop_nuts_name:
                    for v in l.get('values', []):
                        if v.get('name') == 'population':
                            population = v

            if heat_cons != None and population != None:
                pop_val = float(population.get('value', 1))
                pop_val = pop_val if pop_val > 0 else 1
                hea_val = float(heat_cons.get('value', 0))

                v = {
                    'name': 'consumption_per_citizen',
                    'value': hea_val / pop_val,
                    'unit': heat_cons.get('unit') + '/' + population.get('unit')
                }

                hdm.get('values').append(v)

        # compute heat consumption/person if both layers are selected
        pop1ha_name = 'population_density_ha'
        hdm_name = 'heat_density_ha'
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
                        if v.get('name') == 'population':
                            population = v

            if heat_cons != None and population != None:
                pop_val = float(population.get('value', 1))
                pop_val = pop_val if pop_val > 0 else 1
                hea_val = float(heat_cons.get('value', 0))

                v = {
                    'name': 'consumption_per_citizen',
                    'value': hea_val / pop_val,
                    'unit': heat_cons.get('unit') + '/' + population.get('unit')
                }

                hdm.get('values').append(v)

        nuts = None
        r = re.compile("^.*_nuts[0-3]$")
        nuts_layers = list(filter(r.match, layers))
        if nuts_layers != None and hasattr(nuts_layers, '__len__') and len(nuts_layers) > 0:
            nuts_levels = []
            for l in nuts_layers:
                try:
                    nuts_levels.append(int(re.search("^.*nuts([0-3])$", l).group(1)))
                except (AttributeError, ValueError):
                    pass

            nuts = NutsRG01M.nuts_in_geometry(geometry=geom, year=year, nuts_level=max(nuts_levels))

        return {
            "layers": output,
            "feature_collection": nuts
        }

