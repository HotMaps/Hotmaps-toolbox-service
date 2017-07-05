from flask_restplus import fields
from main_api.api.restplus import api
from geoalchemy2.shape import to_shape
import geojson


class GeoJSON(fields.Raw):
    def format(self, value):
        shape = to_shape(value)
        geo_json = geojson.Feature(geometry=shape, properties={})
        return geo_json


nuts = api.model('Nuts', {
    'gid': fields.Integer(readOnly=True, description='ID of the nuts geometry'),
    'nuts_id': fields.String(required=True, description='Nuts ID'),
    'name': fields.String(description='Name of the nuts'),
    'nuts_level': fields.Integer(attribute='stat_levl_', description='Nuts level'),
    'shape_area': fields.Float(description='Shape area'),
    'shape_len': fields.Float(desciption='Shape length'),
    'geom': GeoJSON(attribute='geom')
})

population_density = api.model('Population density', {
    'id': fields.Integer(readOnly=True, description='ID of the population density object'),
    'date': fields.Date(description='Date related to the density'),
    'value': fields.Integer(description='Density value'),
    'nuts_id': fields.String(attribute='nuts.nuts_id'),
    'nuts': fields.Nested(nuts)
})

total_density_for_nuts_area = api.model('Population density sum', {
    'sum_density': fields.Integer(attribute='sum_density', description='Sum of density for selected area'),
    'geometries': fields.String(attribute='geometries')
})

