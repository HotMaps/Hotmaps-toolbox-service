import logging
import re
from flask import request
from flask_restplus import Resource
from main_api.api.main.serializers import stats_layers_area_input, stats_layers_output, stats_layers_nuts_input, stats_layers_nuts_output, stats_layer_point_input, stats_layers_area_nuts_input
from main_api.api.restplus import api
from main_api.models.wwtp import Wwtp, WwtpNuts3, WwtpLau2
from main_api.models.heat_density_map import HeatDensityMap, HeatDensityHa, HeatDensityNuts3, HeatDensityLau2
from main_api.models.population_density import PopulationDensityHa, PopulationDensityNuts3, PopulationDensityLau2
from main_api.models.nuts import Nuts, NutsRG01M
from main_api.models.lau import Lau
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
    'wwtp_nuts3': WwtpNuts3,
    'wwtp_ha': Wwtp,
    'wwtp_lau2': WwtpLau2,
    'population': PopulationDensityNuts3,
    'population_density_nuts3': PopulationDensityNuts3,
    'population_density_ha': PopulationDensityHa,
    'population_density_lau2': PopulationDensityLau2,
    'heat_density_map': HeatDensityMap,
    'heat_density_ha': HeatDensityHa,
    'heat_density_nuts3': HeatDensityNuts3,
    'heat_density_lau2': HeatDensityLau2,
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

        # compute heat consumption/person if both layers are selected
        pop_lau_name = 'population_density_lau2'
        heat_lau_name = 'heat_density_lau2'
        if pop_lau_name in layers and heat_lau_name in layers:
            hdm = None
            heat_cons = None
            population = None

            for l in output:
                if l.get('name') == heat_lau_name:
                    hdm = l
                    for v in l.get('values', []):
                        if v.get('name') == 'heat_consumption':
                            heat_cons = v
                if l.get('name') == pop_lau_name:
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

        # return feature collection
        # priority lau higher level first
        # then nuts higher level first
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

        r = re.compile("^.*_lau[0-3]$")
        lau_layers = list(filter(r.match, layers))
        if lau_layers != None and hasattr(lau_layers, '__len__') and len(lau_layers) > 0:
            levels = []
            for l in lau_layers:
                try:
                    levels.append(int(re.search("^.*lau([0-3])$", l).group(1)))
                except (AttributeError, ValueError):
                    pass

            nuts = Lau.nuts_in_geometry(geometry=geom, year=2013, level=max(levels))

        return {
            "layers": output,
            "feature_collection": nuts
        }


@ns.route('/layers/nuts/')
@api.response(404, 'No data found for that specific list of NUTS.')
class StatsLayersNutsInArea(Resource):
    @api.marshal_with(stats_layers_nuts_output)
    @api.expect(stats_layers_nuts_input)
    def post(self):
        """
        Returns the statistics for specific layers, area and year
        :return:
        """
        year = api.payload['year']
        layers = api.payload['layers']
        nuts = api.payload['nuts']

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
                'values': a.aggregate_for_nuts_selection(nuts=nuts, year=year)
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
        pop_lau_name = 'population_density_lau2'
        heat_lau_name = 'heat_density_lau2'
        if pop_lau_name in layers and heat_lau_name in layers:
            hdm = None
            heat_cons = None
            population = None

            for l in output:
                if l.get('name') == heat_lau_name:
                    hdm = l
                    for v in l.get('values', []):
                        if v.get('name') == 'heat_consumption':
                            heat_cons = v
                if l.get('name') == pop_lau_name:
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

        return {
            "layers": output,
        }
