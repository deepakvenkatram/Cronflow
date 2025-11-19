#!/bin/bash

# A wrapper script to monitor the execution of a cron job.
#
# Usage:
# ./monitor.sh "my-job-name" /path/to/your/command --with --args
#
# It sends a 'start' signal to the monitoring API, runs the command,
# and then sends a 'success' or 'failure' signal based on the command's exit code.

set -eo pipefail

# --- Configuration ---
# The base URL of the monitoring API.
# This will be replaced with your actual server address.
API_URL="http://127.0.0.1:8000"

# --- Script Arguments ---
# The first argument is the unique name for the job.
JOB_NAME="$1"
shift

# The rest of the arguments form the actual command to execute.
COMMAND_TO_RUN=($@)

# --- Helper Functions ---
send_ping() {
    local status="$1"
    local url="${API_URL}/jobs/${JOB_NAME}/${status}"
    echo "Pinging: ${url}"
    # The -sS flags make curl silent but show errors.
    # The --fail flag makes curl exit with an error code if the server returns an error (>=400).
    curl -sS --fail -X POST "${url}" || echo "Warning: Failed to ping monitoring API at ${url}"
}

# --- Main Execution ---
if [[ -z "$JOB_NAME" ]] || [[ ${#COMMAND_TO_RUN[@]} -eq 0 ]]; then
    echo "Error: Missing arguments."
    echo "Usage: $0 \"<job-name>\" <command-to-run...>"
    exit 1
fi

# 1. Send 'start' ping
send_ping "start"

# 2. Execute the actual command
echo "Running command: ${COMMAND_TO_RUN[*]}"
# The `exit_code` is captured for the final status ping.
# We use `set +e` to prevent the script from exiting immediately if the command fails.
set +e
"${COMMAND_TO_RUN[@]}"
exit_code=$?
set -e
echo "Command finished with exit code: ${exit_code}"

# 3. Send 'success' or 'failure' ping based on the exit code
if [[ $exit_code -eq 0 ]]; then
    send_ping "success"
else
    send_ping "failure"
fi

# Exit with the original command's exit code
exit $exit_code
