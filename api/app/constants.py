import os

# General 
API_URL = os.environ.get('API_URL')
API_PORT = os.environ.get('API_PORT')

CLIENT_URL = os.environ.get('CLIENT_URL')

# Database
HOST_DB = os.environ.get('DB_HOST')
PORT_DB = os.environ.get('DB_PORT')
USER_DB = os.environ.get('DB_USER')
PASSWORD_DB = os.environ.get('DB_PASSWORD')
DATABASE_DB = os.environ.get('DB_DATABASE')

# Flask settings
FLASK_SERVER_NAME = os.environ.get('FLASK_SERVER_NAME')
FLASK_DEBUG = False  # Do not use debug mode in production
FLASK_SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')
FLASK_SALT = os.environ.get('FLASK_SALT')
CELERY_BROKER_URL_DOCKER= 'amqp://admin:mypass@rabbit:5672/'
CELERY_BROKER_URL_LOCAL  = 'amqp://localhost/'

# Flask-Restplus settings
RESTPLUS_SWAGGER_UI_DOC_EXPANSION = 'list'
RESTPLUS_VALIDATE = True
RESTPLUS_MASK_SWAGGER = False
RESTPLUS_ERROR_404_HELP = False
RESTPLUS_JSON = {
    'separators': (',', ':')
}

# Celery
CELERY_ALWAYS_EAGER = False
# CELERY_RESULT_BACKEND = 'redis://localhost:6379'
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND')
CELERYD_SOFT_TIME_LIMIT = os.environ.get('CELERYD_SOFT_TIME_LIMIT')

RPC_Q = 'rpc_queue_CM_compute'
TIMEOUT_ALIVE_CM = 60
TIMEOUT_START_CM = 1
TIMEOUT_DELETE_CM= 15
RPC_CM_ALIVE= 'rpc_queue_CM_ALIVE'

# The default timeout for API function in seconds
DEFAULT_TIMEOUT = 3600  # 1 hour

CM_REGISTER_Q = 'rpc_queue_CM_register'

CM_DB_NAME = 'calculation_module.db'

# disc space available for every users (in MegaOctet)
USER_DISC_SPACE_AVAILABLE = 500

# Mail
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
MAIL_DEFAULT_SENDER = MAIL_USERNAME
MAIL_SERVER = os.environ.get('MAIL_SERVER')
MAIL_PORT = os.environ.get('MAIL_PORT')

# Geoserver
GEOSERVER_API_URL = os.environ.get('GEOSERVER_API_URL')
GEOSERVER_USER = os.environ.get('GEOSERVER_USER')
GEOSERVER_PASSWORD = os.environ.get('GEOSERVER_PASSWORD')

# Cors
CORS_HEADER_API_KEY = 'av7e7d78f93e2af'
CORS_ORIGIN = str(API_URL) + ':' + str(API_PORT)
CORS_CREDENTIALS = False
"""CORS_HEADERS = (
    CORS_HEADER_API_KEY,
    'X-Fields',
    'Content-Type',
    'Accept',
    'Accept-Charset',
    'Accept-Language',
    'Cache-Control',
    'Content-Encoding',
    'Content-Length',
    'Content-Security-Policy',
    'Content-Type',
    'Cookie',
    'ETag',
    'Host',
    'If-Modified-Since',
    'Keep-Alive',
    'Last-Modified',
    'Origin',
    'Referer',
    'User-Agent',
    'X-Forwarded-For',
    'X-Forwarded-Port',
    'X-Forwarded-Proto'
)"""

# SQLAlchemy settings
SQLALCHEMY_TRACK_MODIFICATIONS = False
CRS = 3035
CRS_USER_GEOMETRY = '4326'
CRS_NUTS = '4258'
CRS_LAU = '4326'

# Duration curve constants used in heat.load.profile.py
HOURS_PER_YEAR = 8760
LIMIT_VALUES_PER_NUTS = 4000
POINTS_FIRST_GROUP_PERCENTAGE = 0.0228
POINTS_SECOND_GROUP_PERCENTAGE = 0.1141
POINTS_THIRD_GROUP_PERCENTAGE = 0.7207
POINTS_FOURTH_GROUP_PERCENTAGE = 0.1424
POINTS_FIRST_GROUP_STEP = 12
POINTS_SECOND_GROUP_STEP = 40
POINTS_THIRD_GROUP_STEP = 134
POINTS_FOURTH_GROUP_STEP = 39
nuts3 = 'NUTS 3'
nuts2 = 'NUTS 2'
nuts1 = 'NUTS 1'
nuts0 = 'NUTS 0'
lau2 = 'LAU 2'
hectare_name = 'Hectare'
# heat load and duration curve data options
NUMBER_DECIMAL_DATA = 2
NUTS_LAU_VALUES = [nuts0,nuts1,nuts2,nuts3,lau2]
NUTS_VAlUES = [nuts0,nuts1,nuts2,nuts3]
LAU_TABLE= 'tbl_lau1_2'

NUTS_LAU_LEVELS = {nuts0:0,nuts1:1,nuts2:2,nuts3:3,lau2:4,hectare_name:5}
scale_level_loadprofile_aggreagtion = [nuts3,lau2]

USER_UPLOAD_FOLDER = os.environ.get('USER_UPLOAD_FOLDER')

UPLOAD_BASE_NAME = 'grey.tif'
UPLOAD_DIRECTORY = '/var/tmp'
DATASET_DIRECTORY = '/var/hotmaps/repositories/'

NUTS_YEAR = '2013'
LAU_YEAR = NUTS_YEAR