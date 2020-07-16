#!/usr/bin/env bash

gnome-terminal -e "python producer_cm_alive.local.py" --title="HTAPI: producer_cm_alive"

gnome-terminal -e "python run.local.py" --title="HTAPI: run API"

gnome-terminal -e "python consumer_cm_register.local.py" --title="HTAPI: consumer_cm_register"

gnome-terminal -e "celery -A celery_worker_local.celery worker --loglevel=info" --title="HTAPI: celery3"
