from datetime import datetime
from app import helper
from app import db
from flask import current_app
from sqlalchemy.inspection import inspect

class CalculationModules(db.Model):
    '''
    This class will describe the model of a calculation module
    '''
    __bind_key__ = 'db_cm'
    __tablename__ = 'cm'

    cm_id = db.Column(db.Integer, primary_key=True)
    cm_name = db.Column(db.String(255))
    cm_description = db.Column(db.String(255))
    cm_url = db.Column(db.String(255))
    category = db.Column(db.String(255))
    layers_needed = db.Column(db.String(255))
    authorized_scale = db.Column(db.String(255))
    description_link = db.Column(db.String(255))
    createdAt = db.Column(db.DateTime())
    updatedAt = db.Column(db.DateTime())
    type_layer_needed = db.Column(db.String(255))
    vectors_needed = db.Column(db.String(255))
    inputs = db.relationship('CalculationModuleInputs', cascade="delete")


class CalculationModuleInputs(db.Model):
    '''
    This class will describe the model of an input of a calculation module
    '''
    __bind_key__ = 'db_cm'
    __tablename__ = 'cm_inputs'

    input_id = db.Column(db.Integer, primary_key=True)
    input_name = db.Column(db.String(255))
    input_type = db.Column(db.String(255))
    input_parameter_name = db.Column(db.String(255))
    input_value = db.Column(db.String(255))
    input_priority = db.Column(db.Integer)
    input_unit = db.Column(db.String(255))
    input_min = db.Column(db.Integer)
    input_max = db.Column(db.Integer)
    createdAt = db.Column(db.DateTime())
    updatedAt = db.Column(db.DateTime())
    cm_id = db.Column(db.Integer, db.ForeignKey('cm.cm_id'))


def register_calulation_module(data):
    if data is not None:
        # conn = myCMpool.connect()
        # cursor = conn.cursor()
        cm_id = data['cm_id']
        cm_name = data['cm_name']
        cm_description = data['cm_description']
        cm_url = data['cm_url']
        cm_category = data['category']
        type_layer_needed = str(data['type_layer_needed'])
        layers_needed = str(data['layers_needed'])

        try:
            authorized_scale = str(data['authorized_scale'])
        except:
            authorized_scale = "[]"

        try:
            description_link = str(data['description_link'])
        except:
            description_link = ""

        try:
            vectors_needed = str(data['vectors_needed'])
        except:
            vectors_needed = "[]"

        updatedAt = datetime.utcnow()
        createdAt = datetime.utcnow()
        inputs_calculation_module = data['inputs_calculation_module']

        already_exists = CalculationModules.query.get(cm_id)
        if already_exists:
            update_calulation_module(already_exists, cm_name, cm_description, cm_category, cm_url, layers_needed, createdAt,
                updatedAt, type_layer_needed, authorized_scale, description_link, vectors_needed, inputs_calculation_module)
            id = already_exists.cm_id
        else:
            cm = CalculationModules(cm_id=cm_id, cm_name=cm_name, cm_description=cm_description, cm_url=cm_url, category=cm_category,
                layers_needed=layers_needed, authorized_scale=authorized_scale, description_link=description_link,
                createdAt=createdAt, updatedAt=updatedAt, type_layer_needed=type_layer_needed, vectors_needed=vectors_needed)

            db.session.add(cm)
            db.session.commit()
            id = cm.cm_id

        for input in inputs_calculation_module:
            input_name = input['input_name']
            input_type = input['input_type']
            input_parameter_name = input['input_parameter_name']
            input_value = str(input['input_value'])
            input_unit = input['input_unit']
            input_min = input['input_min']
            input_max = input['input_max']
            try:
                input_priority = input['input_priority']
            except:
                input_priority = 0

            new_input = CalculationModuleInputs(input_name=input_name, input_type=input_type, input_parameter_name=input_parameter_name,
                input_value=input_value, input_priority=input_priority, input_unit=input_unit, input_min=input_min,
                createdAt=createdAt, updatedAt=updatedAt, input_max=input_max, cm_id=id)
            db.session.add(new_input)
        db.session.commit()


def update_calulation_module(cm, cm_name, cm_description, cm_category, cm_url, layers_needed, createdAt, updatedAt, type_layer_needed, authorized_scale, description_link, vectors_needed, inputs_calculation_module):
    cm.cm_name = cm_name
    cm.cm_description = cm_description
    cm.cm_category = cm_category
    cm.cm_url = cm_url
    cm.layers_needed = layers_needed
    cm.createdAt = createdAt
    cm.updatedAt = updatedAt
    cm.type_layer_needed = type_layer_needed
    cm.authorized_scale = authorized_scale
    cm.description_link = description_link
    cm.vectors_needed = vectors_needed

    db.session.commit()

    inputs = cm.inputs
    for input in inputs:
        db.session.delete(input)
    db.session.commit()

def retrieve_list_from_sql_result(results):
    response = []
    for element in results:
        json_element = {}
        for column in element.__table__.columns:
            json_element[column.name] = str(getattr(element, column.name))
        response.append(json_element)
    return response

def getUI(cm_id):
    cm = CalculationModules.query.get(cm_id)
    response = retrieve_list_from_sql_result(cm.inputs)
    return response

def getCMList():
    results = CalculationModules.query.all()
    response = retrieve_list_from_sql_result(results)
    return response

# def get_vectors_needed(cm_id):
#     cm = CalculationModules.query.get(cm_id)
#     vectors = cm.vectors_needed
#     vectors_needed = vectors_needed.fetchone()[0]  ????????
#     vectors_needed = helper.unicode_array_to_string(vectors_needed)  ?????????
#     return vectors_needed

def delete_cm(cm_id):
    cm = CalculationModules.query.get(cm_id)
    db.session.delete(cm)
    db.session.commit()
