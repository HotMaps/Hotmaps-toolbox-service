#!/usr/bin/env python
import os
from app import celery, create_app

app = create_app(os.environ.get('FLASK_CONFIG', 'development'))
app.app_context().push()
