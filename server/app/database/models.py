"""
Database Models - SQLAlchemy ORM
Based on Research Document Metrics Definition
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, Date, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()


class Organization(Base):
    """Organization model for tracking GitHub organizations"""
    __tablename__ = "organizations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    github_org = Column(String(255), unique=True, nullable=False)
    name = Column(String(255))
    total_seats = Column(Integer, default=0)
    copilot_seats = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    users = relationship("User", back_populates="organization")
    daily_metrics = relationship("DailyMetrics", back_populates="organization")


class User(Base):
    """User model with L0-L5 maturity levels"""
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
    maturity_level = Column(Integer, default=0)  # 0-5
    
    # Activity Status
    is_weekly_active = Column(Boolean, default=False)
    is_monthly_active = Column(Boolean, default=False)
    last_activity_date = Column(Date)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    organization = relationship("Organization", back_populates="users")
    activity_logs = relationship("UserActivityLog", back_populates="user")


class DailyMetrics(Base):
    """
    Daily aggregated metrics - combines Adoption, Productivity, Quality
    Based on Research Document Section 4
    """
    __tablename__ = "daily_metrics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    date = Column(Date, nullable=False)
    
    # === ADOPTION METRICS (Section 4.1) ===
    total_users = Column(Integer, default=0)
    enabled_users = Column(Integer, default=0)
    active_users = Column(Integer, default=0)
    weekly_active_users = Column(Integer, default=0)  # WAU
    monthly_active_users = Column(Integer, default=0)  # MAU
    activation_rate = Column(Float, default=0.0)  # (Active/Enabled) × 100
    prompts_per_user = Column(Float, default=0.0)  # Prompts per User/Week
    features_utilized = Column(Integer, default=0)  # Features Utilization
    team_activation_rate = Column(Float, default=0.0)  # Team Activation
    
    # Maturity Distribution (L0-L5)
    l0_count = Column(Integer, default=0)  # Not Enabled
    l1_count = Column(Integer, default=0)  # Enabled
    l2_count = Column(Integer, default=0)  # Active User
    l3_count = Column(Integer, default=0)  # Working User
    l4_count = Column(Integer, default=0)  # Consistent User
    l5_count = Column(Integer, default=0)  # Value User
    
    # === PRODUCTIVITY METRICS (Section 4.2) ===
    total_suggestions_shown = Column(Integer, default=0)
    total_suggestions_accepted = Column(Integer, default=0)
    acceptance_rate = Column(Float, default=0.0)  # Code Acceptance Rate
    total_lines_suggested = Column(Integer, default=0)
    total_lines_accepted = Column(Integer, default=0)
    total_chat_interactions = Column(Integer, default=0)
    
    # AI-Assisted Development
    ai_assisted_commits = Column(Integer, default=0)
    ai_assisted_prs = Column(Integer, default=0)
    total_commits = Column(Integer, default=0)
    total_prs = Column(Integer, default=0)
    ai_code_lines = Column(Integer, default=0)  # Lines of Code (AI)
    
    # Time Metrics
    avg_time_to_first_commit = Column(Float, default=0.0)  # Hours
    avg_pr_cycle_time = Column(Float, default=0.0)  # Hours
    
    # === QUALITY METRICS (Section 4.3) ===
    ai_code_retention_rate = Column(Float, default=0.0)  # Code Retention Rate
    ai_code_modification_rate = Column(Float, default=0.0)  # Modification Rate
    ai_code_bug_rate = Column(Float, default=0.0)  # Bug Rate (AI Code)
    pr_rejection_rate = Column(Float, default=0.0)  # PR Rejection Rate
    avg_review_comments = Column(Float, default=0.0)  # Code Review Feedback
    
    # Breakdown by Language/Editor
    language_breakdown = Column(JSON)  # {"python": 40, "javascript": 30, ...}
    editor_breakdown = Column(JSON)  # {"vscode": 80, "jetbrains": 20, ...}
    
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    organization = relationship("Organization", back_populates="daily_metrics")


class UserActivityLog(Base):
    """Individual user activity tracking"""
    __tablename__ = "user_activity_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(Date, nullable=False)
    
    # Usage Metrics
    suggestions_shown = Column(Integer, default=0)
    suggestions_accepted = Column(Integer, default=0)
    lines_suggested = Column(Integer, default=0)
    lines_accepted = Column(Integer, default=0)
    chat_interactions = Column(Integer, default=0)
    
    # Feature Usage
    features_used = Column(JSON)  # ["completions", "chat", "inline", ...]
    
    # Productivity
    commits_count = Column(Integer, default=0)
    ai_assisted_commits = Column(Integer, default=0)
    prs_created = Column(Integer, default=0)
    ai_assisted_prs = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    user = relationship("User", back_populates="activity_logs")


class KPI(Base):
    """
    KPI Tracking based on Phase Progression Model
    - Phase 1: Activation Rate target: 60%
    - Phase 2: Work Linkage target: 50%
    - Phase 3: Consistency Score target: 40%
    - Phase 4: KOIs Achieved target: 8+
    """
    __tablename__ = "kpis"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    category = Column(String(100))  # adoption, productivity, quality
    phase = Column(Integer)  # 1-4
    target_value = Column(Float)
    current_value = Column(Float)
    is_achieved = Column(Boolean, default=False)
    measurement_date = Column(Date)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
