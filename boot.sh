#!/bin/bash
set -e

# The database container may not accept connections yet when the web container
# starts, so retry the migration until it succeeds.
until flask db upgrade; do
    echo "Migration failed, retrying in 5 seconds..."
    sleep 5
done

exec gunicorn -b :5000 --access-logfile - --error-logfile - microblog:app
