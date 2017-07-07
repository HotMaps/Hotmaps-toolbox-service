from flask_restplus import fields
from main_api.api.restplus import api
from geoalchemy2.shape import to_shape
import geojson


class Geometry(fields.Raw):
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
    'geom': Geometry(attribute='geom')
})

population_density = api.model('Population density', {
    'id': fields.Integer(readOnly=True, description='ID of the population density object'),
    'date': fields.Date(description='Date related to the density'),
    'value': fields.Integer(description='Density value'),
    'nuts_id': fields.String(attribute='nuts.nuts_id'),
    'nuts': fields.Nested(nuts)
})

total_density_for_nuts_area = api.model('Population density sum', {
    'year': fields.Integer(attribute='year', description='Year'),
    'nuts_level': fields.Integer(attribute='nuts_level', description='Nuts level'),
    'sum_density': fields.Integer(attribute='sum_density', description='Sum of density for selected area'),
    'geometries': fields.String(attribute='geometries')
})

point = api.model('Point', {
    'lat': fields.Float(description='Latitude'),
    'lng': fields.Float(description='Longitude')
})

total_density_for_nuts_area_input = api.model('Input for population density for area', {
    'nuts_level': fields.Integer(description='Nuts level'),
    'year': fields.Integer(description='Year'),
    'points': fields.List(fields.Nested(point))
})

# Population density output format
density_properties = {}
density_properties['density'] = fields.Integer(description='Population density')
density_properties['year'] = fields.Integer(description='Year')
density_properties['nuts_level'] = fields.Integer(description='Nuts level')

density_feature = {}
density_feature['type'] = 'Feature'
density_feature['properties'] = fields.Nested(density_properties)
density_feature['geometry'] = fields.String(description='Geometry')

density_featurecollection = {}
density_featurecollection['type'] = 'FeatureCollection'
density_featurecollection['features'] = fields.List(fields.Nested(density_feature))
# end