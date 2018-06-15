DEBUG = False
import os

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, '../data.sqlite')
from app import secrets
SECRET_KEY = 'top-secret!'
# Flask settings
FLASK_SECRET_KEY = 'paPTvnNME5NBHHuIOlFqG6zS77vHadbo'

SQLALCHEMY_DATABASE_URI = secrets.SQLALCHEMY_DATABASE_URI_PRODUCTION
SQLALCHEMY_BINDS = {
    'cm_db':      os.environ.get('DATABASE_URL') or \
                    'sqlite:///' + db_path
}
#flask_app.config['SERVER_NAME'] = settings.FLASK_SERVER_NAME
SECRET_KEY = 'paPTvnNME5NBHHuIOlFqG6zS77vHadbo'
SQLALCHEMY_TRACK_MODIFICATIONS = True
SWAGGER_UI_DOC_EXPANSION = 'list'
RESTPLUS_VALIDATE = True
RESTPLUS_MASK_SWAGGER = False
ERROR_404_HELP = False
RESTPLUS_JSON = {
    'separators': (',', ':')
}
CELERY_BROKER_URL = 'amqp://localhost//'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'