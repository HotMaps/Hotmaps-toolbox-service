import os
from flask_cors import CORS
from app import create_app,dbCM as db, log

application = create_app(os.environ.get('FLASK_CONFIG', 'development'))
log.info(application)
if __name__ == "__main__":
    with application.app_context():
        db.create_all(bind='cm_db')

    application.run()

