DEBUG = False


SECRET_KEY = 'top-secret!'
# Flask settings
FLASK_SECRET_KEY = 'paPTvnNME5NBHHuIOlFqG6zS77vHadbo'

SQLALCHEMY_DATABASE_URI = 'postgresql://hotmaps:Dractwatha9@hotmaps.hevs.ch:32768/toolboxdb'
DEBUG = True
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