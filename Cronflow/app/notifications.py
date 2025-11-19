"""
Handles the sending of all outgoing notifications for the application.

This module is responsible for dispatching alerts when a job fails or is
missed. It is designed to be easily adaptable to different notification
services.

- `send_notification`: The main function that sends a message. It is currently
  configured to send alerts to Slack via an Incoming Webhook. The webhook URL
  is read securely from the `SLACK_WEBHOOK_URL` environment variable. If the
  variable is not set, it logs a warning and prints a fallback message.
"""
import os
import httpx
import logging

# Configure a logger for notifications
logger = logging.getLogger("notification_sender")
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - [NOTIFICATION] - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Get the Slack Webhook URL from environment variables.
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

def send_notification(message: str):
    """
    Sends a notification to a Slack webhook.
    
    Reads the webhook URL from the SLACK_WEBHOOK_URL environment variable.
    """
    if not SLACK_WEBHOOK_URL:
        logger.warning("SLACK_WEBHOOK_URL environment variable not set. Cannot send notification.")
        # Also print to console as a fallback
        logger.info(f"(Fallback) Notification: {message}")
        return

    payload = {"text": message}
    
    try:
        with httpx.Client() as client:
            response = client.post(SLACK_WEBHOOK_URL, json=payload)
            response.raise_for_status() # Raises an exception for 4XX/5XX responses
        logger.info("Successfully sent notification to Slack.")
    except httpx.RequestError as e:
        logger.error(f"Failed to send notification to Slack: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred while sending notification: {e}")
