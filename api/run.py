import os

from app import create_app
application = create_app(os.environ.get('FLASK_CONFIG', 'development'))

if __name__ == '__main__':
    application.run(host='0.0.0.0', threaded=True)
