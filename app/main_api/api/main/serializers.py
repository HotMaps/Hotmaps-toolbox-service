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
    'id': fields.Integer(desciption='id'),
    'xmin': fields.String(description='Xmin'),
    'xmax': fields.String(description='Xmax'),
    'ymin': fields.String(description='Ymin'),
    'ymax': fields.String(description='Ymax'),
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
crs_properties = api.model('properties', {
    'name': fields.String
})
feature_collection_crs = api.model('crs', {
    'type': fields.String,
    'properties': fields.Nested(crs_properties)
})
grid_feature = api.model('Feature', {
    'type': fields.String(),
    'id': fields.Float(desciption='id'),
    'geometry': fields.Nested(multipolygon_geometry),
    'properties': fields.Nested(grid_properties)
})

grid_feature_collection = api.model('FeatureCollection', {
    'type': fields.String(),
    'crs': fields.Nested(feature_collection_crs),
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

raster_for_area_input = api.model('Input for population density for area', {
    'year': fields.Integer(description='Year'),
    'points': fields.List(fields.Nested(point))
})

stats_layers_area_input = api.model('Input for statistics on layers, area and year', {
    'layers': fields.List(fields.String(description='Layer')),
    'year': fields.Integer(description='Year'),
    'points': fields.List(fields.Nested(point))
})

aggregation_value = api.model('Layer aggregation values', {
    'name': fields.String(description='Name'),
    'value': fields.String(description='Value'),
    'unit': fields.String(description='Unit')
})

stats_layer_aggregation = api.model('Layer aggregation', {
    'name': fields.String(description='Name'),
    'values': fields.List(fields.Nested(aggregation_value))
})

vector_feature_properties = api.model('Feature properties', {
    'values': fields.List(fields.Nested(aggregation_value)),
})

vector_feature = api.model('Feature', {
    'type': fields.String(),
    'id': fields.Float(desciption='id'),
    'geometry': fields.Nested(multipolygon_geometry),
    'properties': fields.List(fields.Nested(vector_feature_properties))
})

vector_feature_collection = api.model('Feature collection', {
    'type': fields.String(),
    'crs': fields.Nested(feature_collection_crs),
    'features': fields.List(fields.Nested(vector_feature)),
    'properties': fields.List(fields.Nested(vector_feature_properties))
})

stats_layers_output = api.model('Stats for selected layers, year and area', {
    'layers': fields.List(fields.Nested(stats_layer_aggregation)),
    'feature_collection': fields.Nested(vector_feature_collection)
})

stats_layers_area_nuts_input = api.model('Input for statistics on layers, area and year', {
    'layers': fields.List(fields.String(description='Layer')),
    'nuts_level': fields.String(description='Nuts level'),
    'year': fields.Integer(description='Year'),
    'points': fields.List(fields.Nested(point))
})

stats_layer_point_input = api.model('Input for statistics on layers, year, point', {
    'layers': fields.List(fields.String(description='Layer')),
    'nuts_level': fields.String(description='Nuts level'),
    'year': fields.Integer(description='Year'),
    'point': fields.Nested(point)
})

load_profile_aggregation_month_row = api.model('Output row for load profile', {
    'average': fields.Float(description='Average value per month'),
    'min': fields.Float(description='Minimum value per month'),
    'max': fields.Float(description='Maximum value per month'),
    'unit': fields.String(descriptsion='Unit'),
    'month': fields.Integer(description='Month'),
    'year': fields.Integer(description='Year'),
    'granularity': fields.String(description='Granularity'),
})
load_profile_aggregation_month = api.model('Output for load profile', {
    'values': fields.List(fields.Nested(load_profile_aggregation_month_row)),
    'nuts': fields.String(description='List of NUTS'),
    'nuts_level': fields.String(descriptions='Nuts level')
})
load_profile_aggregation_month_input = api.model('Input for load profile', {
    'year': fields.Integer(description='Year'),
    'nuts': fields.List(fields.String(descriptions='List of NUTS')),
    'nuts_level': fields.String(description='Nuts level')
})

load_profile_aggregation_hour_row = api.model('Output row for load profile (hour per day)', {
    'value': fields.Float(description='Average value per hour'),
    'min': fields.Float(description='Minimum value per hour'),
    'max': fields.Float(description='Maximum value per hour'),
    'unit': fields.String(descriptsion='Unit'),
    'hour_of_day': fields.Integer(description='Hour'),
    'month': fields.Integer(description='Month'),
    'year': fields.Integer(description='Year'),
    'granularity': fields.String(description='Granularity'),
})
load_profile_aggregation_hour = api.model('Output for load profile (hour per day)', {
    'values': fields.List(fields.Nested(load_profile_aggregation_hour_row)),
    'nuts': fields.String(description='List of NUTS'),
    'nuts_level': fields.String(descriptions='Nuts level')
})

load_profile_aggregation_hour_input = api.model('Input for load profile (hour per day)', {
    'year': fields.Integer(description='Year'),
    'month': fields.Integer(description='Month'),
    'nuts': fields.List(fields.String(descriptions='List of NUTS')),
    'nuts_level': fields.String(description='Nuts level')
})

stats_layers_nuts_output = api.model('Stats for selected layers, year and area', {
    'layers': fields.List(fields.Nested(stats_layer_aggregation)),
    'load_profile_month': fields.Nested(load_profile_aggregation_month),
})

stats_layers_nuts_input = api.model('Input for statistics on layers, list of nuts and year', {
    'layers': fields.List(fields.String(description='Layer')),
    'nuts': fields.List(fields.String(descriptions='List of NUTS')),
    'year': fields.Integer(description='Year'),
})
