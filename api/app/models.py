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
    user_id = db.Column(db.Integer, db.ForeignKey('user.users.id'))

"CREATE TABLE calculation_module (cm_id INTEGER NOT NULL, cm_name VARCHAR(255), "
               "cm_description VARCHAR(255),cm_url VARCHAR(255),category VARCHAR(255),layers_needed VARCHAR(255),authorized_scale VARCHAR(255),description_link VARCHAR(255),createdAt REAL(255),updatedAt REAL(255),type_layer_needed REAL(255),vectors_needed REAL(255),"
               " PRIMARY KEY(cm_id))"

class CalculationModuleInputs(db.Model):
    '''
    This class will describe the model of an input of a calculation module
    '''
    __tablename__ = 'cm_input'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(255))
    name = db.Column(db.String(255))
    layer = db.Column(db.String(255))
    layer_type = db.Column(db.String(255))
    size = db.Column(db.Numeric)
    url = db.Column(db.String(255))
    is_generated = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.users.id'))
