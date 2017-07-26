from flask_restplus import fields
from main_api.api.restplus import api
from geoalchemy2.shape import to_shape
from geojson import Feature, FeatureCollection, dumps

class Geometry(fields.Raw):
    def format(self, value):
        shape = to_shape(value)
        geo_json = Feature(geometry=shape, properties={})
        return geo_json


point = api.model('Point', {
    'lat': fields.Float(description='Latitude'),
    'lng': fields.Float(description='Longitude')
})

grid = api.model('Grid', {
    'gid': fields.Integer(readOnly=True, description='ID of the grid geometry'),
    'id': fields.Float(desciption='id'),
    'xmin': fields.String(description='Xmin'),
    'xmax': fields.String(description='Xmax'),
    'ymin': fields.Integer(description='Ymin'),
    'ymax': fields.Float(description='Ymax'),
    'geom': Geometry(attribute='geom', description='Geometry')
})

grid_properties = api.model('Properties', {
    'xmin': fields.Integer(description='Xmin'),
    'xmax': fields.Integer(description='Xmax'),
    'ymin': fields.Integer(description='Ymin'),
    'ymax': fields.Integer(description='Ymax'),

})

multipolygon_geometry = api.model('MultiPolygon', {
    'type': fields.String(),
    'coordinates': fields.List(fields.List(fields.List(fields.List(fields.Float))))
})
grid_feature = api.model('Feature', {
    'type': fields.String(),
    'id': fields.Float(desciption='id'),
    'geometry': fields.Nested(multipolygon_geometry),
    'properties': fields.Nested(grid_properties)
})

grid_feature_collection = api.model('FeatureCollection', {
    'type': fields.String(),
    'features': fields.List(fields.Nested(grid_feature))
})

area = api.model('Input area', {
    'points': fields.List(fields.Nested(point))
})


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

total_density_for_nuts_area_input = api.model('Input for population density for area', {
    'nuts_level': fields.Integer(description='Nuts level'),
    'year': fields.Integer(description='Year'),
    'points': fields.List(fields.Nested(point))
})

