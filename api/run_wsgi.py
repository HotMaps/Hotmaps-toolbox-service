import os
from flask_cors import CORS
from app import create_app, log
from app.model import init_sqlite_caculation_module_database


application = create_app(os.environ.get('FLASK_CONFIG', 'development'))
log.info(application)
if __name__ == "__main__":

    #with application.app_context():
        #init_sqlite_caculation_module_database()



    application.run()

