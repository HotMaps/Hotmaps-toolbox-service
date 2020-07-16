#!/usr/bin/env python

import os
from app import celery, create_app
from dotenv import load_dotenv
from pathlib import Path  
env_path = Path('../.env')
load_dotenv(dotenv_path=env_path)



app = create_app(os.environ.get('ENVIRONMENT'))
app.app_context().push()
