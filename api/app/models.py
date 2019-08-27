from .. import dbCM as db

class CalculationModules(db.Model):
    '''
    This class will describe the model of a calculation module
    '''
    __tablename__ = 'cm'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    description = db.Column(db.String(255))
    url = db.Column(db.String(255))
    category = db.Column(db.String(255))
    layers_needed = db.Column(String(255))
    authorized_scale = db.Column(String(255))
    description_link = db.Column(String(255))
    created_at = db.Column(db.DateTime())
    updated_at = db.Column(db.DateTime())
    type_layer_needed = db.Column(db.String(255))
    vectors_needed = db.Column(db.String(255))
    inputs = db.relationship('CalculationModuleInputs', cascade="delete")


class CalculationModuleInputs(db.Model):
    '''
    This class will describe the model of an input of a calculation module
    '''
    __tablename__ = 'cm_inputs'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    type = db.Column(db.String(255))
    parameter_name = db.Column(db.String(255))
    value = db.Column(db.String(255))
    priority = db.Column(db.Integer)
    unit = db.Column(db.String(255))
    min = db.Column(db.Integer)
    max = db.Column(db.Integer)
    created_at = db.Column(db.DateTime())
    updated_at = db.Column(db.DateTime())
    cm_id = db.Column(db.Integer, db.ForeignKey('cm.id'))


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

        already_exist = CalculationModules.query.get(cm_id)
        if already_exist:
            update_calulation_module(already_exist, cm_name, cm_description, cm_category, cm_url, layers_needed, createdAt,
                updatedAt, type_layer_needed, authorized_scale, description_link, vectors_needed, inputs_calculation_module)
        else:
            cm = CalculationModules(id=cm_id, name=cm_name, description=cm_description, url=cm_url, category=cm_category,
                layers_needed=layers_needed, authorized_scale=authorized_scale, description_link=description_link,
                created_at=createdAt, updated_at=updateAt, type_layer_needed=type_layer_needed, vectors_needed=vectors_needed)

            db.session.add(cm)
            db.session.commit()

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

            new_input = CalculationModuleInputs(name=input_name, type=input_type, parameter_name=input_parameter_name,
                value=input_value, priority=input_priority, unit=input_unit, min=input_min, max=input_max, cm_id=cm.id)
            db.session.add(new_input)
        db.session.commit()


def update_calulation_module(cm, cm_name, cm_description, cm_category, cm_url, layers_needed, createdAt, updatedAt, type_layer_needed, authorized_scale, description_link, vectors_needed, inputs_calculation_module):
    cm.name = cm_name
    cm.description = cm_description
    cm.category = cm_category
    cm.url = cm_url
    cm.layers_needed = layers_needed
    cm.createdAt = createdAt
    cm.updatedAt = updateAt
    cm.type_layer_needed = type_layer_needed
    cm.authorized_scale = authorized_scale
    cm.description_link = description_link
    cm.vectors_needed = vectors_needed

    db.session.commit()

    inputs = cm.inputs
    for input in inputs:
        db.session.delete(input)
    db.session.commit()


def getUI(cm_id):
    cm = CalculationModules.query.get(cm_id)
    response = helper.retrieve_list_from_sql_result(cm.inputs)
    return response

def getCMList():
    results = CalculationModules.query.all()
    response = helper.retrieve_list_from_sql_result(results)
    return response

# def get_vectors_needed(cm_id):
#     conn = myCMpool.connect()
#     cursor = conn.cursor()
#     vectors_needed = cursor.execute('select vectors_needed from calculation_module where cm_id = ?',
#                             (cm_id))
#     conn.commit()
#     vectors_needed = vectors_needed.fetchone()[0]
#     vectors_needed = helper.unicode_array_to_string(vectors_needed)
#     conn.close()
#     return vectors_needed

def delete_cm(cm_id):
    cm = CalculationModules.query.get(cm_id)
    db.session.delete(cm)
    db.session.commit()
