import datetime

from main_api.models import db
from geoalchemy2 import Geometry
from sqlalchemy import func
from geojson import FeatureCollection, Feature
from geoalchemy2.shape import to_shape



class Nuts(db.Model):
    __tablename__ = 'nuts_rg_01m'
    __table_args__ = (
        db.UniqueConstraint('nuts_id'),
        {"schema": 'geo'}
    )

    CRS = 4258

    gid = db.Column(db.Integer, primary_key=True)
    nuts_id = db.Column(db.String(14))
    name = db.Column(db.String(255))
    stat_levl_ = db.Column(db.Integer)
    shape_area = db.Column(db.Numeric)
    shape_len = db.Column(db.Numeric)
    geom = db.Column(Geometry('GEOMETRY', 4258))

    def __repr__(self):
        return "<Nuts(nuts_id='%s', name='%s', level='%s')>" % (
            self.nuts_id, self.name, self.stat_levl_)

    @staticmethod
    def nuts_in_geometry(geometry, year, nuts_level):
        query = db.session.query(
                Nuts
            ). \
            filter(Nuts.stat_levl_ == nuts_level). \
            filter(func.ST_Within(Nuts.geom,
                                  func.ST_Transform(func.ST_GeomFromEWKT(geometry), Nuts.CRS))).all()

            #filter(Nuts.date == datetime.datetime.strptime(str(year), '%Y')). \

        if query == None or len(query) < 1:
            return []

        sum_area = 0.0
        sum_len = 0.0
        features = []
        for nuts in query:
            # sum area
            sum_area += float(nuts.shape_area)
            sum_len += float(nuts.shape_len)

            # create feature
            geometry = to_shape(nuts.geom)
            feature = Feature(
                id=nuts.gid,
                geometry=geometry,
                properties= {
                    'values': [{
                        'name': 'area',
                        'value': nuts.shape_area,
                        'unit': 'm'
                    }, {
                        'name': 'name',
                        'value': nuts.name,
                        'unit': None
                    }, {
                        'name': 'nuts_id',
                        'value': nuts.nuts_id,
                        'unit': None
                    }]
                }
            )
            features.append(feature)

        properties = {
            'values': [{
            'name': 'year',
            'value': year,
            'unit': 'year'
            }, {
                'name': 'nuts_level',
                'value': nuts_level,
                'unit': None
            }, {
                'name': 'area',
                'value': sum_area,
                'unit': 'd'
            }]
        }

        crs = {
            "type": "name",
            "properties": {
                "name": "EPSG:%d" % Nuts.CRS
            }
        }

        return FeatureCollection(features, properties=properties, crs=crs)

