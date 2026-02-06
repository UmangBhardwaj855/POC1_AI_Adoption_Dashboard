"""
POC 1: AI Adoption Metrics Dashboard
Database Connection and Session Management
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
from pathlib import Path
import os

from .models import Base
from ..config.settings import settings


def get_engine():
    """Create database engine based on configuration."""
    database_url = settings.database_url
    
    # SQLite
    if database_url.startswith("sqlite"):
        db_path = database_url.replace("sqlite:///", "")
        if db_path.startswith("./"):
            db_path = db_path[2:]
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        return create_engine(
            database_url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=settings.dashboard_debug
        )
    
    # MySQL
    if database_url.startswith("mysql"):
        return create_engine(
            database_url,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=settings.dashboard_debug
        )
    
    # PostgreSQL or other databases
    return create_engine(
        database_url,
        pool_pre_ping=True,
        echo=settings.dashboard_debug
    )


# Create engine and session factory
engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_database():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized successfully!")


def drop_database():
    """Drop all database tables (use with caution!)."""
    Base.metadata.drop_all(bind=engine)
    print("⚠️ All database tables dropped!")


@contextmanager
def get_db_session() -> Session:
    """Context manager for database sessions."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def get_db():
    """Dependency for FastAPI endpoints."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
