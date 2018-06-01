import os
from flask_cors import CORS
from main_api import create_app, log

application = create_app(os.environ.get('FLASK_CONFIG', 'production'))
log.info(application)

if __name__ == "__main__":
    application.run()

