
from flask import url_for
from app import dbCM as db

from app.decorators.exceptions import ValidationError

from datetime import datetime


class ComputationModule(db.Model):
    __tablename__ = 'computational_module'
    cm_Id = db.Column(db.Integer, primary_key=True)
    cm_name  = db.Column(db.String())
    cm_description  = db.Column(db.String())
    category = db.Column(db.DateTime)
    cm_url = db.Column(db.String())
    createdAt = db.Column(db.DateTime)
    updateAt = db.Column(db.DateTime)
    def set_computation_module(self, cm_Id, cm_name, category,input_components,cm_url):
        self.cm_Id = cm_Id
        self.cm_name = cm_name
        self.category = category
        self.cm_url = cm_url
        self.createdAt = datetime.utcnow()
        self.updateAt = datetime.utcnow()
    def get_url(self):
        return url_for('api.get_computational_module', objectId=self.objectId, _external=True)
    def export_data(self):
        return {'results': [{
                                'cm_Id': self.cm_Id,'cm_name': self.cm_description,'cm_description': self.cm_description,
                                'category': self.category,'createdAt':  self.createdA,'createdAt':  self.createdAt,'updatedAt':  self.updateAt,
                                }]}
    def import_data(self, data):
        try:
            self.cm_name = data['cm_name']
            self.category = data['category']
            self.cm_description = data['cm_description']
            self.category = data['category']
            self.cm_url = data['cm_url']
            self.cm_Id = data['id']

            self.updatedAt = datetime.utcnow()
            self.createdAt = datetime.utcnow()
        except KeyError as e:
            raise ValidationError('Invalid action: missing ' + e.args[0])
        return self

class InputComponents(db.Model):
    __tablename__ = 'input_computation_module'
    objectId = db.Column(db.Integer, primary_key=True)
    cm_Id = db.Column(db.Integer, db.ForeignKey('computational_module.cm_Id'))
    component_name = db.Column(db.String())
    component_type = db.Column(db.String())
    parameter_name = db.Column(db.String())
    value = db.Column(db.String())
    min = db.Column(db.String())
    max = db.Column(db.String())
    unit = db.Column(db.String())
    createdAt = db.Column(db.DateTime)
    updateAt = db.Column(db.DateTime)
    def set_action(self, name, category_id):
        self.name = name
        self.category_id = category_id
        self.createdAt = datetime.utcnow()
        self.updateAt = datetime.utcnow()
    def get_url(self):
        return url_for('api.get_input_computation_module', objectId=self.objectId, _external=True)
    def export_data(self):
        return {'results': [{
            'objectId': self.objectId,'cm_Id': self.cm_Id,
            'component_name': self.component_name,
            'component_type': self.component_type,
            'parameter_name': self.parameter_name,
            'value': self.value,
            'min': self.min,
            'max': self.max,
            'unit': self.unit,
            'createdAt':  self.createdAt,
            'updatedAt':  self.updateAt,
        }]}
    def import_data(self, data):
        try:
            self.component_name = data['component_name']
            self.component_type = data['component_type']
            self.parameter_name = data['parameter_name']
            self.value = data['value']
            self.max = data['max']
            self.min = data['min']
            self.min = data['min']
            self.unit = data['unit']
            self.createdAt = datetime.utcnow()
            self.updateAt = datetime.utcnow()
        except KeyError as e:
            raise ValidationError('Invalid action type: missing ' + e.args[0])
        return self

