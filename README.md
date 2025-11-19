<img alt="gitleaks badge" src="https://img.shields.io/badge/protected%20by-gitleaks-blue"> ![Static Badge](https://img.shields.io/badge/Devops-Deepak%20Venkatram-Green)

# Cronflow

A simple, self-hosted service to monitor cron jobs for success, failure, and missed executions, with real-time notifications sent to Slack.

This project provides a central API endpoint that your cron jobs can ping. If a job fails to report in, runs into an error, or is missed entirely according to its schedule, the service will send an alert to a configured Slack channel.

## Features

- **Simple REST API**: Register jobs and receive status updates (`start`, `success`, `failure`).
- **Universal Wrapper Script**: Easily wrap any existing cron job with a simple Bash script without modifying its core logic.
- **Missed Job Detection**: A background scheduler runs every minute to check if any job missed its scheduled execution time.
- **Slack Notifications**: Get immediate alerts in Slack for failed or missed jobs.
- **Lightweight and Self-Contained**: Built with Python, FastAPI, and SQLite, requiring minimal setup.

## Tech Stack

- **Backend**: Python with [FastAPI](https://fastapi.tiangolo.com/)
- **Database**: [SQLite](https://www.sqlite.org/index.html)
- **Scheduling**: [APScheduler](https://apscheduler.readthedocs.io/en/3.x/)
- **Cron Parsing**: [croniter](https://github.com/kiorky/croniter)

---

## Setup and Installation

Follow these steps to get the Cron Monitor running locally.

### 1. Clone the Repository

bash
git clone [<your-repository-url>](https://github.com/deepakvenkatram/Cronflow.git)
cd cronflow


### 2. Create a Virtual Environment

It's highly recommended to use a virtual environment to manage dependencies.

# Create the virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

### 3. Install Dependencies

Install all the required Python packages.

pip install -r requirements.txt

### 4. Create a Slack Incoming Webhook

You need a Slack Incoming Webhook URL to receive notifications. This is free and easy to create.

1.  **Go to the Slack API website**: Navigate to [api.slack.com/apps](https://api.slack.com/apps).
2.  **Create a New App**:
    *   Click **"Create New App"**.
    *   Choose **"From scratch"**.
    *   Give your app a name (e.g., "Cron Job Monitor") and select the Slack workspace you want to post notifications to.
    *   Click **"Create App"**.
3.  **Enable Incoming Webhooks**:
    *   On the next screen, under "Add features and functionality", click on **"Incoming Webhooks"**.
    *   Toggle the switch to **"On"**.
4.  **Create a Webhook for a Channel**:
    *   Scroll down and click **"Add New Webhook to Workspace"**.
    *   Choose the channel where you want notifications to be sent (e.g., `#alerts`, `#devops`).
    *   Click **"Allow"**.
5.  **Copy the Webhook URL**:
    *   You will be redirected back to the webhook settings page. A new webhook URL will appear in the table.
    *   Click **"Copy"**. This is your webhook URL. Keep it safe.

### 5. Set the Environment Variable

The application reads the Slack URL from an environment variable for security. **Do not hard-code this URL in the source code.**

In your terminal, run the following command, pasting your new webhook URL:

export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/NEW/URL"

### 6. Run the Application

You can now start the monitoring service using `uvicorn`.

uvicorn app.main:app --reload

The server will start on `http://127.0.0.1:8000`. You can view the interactive API documentation at `http://127.0.0.1:8000/docs`.

---

## Usage

### 1. Register a Job

First, you must register the job you want to monitor with the service. Send a `POST` request to the `/jobs` endpoint with the job's unique name and its cron schedule.

curl -X POST "http://127.0.0.1:8000/jobs" \ -H "Content-Type: application/json" -d '{"name": "daily-database-backup", "schedule": "0 2 * * *"}'

### 2. Wrap Your Cron Job

Modify your crontab to use the `scripts/monitor.sh` wrapper. The wrapper takes two arguments: the `job-name` you just registered and the actual command to run.

**Before:**

crontab
# This script runs every day at 2 AM.
0 2 * * * /home/user/scripts/backup_database.sh

**After:**

crontab
# The wrapper now monitors the script.
0 2 * * * /path/to/your/cron-moniter/scripts/monitor.sh "daily-database-backup" /home/user/scripts/backup_database.sh

### How the Wrapper Works

The `monitor.sh` script will:
1.  Send a `start` ping to the API.
2.  Execute your original command (`/home/user/scripts/backup_database.sh`).
3.  Based on your script's exit code, it will send a `success` (if exit code is 0) or `failure` ping to the API.

If the job fails or if it doesn't run at its scheduled time of 2 AM, the service will send a notification to your Slack channel.
