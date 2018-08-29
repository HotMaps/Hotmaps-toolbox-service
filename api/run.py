import os

from app import create_app, log

application = create_app(os.environ.get('FLASK_CONFIG', 'development'))




if __name__ == '__main__':
    #with application.app_context():
        #init_sqlite_caculation_module_database()
    application.run(host='0.0.0.0')

