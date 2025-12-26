#!/bin/bash
while true; do
# Run the database migration command
    flask db upgrade
    # Check if the command was successful
    if [[ "$?" == "0" ]]; then
    # If successful, exit the loop
        break
    fi # If not successful, wait for 5 seconds before retrying
    echo Upgrade command failed, retrying in 5 seconds...
    sleep 5 # Wait for 5 seconds before retrying
done
# Now start the Gunicorn server
exec gunicorn -b :5000 --access-logfile - --error-logfile - microblog:app