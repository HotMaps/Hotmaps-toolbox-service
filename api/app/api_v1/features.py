from app import celery
import logging
import re
import os.path
import pandas as pd
import numpy as np
from osgeo import gdal

from flask_restplus import Resource
from app.decorators.restplus import api
from app.decorators.exceptions import HugeRequestException, IntersectionException, NotEnoughPointsException, ParameterException, RequestException

import shapely.geometry as shapely_geom

from app import constants

import app
import json
from ..decorators.timeout import return_on_timeout_endpoint
from app.model import Features




log = logging.getLogger(__name__)

nsFeatures = api.namespace('features', description='Operations related to geo features')
ns = nsFeatures


@ns.route('/select/<string:layer>/<string:wkt>')
@api.response(530, 'Request error')
@api.response(531, 'Missing parameter')
class SelectFeatures(Resource):
    @return_on_timeout_endpoint()
    def get(self, layer, wkt):
        """
        The method called to get the features in selection (wkt)
        :return:
        """
        schema = 'geo'
        if layer == 'lau':
            schema = 'public'
        # get features
        features = Features.select_features(layer=layer, schema=schema, wkt=wkt)

        # return result
        return features

