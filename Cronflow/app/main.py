"""
Main application file for the Cron Monitor.

This file initializes the FastAPI application and defines all the API endpoints
for interacting with the monitoring service. It handles:
- API endpoint routing (`/jobs`, `/jobs/{job_name}/<status>`).
- Database session management through a FastAPI dependency (`get_db`).
- Triggering notifications for failed jobs.
- Starting the background scheduler on application startup.
"""
from typing import List
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from . import models, schemas
from .database import SessionLocal, engine
from .scheduler import start_scheduler
from .notifications import send_notification

# Create the database tables on startup
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Cron Monitor",
    description="A service to monitor the status of cron jobs.",
    version="0.1.0",
)

@app.on_event("startup")
def startup_event():
    """
    On application startup, start the background scheduler.
    """
    start_scheduler()

# --- Dependency ---
def get_db():
    """
    FastAPI dependency to provide a database session per request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Helper Function ---
def update_job_status(job_name: str, status: schemas.JobStatus, db: Session):
    """
    Finds a job by name and updates its status.
    Triggers a notification on failure.
    """
    db_job = db.query(models.Job).filter(models.Job.name == job_name).first()
    if not db_job:
        raise HTTPException(status_code=404, detail=f"Job with name '{job_name}' not found.")
    
    db_job.status = status
    db.commit()
    db.refresh(db_job)

    if status == schemas.JobStatus.FAILURE:
        send_notification(f"Job '{job_name}' has failed.")

    return db_job

# --- API Endpoints ---

@app.get("/")
def read_root():
    """
    Root endpoint for the Cron Monitor API.
    """
    return {"message": "Cron Monitor is running. See /docs for API documentation."}

@app.post("/jobs", response_model=schemas.Job)
def create_job(job: schemas.JobCreate, db: Session = Depends(get_db)):
    """
    Register a new job to be monitored.
    """
    db_job = db.query(models.Job).filter(models.Job.name == job.name).first()
    if db_job:
        raise HTTPException(status_code=400, detail=f"Job with name '{job.name}' already registered.")
    
    new_job = models.Job(name=job.name, schedule=job.schedule)
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    return new_job

@app.get("/jobs", response_model=List[schemas.Job])
def read_jobs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve a list of all registered jobs.
    """
    jobs = db.query(models.Job).offset(skip).limit(limit).all()
    return jobs

@app.post("/jobs/{job_name}/start", response_model=schemas.Job)
def report_job_start(job_name: str, db: Session = Depends(get_db)):
    """
    Report that a job has started execution.
    """
    return update_job_status(job_name, schemas.JobStatus.RUNNING, db)

@app.post("/jobs/{job_name}/success", response_model=schemas.Job)
def report_job_success(job_name: str, db: Session = Depends(get_db)):
    """
    Report that a job has completed successfully.
    """
    return update_job_status(job_name, schemas.JobStatus.SUCCESS, db)

@app.post("/jobs/{job_name}/failure", response_model=schemas.Job)
def report_job_failure(job_name: str, db: Session = Depends(get_db)):
    """
    Report that a job has failed.
    """
    return update_job_status(job_name, schemas.JobStatus.FAILURE, db)
