"""
SQLAlchemy ORM models for the application.

This file defines the database schema using SQLAlchemy's declarative base.
Each class here represents a table in the database.

- `JobStatus`: An enumeration that defines the possible states of a cron job.
- `Job`: The main table for the application, storing all information about a
  monitored cron job, including its name, schedule, status, and timestamps.
"""
import enum
from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLAlchemyEnum
from sqlalchemy.sql import func
from .database import Base

class JobStatus(str, enum.Enum):
    """
    Enumeration for the status of a cron job.
    """
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILURE = "failure"
    MISSED = "missed"

class Job(Base):
    """
    Database model for a monitored cron job.
    """
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    schedule = Column(String, nullable=True)
    status = Column(SQLAlchemyEnum(JobStatus), default=JobStatus.PENDING, nullable=False)
    last_run = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Job(name='{self.name}', status='{self.status}')>"
