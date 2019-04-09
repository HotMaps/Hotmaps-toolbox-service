REM CALL ..\.vscode\venv\Scripts\activate 
start /MAX "Producer" python producer_cm_alive.py
start /MAX "API" python run.py
REM start /MAX "Consumer" python consumer_cm_register.py
start /MAX "Celery" celery -A celery_worker.celery worker --loglevel=info