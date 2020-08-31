import os

from app import create_app, log
from app.model import init_sqlite_caculation_module_database

application = create_app(os.environ.get('ENVIRONMENT'))

if __name__ == '__main__':
    with application.app_context():
        init_sqlite_caculation_module_database()
    application.run(host='0.0.0.0', threaded=True)
