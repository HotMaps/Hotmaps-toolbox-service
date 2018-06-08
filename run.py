import os
from flask_cors import CORS
from app import create_app
if __name__ == "__main__":
    app = create_app(os.environ.get('FLASK_CONFIG', 'development'))
    app.run()

