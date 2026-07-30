#!/bin/bash
# Start an RQ worker for the microblog-tasks queue.
# Override the broker with REDIS_URL, e.g. REDIS_URL=redis://redis:6379 ./start_worker.sh
set -e

cd "$(dirname "$0")"

export FLASK_APP=microblog.py
export REDIS_URL="${REDIS_URL:-redis://localhost:6379}"

echo "Connecting to Redis at $REDIS_URL"
exec rq worker --url "$REDIS_URL" microblog-tasks
