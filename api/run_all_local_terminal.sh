#!/usr/bin/env bash

sudo gnome-terminal -e "/home/albain/REPOSITORIES/Hotmaps-toolbox-service/.vscode/venv/bin/python producer_cm_alive.py" --title="HTAPI: producer_cm_alive"

sudo gnome-terminal -e "/home/albain/REPOSITORIES/Hotmaps-toolbox-service/.vscode/venv/bin/python run.py" --title="HTAPI: run API"

sudo gnome-terminal -e "/home/albain/REPOSITORIES/Hotmaps-toolbox-service/.vscode/venv/bin/python consumer_cm_register.py" --title="HTAPI: consumer_cm_register"

sudo gnome-terminal -e "/home/albain/REPOSITORIES/Hotmaps-toolbox-service/.vscode/venv/bin/celery -A celery_worker.celery worker --loglevel=info" --title="HTAPI: celery3"