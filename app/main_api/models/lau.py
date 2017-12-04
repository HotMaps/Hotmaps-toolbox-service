import datetime

from main_api.models import db
from geoalchemy2 import Geometry
from sqlalchemy import func
from geojson import FeatureCollection, Feature
from geoalchemy2.shape import to_shape


class Lau(db.Model):
    __tablename__ = 'lau'
    __table_args__ = (
        {"schema": 'geo'}
    )

    CRS = 4258

    gid = db.Column(db.Integer, primary_key=True)
    comm_id = db.Column(db.String(14))
    #name = db.Column(db.String(255))
    stat_levl_ = db.Column(db.Integer)
    shape_area = db.Column(db.Numeric)
    shape_leng = db.Column(db.Numeric)
    geom = db.Column(Geometry('GEOMETRY', 4258))
    year = db.Column(db.Date)

    def __repr__(self):
        return "<Lau(comm_id='%s', level='%s')>" % (
            self.comm_id, self.stat_levl_)

    @staticmethod
    def nuts_in_geometry(geometry, year, level):
        query = db.session.query(
                Lau
            ). \
            filter(Lau.stat_levl_ == level). \
            filter(func.ST_Within(Lau.geom,
                                  func.ST_Transform(func.ST_GeomFromEWKT(geometry), Lau.CRS))).all()

            #filter(Lau.date == datetime.datetime.strptime(str(year), '%Y')). \

        if query == None or len(query) < 1:
            return []

        sum_area = 0.0
        sum_len = 0.0
        features = []
        for lau in query:
            # sum area
            sum_area += float(lau.shape_area)
            sum_len += float(lau.shape_leng)

            # create feature
            geometry = to_shape(lau.geom)
            feature = Feature(
                id=lau.gid,
                geometry=geometry,
                properties= {
                    'values': [{
                        'name': 'area',
                        'value': lau.shape_area,
                        'unit': 'm'
                    }, #{
                        #'name': 'name',
                        #'value': nuts.name,
                        #'unit': None
                    #},
                    {
                        'name': 'comm_id',
                        'value': lau.comm_id,
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
                'name': 'comm_level',
                'value': level,
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
                "name": "EPSG:%d" % Lau.CRS
            }
        }

        return FeatureCollection(features, properties=properties, crs=crs)



