#!/bin/bash

echo "Starting the nightly backup script..."

# Simulate a process that can succeed or fail
# We'll generate a random number between 0 and 9
random_exit_code=$((RANDOM % 10))

# Let's say it fails 30% of the time (if the number is 0, 1, or 2)
if [ $random_exit_code -lt 3 ]; then
    echo "Backup failed! Could not connect to the remote server."
    exit 1
else
    echo "Backup completed successfully."
    exit 0
fi
