#!/bin/sh

# Check if endpoint_checker.log exists as a directory and remove it
if [ -d "/app/endpoint_checker.log" ]; then
  rm -rf /app/endpoint_checker.log
fi

# Create the log file with proper permissions
touch /app/endpoint_checker.log
chmod 666 /app/endpoint_checker.log

# Run the main application
exec "$@"
