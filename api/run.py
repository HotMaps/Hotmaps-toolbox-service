import os

from app import create_app
from app import cm_models
application = create_app(os.environ.get('FLASK_CONFIG', 'development'))

if __name__ == '__main__':
    with application.app_context():
        cm_models.clean_cm_db()
    application.run(host='0.0.0.0', threaded=True)
