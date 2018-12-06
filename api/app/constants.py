# Flask settings
#FLASK_SERVER_NAME = '0.0.0.0:80'
FLASK_SERVER_NAME = '0.0.0.0:5556'
FLASK_DEBUG = False  # Do not use debug mode in production
CELERY_BROKER_URL_DOCKER= 'amqp://admin:mypass@rabbit:5672/'
CELERY_BROKER_URL_LOCAL  = 'amqp://localhost/'
CELERY_BROKER_URL = CELERY_BROKER_URL_LOCAL
CELERY_ALWAYS_EAGER = False
CELERY_RESULT_BACKEND = 'redis://localhost:6379'
RPC_Q = 'rpc_queue_CM_compute'
TIMEOUT_ALIVE_CM = 3
TIMEOUT_START_CM = 1
TIMEOUT_DELETE_CM= 15
RPC_CM_ALIVE= 'rpc_queue_CM_ALIVE'
PORT_LOCAL = 5000
PORT_DOCKER = 80
CM_REGISTER_Q = 'rpc_queue_CM_register'
PORT = PORT_LOCAL
CM_DB_NAME = "calculation_module.db"
# Flask-Restplus settings
RESTPLUS_SWAGGER_UI_DOC_EXPANSION = 'list'
RESTPLUS_VALIDATE = True
RESTPLUS_MASK_SWAGGER = False
RESTPLUS_ERROR_404_HELP = False
RESTPLUS_JSON = {
    'separators': (',', ':')
}

CORS_HEADER_API_KEY = 'av7e7d78f93e2af'
CORS_ORIGIN = 'http://hotmaps.hevs.ch'
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

