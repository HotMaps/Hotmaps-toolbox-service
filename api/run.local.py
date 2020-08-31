import os
from pathlib import Path

from app import create_app, log
from app.model import init_sqlite_caculation_module_database
from dotenv import load_dotenv

env_path = Path('../.env')
load_dotenv(dotenv_path=env_path)



application = create_app(os.environ.get('ENVIRONMENT'))

if __name__ == '__main__':
    with application.app_context():
        init_sqlite_caculation_module_database()
    application.run(host='0.0.0.0', threaded=True)
