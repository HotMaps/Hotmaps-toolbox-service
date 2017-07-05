# Flask settings
#FLASK_SERVER_NAME = '0.0.0.0:80'
FLASK_SERVER_NAME = '0.0.0.0:5000'
FLASK_DEBUG = True  # Do not use debug mode in production
FLASK_SECRET_KEY = 'test-secret-key'

# Flask-Restplus settings
RESTPLUS_SWAGGER_UI_DOC_EXPANSION = 'list'
RESTPLUS_VALIDATE = True
RESTPLUS_MASK_SWAGGER = False
RESTPLUS_ERROR_404_HELP = False

# SQLAlchemy settings
SQLALCHEMY_DATABASE_URI = 'postgresql://hotmaps:Dractwatha9@192.168.99.101:32768/toolboxdb'
SQLALCHEMY_TRACK_MODIFICATIONS = False