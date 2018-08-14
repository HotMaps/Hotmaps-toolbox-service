#!/bin/bash

# Start the first  => process Run the API
gunicorn -b 0.0.0.0:5000 --access-logfile - "run:application" -D
status=$?
if [ $status -ne 0 ]; then
  echo "Failed to start the API: $status"
  exit $status
fi
# Start the second process => run the register queue
python consumer_cm_register.py -D
status=$?
if [ $status -ne 0 ]; then
  echo "Failed to start Register queue: $status"
  exit $status
fi
# Start the third process  => run the calculation alive verification
python producer_cm_alive.py -D
status=$?
if [ $status -ne 0 ]; then
  echo "Failed to start Producer Alive checking : $status"
  exit $status
fi


# Naive check runs checks once a minute to see if either of the processes exited.
# This illustrates part of the heavy lifting you need to do if you want to run
# more than one service in a container. The container exits with an error
# if it detects that either of the processes has exited.
# Otherwise it loops forever, waking up every 60 seconds

while sleep 60; do
  ps aux |grep gunicorn -b 0.0.0.0:5000 --access-logfile - "run:application" |grep -q -v grep
  PROCESS_1_STATUS=$?
  ps aux |grep python consumer_cm_register.py |grep -q -v grep
  PROCESS_2_STATUS=$?
  ps aux |grep python producer_cm_alive.py |grep -q -v grep
  PROCESS_3_STATUS=$?
  # If the greps above find anything, they exit with 0 status
  # If they are not both 0, then something is wrong
  if [ $PROCESS_1_STATUS -ne 0 ]; then
    echo "run api process has already exited."
    exit 1
  fi
  if [ $PROCESS_2_STATUS -ne 0 ]; then
    echo "register queue process has already exited."
    exit 1
  fi
  if [ $PROCESS_3_STATUS -ne 0 ]; then
    echo "calculation alive verification process has already exited."
    exit 1
  fi
done

