#!/bin/bash

# A script to check the disk space of the root filesystem (/).
# It fails if the usage percentage is above a defined threshold.

# --- Configuration ---
# Set the threshold (e.g., 90 for 90%).
THRESHOLD=0

# --- Main Logic ---
echo "Checking disk space for the root filesystem (/). Threshold: ${THRESHOLD}%"

# Get the current usage percentage of the root filesystem.
# - `df /`: Gets disk usage for the root filesystem.
# - `tail -n 1`: Gets the last line of the output, which is the data.
# - `awk '{print $5}'`: Gets the 5th column (the percentage value like "56%").
# - `sed 's/%//'`: Removes the '%' character.
CURRENT_USAGE=$(df / | tail -n 1 | awk '{print $5}' | sed 's/%//')

echo "Current usage is: ${CURRENT_USAGE}%"

# Compare current usage with the threshold.
if [ "$CURRENT_USAGE" -gt "$THRESHOLD" ]; then
    echo "Alert: Disk usage (${CURRENT_USAGE}%) is above the threshold of ${THRESHOLD}%."
    exit 1
else
    echo "OK: Disk usage is within the acceptable range."
    exit 0
fi
