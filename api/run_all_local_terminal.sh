#!/usr/bin/env bash

sudo gnome-terminal -e "bash -c 'python producer_cm_alive.py; read line'" --title="HTAPI: producer_cm_alive"

sudo gnome-terminal -e "bash -c 'python run.py; read line'" --title="HTAPI: run API"

sudo gnome-terminal -e "bash -c 'python consumer_cm_register.py; read line'" --title="HTAPI: consumer_cm_register"

sudo gnome-terminal -e "bash -c 'celery -A celery_worker.celery worker --loglevel=info --concurrency=10 -n worker3@%; read line'" --title="HTAPI: celery3"

sudo gnome-terminal -e "bash -c 'celery -A celery_worker.celery worker --loglevel=info --concurrency=10 -n worker2@%h; read line'" --title="HTAPI: celery2"

sudo gnome-terminal -e "bash -c 'celery -A celery_worker.celery worker --loglevel=info --concurrency=10 -n worker1@%h; read line'" --title="HTAPI: celery1"
