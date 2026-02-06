"""
POC 1: AI Adoption Metrics Dashboard
Database Models

SQLAlchemy models for storing metrics data.
"""

from datetime import datetime, date
from typing import Optional
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Date, Boolean, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.pool import StaticPool

Base = declarative_base()


class Organization(Base):
    """Organization/Team information."""
    __tablename__ = "organizations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    github_org = Column(String(255), unique=True, nullable=False)
    name = Column(String(255))
    total_seats = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = relationship("User", back_populates="organization")
    daily_metrics = relationship("DailyMetrics", back_populates="organization")


class User(Base):
    """User/Engineer information."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    github_username = Column(String(255), unique=True, nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    email = Column(String(255))
    name = Column(String(255))
    team = Column(String(255))
    
    # Copilot Status
    copilot_enabled = Column(Boolean, default=False)
    copilot_enabled_date = Column(Date)
    
    # Maturity Level (L0-L5)
    maturity_level = Column(Integer, default=0)
    
    # Activity Status
    is_weekly_active = Column(Boolean, default=False)
    is_monthly_active = Column(Boolean, default=False)
    last_activity_date = Column(Date)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization", back_populates="users")
    activity_logs = relationship("UserActivityLog", back_populates="user")
    

class DailyMetrics(Base):
    """Daily aggregated metrics for the organization."""
    __tablename__ = "daily_metrics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    date = Column(Date, nullable=False)
    
    # Adoption Metrics
    total_users = Column(Integer, default=0)
    enabled_users = Column(Integer, default=0)
    active_users = Column(Integer, default=0)
    weekly_active_users = Column(Integer, default=0)
    monthly_active_users = Column(Integer, default=0)
    
    # Copilot Usage Metrics
    total_suggestions_shown = Column(Integer, default=0)
    total_suggestions_accepted = Column(Integer, default=0)
    total_lines_suggested = Column(Integer, default=0)
    total_lines_accepted = Column(Integer, default=0)
    total_chat_interactions = Column(Integer, default=0)
    
    # Calculated Rates
    acceptance_rate = Column(Float, default=0.0)
    activation_rate = Column(Float, default=0.0)
    
    # Productivity Metrics (from MCP/Git)
    ai_assisted_commits = Column(Integer, default=0)
    ai_assisted_prs = Column(Integer, default=0)
    total_commits = Column(Integer, default=0)
    total_prs = Column(Integer, default=0)
    
    # Quality Metrics
    ai_code_lines = Column(Integer, default=0)
    ai_code_modified = Column(Integer, default=0)
    ai_code_retention_rate = Column(Float, default=0.0)
    
    # Maturity Distribution
    l0_count = Column(Integer, default=0)
    l1_count = Column(Integer, default=0)
    l2_count = Column(Integer, default=0)
    l3_count = Column(Integer, default=0)
    l4_count = Column(Integer, default=0)
    l5_count = Column(Integer, default=0)
    
    # Language Breakdown (JSON)
    language_breakdown = Column(JSON)
    
    # Editor Breakdown (JSON)
    editor_breakdown = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization", back_populates="daily_metrics")


class UserActivityLog(Base):
    """Individual user activity log."""
    __tablename__ = "user_activity_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(Date, nullable=False)
    
    # Daily Activity
    suggestions_shown = Column(Integer, default=0)
    suggestions_accepted = Column(Integer, default=0)
    lines_suggested = Column(Integer, default=0)
    lines_accepted = Column(Integer, default=0)
    chat_interactions = Column(Integer, default=0)
    
    # Features Used (JSON list)
    features_used = Column(JSON)
    
    # Productivity
    commits_count = Column(Integer, default=0)
    ai_assisted_commits = Column(Integer, default=0)
    prs_created = Column(Integer, default=0)
    ai_assisted_prs = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="activity_logs")


class MCPEvent(Base):
    """MCP Server events for tracking AI-assisted actions."""
    __tablename__ = "mcp_events"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    event_type = Column(String(100), nullable=False)  # commit, pr, branch, etc.
    github_username = Column(String(255))
    repository = Column(String(255))
    
    # Event Details
    event_data = Column(JSON)
    
    # Timestamps
    event_timestamp = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class CodeQualityMetric(Base):
    """Code quality tracking for AI-generated code."""
    __tablename__ = "code_quality_metrics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    repository = Column(String(255), nullable=False)
    commit_sha = Column(String(40))
    file_path = Column(Text)
    
    # Code Attribution
    is_ai_generated = Column(Boolean, default=False)
    ai_lines_original = Column(Integer, default=0)
    
    # Quality Tracking
    lines_modified = Column(Integer, default=0)
    modification_date = Column(Date)
    days_until_modification = Column(Integer)
    modification_reason = Column(String(100))  # bug_fix, refactor, feature, etc.
    
    created_at = Column(DateTime, default=datetime.utcnow)


class KPI(Base):
    """Key Performance Indicators tracking."""
    __tablename__ = "kpis"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    category = Column(String(100))  # adoption, productivity, quality
    
    # Target and Current
    target_value = Column(Float)
    current_value = Column(Float)
    
    # Status
    is_achieved = Column(Boolean, default=False)
    
    # Dates
    measurement_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
