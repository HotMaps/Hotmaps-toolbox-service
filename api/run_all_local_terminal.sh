#!/usr/bin/env bash
TERM=gnome-terminal

$TERM -e "python producer_cm_alive.local.py" --title="HTAPI: producer_cm_alive"

$TERM -e "python run.local.py" --title="HTAPI: run API"

$TERM -e "python consumer_cm_register.local.py" --title="HTAPI: consumer_cm_register"

$TERM -e "celery -A celery_worker_local.celery worker --loglevel=info" --title="HTAPI: celery3"
