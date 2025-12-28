#!/bin/bash
cd /mnt/c/Users/User/OneDrive/Documents/MicroBlog

# Use the existing venv (not venv-wsl)
source venv/bin/activate

export FLASK_APP=microblog.py

# Fix: Use default gateway, not DNS servers
WINDOWS_IP=$(ip route show | grep -i default | awk '{ print $3}')
export REDIS_URL=redis://$WINDOWS_IP:6379

echo "Windows IP: $WINDOWS_IP"
echo "Connecting to Redis at: $REDIS_URL"

# Test connection first
echo "Testing Redis connection..."
redis-cli -h $WINDOWS_IP ping

if [ $? -eq 0 ]; then
    echo "Redis connection successful!"
    echo "Starting RQ worker..."
    rq worker microblog-tasks
else
    echo "ERROR: Cannot connect to Redis at $WINDOWS_IP:6379"
    exit 1
fi