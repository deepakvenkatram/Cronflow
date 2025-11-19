"""
Database configuration and session management for the application.

This file sets up the connection to the SQLite database using SQLAlchemy.
It defines:
- The database URL.
- The SQLAlchemy `engine` for connecting to the database.
- `SessionLocal`: A class used to create new database sessions for each request.
- `Base`: A declarative base class that all ORM models inherit from.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Define the database URL for SQLite.
# The database will be a single file named 'cron_monitor.db' in the project root.
DATABASE_URL = "sqlite:///./cron_monitor.db"

# Create the SQLAlchemy engine.
# The 'connect_args' are needed only for SQLite to allow multi-threaded access.
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create a SessionLocal class. Each instance of this class will be a database session.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a Base class. Our database model classes will inherit from this class.
Base = declarative_base()
