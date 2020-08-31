import os, sys, importlib.util

constants_path = os.path.join(os.path.dirname(__file__), '..', 'app', 'constants.py')
constants_spec = importlib.util.spec_from_file_location('constants', constants_path)
constants = importlib.util.module_from_spec(constants_spec)
constants_spec.loader.exec_module(constants)


basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, '../data.sqlite')

# Flask settings
DEBUG = True
FLASK_SECRET_KEY = constants.FLASK_SECRET_KEY
FLASK_SALT = constants.FLASK_SALT

# Database
user = constants.USER_DB
password = constants.PASSWORD_DB
host = constants.HOST_DB
port = constants.PORT_DB
database = constants.DATABASE_DB

SQLALCHEMY_DATABASE_URI = 'postgresql://{user}:{password}@{host}:{port}/{db}'.format(
    user=user,
    password=password,
    host=host,
    port=port,
    db=database
)

SQLALCHEMY_BINDS = {
    'cm_db': 'sqlite:///' + db_path
}

SECRET_KEY = FLASK_SECRET_KEY
SQLALCHEMY_TRACK_MODIFICATIONS = True
SWAGGER_UI_DOC_EXPANSION = 'list'
RESTPLUS_VALIDATE = True
RESTPLUS_MASK_SWAGGER = False
ERROR_404_HELP = False
RESTPLUS_JSON = {
    'separators': (',', ':')
}

CELERY_BROKER_URL = constants.CELERY_BROKER_URL
CELERY_RESULT_BACKEND = constants.CELERY_RESULT_BACKEND
UPLOAD_FOLDER = 'uploaded_file'
USER_UPLOAD_FOLDER = constants.USER_UPLOAD_FOLDER

# Geoserver
GEOSERVER_API_URL = constants.GEOSERVER_API_URL
GEOSERVER_USER = constants.GEOSERVER_USER
GEOSERVER_PASSWORD = constants.GEOSERVER_PASSWORD

# Mail
MAIL_USERNAME = constants.MAIL_USERNAME
MAIL_PASSWORD = constants.MAIL_PASSWORD
MAIL_DEFAULT_SENDER = constants.MAIL_DEFAULT_SENDER
MAIL_SERVER = constants.MAIL_SERVER
MAIL_PORT = constants.MAIL_PORT
