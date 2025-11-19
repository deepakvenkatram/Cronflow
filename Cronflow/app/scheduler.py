"""
Background scheduler for detecting missed cron jobs.

This module uses APScheduler to run a periodic task that checks for jobs
that have missed their scheduled execution time.

- `check_missed_jobs`: This function is run every minute. It queries the
  database for all jobs with a schedule, uses `croniter` to determine the
  last expected run time, and compares it with the last actual run time.
  If a job was expected to run but didn't, its status is updated to 'missed'
  and a notification is triggered.
- `start_scheduler`: This function initializes and starts the global scheduler.
  It is called once on application startup from `main.py`.
"""
import logging
from datetime import datetime, timezone
from apscheduler.schedulers.background import BackgroundScheduler
from croniter import croniter

from .database import SessionLocal
from .models import Job, JobStatus
from .notifications import send_notification

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_missed_jobs():
    """
    Iterates through all jobs with a schedule and checks if any were missed.
    A job is considered missed if its most recent scheduled run time has passed
    without the job's status being updated.
    """
    db = SessionLocal()
    try:
        logger.info("Scheduler running: Checking for missed jobs...")
        jobs_with_schedule = db.query(Job).filter(Job.schedule.isnot(None)).all()
        
        now = datetime.now(timezone.utc)

        for job in jobs_with_schedule:
            # Ensure job.last_run is timezone-aware for correct comparison
            last_run_aware = job.last_run.astimezone(timezone.utc) if job.last_run.tzinfo else job.last_run.replace(tzinfo=timezone.utc)

            # Find the last time the job was supposed to run before 'now'
            cron = croniter(job.schedule, now)
            expected_last_run = cron.get_prev(datetime)

            # If the expected run time is more recent than the last actual run time,
            # and the job isn't currently running, it means a run was missed.
            if expected_last_run > last_run_aware and job.status != JobStatus.RUNNING:
                if job.status != JobStatus.MISSED: # Avoid sending repeated notifications
                    logger.warning(
                        f"Job '{job.name}' was missed. "
                        f"Last actual run: {last_run_aware.isoformat()}, "
                        f"Last expected run: {expected_last_run.isoformat()}"
                    )
                    job.status = JobStatus.MISSED
                    send_notification(f"Job '{job.name}' has been missed.")
        
        db.commit()
        logger.info("Scheduler check finished.")
    except Exception as e:
        logger.error(f"Error in scheduler when checking for missed jobs: {e}", exc_info=True)
        db.rollback()
    finally:
        db.close()


def start_scheduler():
    """
    Initializes and starts the background scheduler.
    """
    scheduler = BackgroundScheduler(timezone=timezone.utc)
    # Schedule the job check to run every minute
    scheduler.add_job(check_missed_jobs, 'interval', minutes=1, id="missed_job_check")
    scheduler.start()
    logger.info("Background scheduler started.")
