#!/usr/bin/env bash

sudo gnome-terminal -e "python3 producer_cm_alive.py" --title="HTAPI: producer_cm_alive"

sudo gnome-terminal -e "python3 run.py" --title="HTAPI: run API"

sudo gnome-terminal -e "python3 consumer_cm_register.py" --title="HTAPI: consumer_cm_register"

sudo gnome-terminal -e "celery -A celery_worker.celery worker --loglevel=info" --title="HTAPI: celery3"
