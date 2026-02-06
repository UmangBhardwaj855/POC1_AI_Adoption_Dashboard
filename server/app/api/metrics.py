"""
Metrics API Endpoints
Daily metrics management for Adoption, Productivity, Quality
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
from typing import Optional, List
from pydantic import BaseModel

from app.database.connection import get_db
from app.database.models import DailyMetrics

router = APIRouter()


class MetricsCreate(BaseModel):
    organization_id: int
    date: date
    # Adoption
    total_users: Optional[int] = 0
    enabled_users: Optional[int] = 0
    active_users: Optional[int] = 0
    weekly_active_users: Optional[int] = 0
    monthly_active_users: Optional[int] = 0
    activation_rate: Optional[float] = 0.0
    prompts_per_user: Optional[float] = 0.0
    features_utilized: Optional[int] = 0
    team_activation_rate: Optional[float] = 0.0
    # Maturity
    l0_count: Optional[int] = 0
    l1_count: Optional[int] = 0
    l2_count: Optional[int] = 0
    l3_count: Optional[int] = 0
    l4_count: Optional[int] = 0
    l5_count: Optional[int] = 0
    # Productivity
    total_suggestions_shown: Optional[int] = 0
    total_suggestions_accepted: Optional[int] = 0
    acceptance_rate: Optional[float] = 0.0
    total_lines_suggested: Optional[int] = 0
    total_lines_accepted: Optional[int] = 0
    total_chat_interactions: Optional[int] = 0
    ai_assisted_commits: Optional[int] = 0
    ai_assisted_prs: Optional[int] = 0
    total_commits: Optional[int] = 0
    total_prs: Optional[int] = 0
    ai_code_lines: Optional[int] = 0
    # Quality
    ai_code_retention_rate: Optional[float] = 0.0
    ai_code_modification_rate: Optional[float] = 0.0
    ai_code_bug_rate: Optional[float] = 0.0
    pr_rejection_rate: Optional[float] = 0.0


class MetricsResponse(BaseModel):
    id: int
    organization_id: Optional[int]
    date: date
    # All fields...
    total_users: Optional[int]
    enabled_users: Optional[int]
    active_users: Optional[int]
    acceptance_rate: Optional[float]
    activation_rate: Optional[float]
    l0_count: Optional[int]
    l1_count: Optional[int]
    l2_count: Optional[int]
    l3_count: Optional[int]
    l4_count: Optional[int]
    l5_count: Optional[int]
    
    class Config:
        from_attributes = True


@router.get("")
def get_metrics(
    days: int = 30,
    org_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get daily metrics for the specified period"""
    start_date = date.today() - timedelta(days=days)
    
    query = db.query(DailyMetrics).filter(DailyMetrics.date >= start_date)
    if org_id:
        query = query.filter(DailyMetrics.organization_id == org_id)
    
    return query.order_by(DailyMetrics.date.desc()).all()


@router.get("/latest")
def get_latest_metrics(
    org_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get the most recent metrics"""
    query = db.query(DailyMetrics).order_by(DailyMetrics.date.desc())
    if org_id:
        query = query.filter(DailyMetrics.organization_id == org_id)
    
    metrics = query.first()
    if not metrics:
        raise HTTPException(status_code=404, detail="No metrics found")
    
    return metrics


@router.post("")
def create_metrics(metrics: MetricsCreate, db: Session = Depends(get_db)):
    """Create new daily metrics record"""
    # Check if metrics already exist for this date
    existing = db.query(DailyMetrics).filter(
        DailyMetrics.organization_id == metrics.organization_id,
        DailyMetrics.date == metrics.date
    ).first()
    
    if existing:
        # Update existing record
        for key, value in metrics.model_dump().items():
            setattr(existing, key, value)
        db.commit()
        db.refresh(existing)
        return existing
    
    # Create new record
    db_metrics = DailyMetrics(**metrics.model_dump(), created_at=datetime.now())
    db.add(db_metrics)
    db.commit()
    db.refresh(db_metrics)
    return db_metrics


@router.get("/adoption")
def get_adoption_metrics(
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get adoption-specific metrics trends"""
    start_date = date.today() - timedelta(days=days)
    
    metrics = db.query(DailyMetrics).filter(
        DailyMetrics.date >= start_date
    ).order_by(DailyMetrics.date).all()
    
    if not metrics:
        return {"summary": {}, "trends": []}
    
    # Calculate summary from latest metrics
    latest = metrics[-1] if metrics else None
    total_prompts = sum(m.prompts_per_user or 0 for m in metrics)
    
    summary = {
        "wau": latest.weekly_active_users if latest else 0,
        "mau": latest.monthly_active_users if latest else 0,
        "activation_rate": latest.activation_rate if latest else 0,
        "avg_prompts_per_user": total_prompts / len(metrics) if metrics else 0,
        "total_users": latest.total_users if latest else 0,
        "enabled_users": latest.enabled_users if latest else 0,
    }
    
    trends = [
        {
            "date": m.date.strftime("%b %d"),
            "active_users": m.active_users or 0,
            "prompts": int(m.prompts_per_user or 0),
            "suggestions": m.total_suggestions_shown or 0,
            "activation_rate": m.activation_rate or 0,
        }
        for m in metrics
    ]
    
    return {"summary": summary, "trends": trends}


@router.get("/productivity")
def get_productivity_metrics(
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get productivity-specific metrics trends"""
    start_date = date.today() - timedelta(days=days)
    
    metrics = db.query(DailyMetrics).filter(
        DailyMetrics.date >= start_date
    ).order_by(DailyMetrics.date).all()
    
    if not metrics:
        return {"summary": {}, "trends": []}
    
    # Calculate summary totals
    total_ai_commits = sum(m.ai_assisted_commits or 0 for m in metrics)
    total_ai_prs = sum(m.ai_assisted_prs or 0 for m in metrics)
    total_lines = sum(m.ai_code_lines or 0 for m in metrics)
    avg_acceptance = sum(m.acceptance_rate or 0 for m in metrics) / len(metrics) if metrics else 0
    
    summary = {
        "total_ai_commits": total_ai_commits,
        "total_ai_prs": total_ai_prs,
        "avg_acceptance_rate": avg_acceptance,
        "total_lines_generated": total_lines,
        "total_suggestions": sum(m.total_suggestions_shown or 0 for m in metrics),
        "total_accepted": sum(m.total_suggestions_accepted or 0 for m in metrics),
    }
    
    trends = [
        {
            "date": m.date.strftime("%b %d"),
            "suggestions_shown": m.total_suggestions_shown or 0,
            "suggestions_accepted": m.total_suggestions_accepted or 0,
            "acceptance_rate": m.acceptance_rate or 0,
            "ai_commits": m.ai_assisted_commits or 0,
            "ai_prs": m.ai_assisted_prs or 0,
            "lines_generated": m.ai_code_lines or 0,
        }
        for m in metrics
    ]
    
    return {"summary": summary, "trends": trends}


@router.get("/quality")
def get_quality_metrics(
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get quality-specific metrics trends"""
    start_date = date.today() - timedelta(days=days)
    
    metrics = db.query(DailyMetrics).filter(
        DailyMetrics.date >= start_date
    ).order_by(DailyMetrics.date).all()
    
    if not metrics:
        return {"summary": {}, "trends": []}
    
    # Calculate summary averages
    avg_retention = sum(m.ai_code_retention_rate or 0 for m in metrics) / len(metrics) if metrics else 0
    avg_modification = sum(m.ai_code_modification_rate or 0 for m in metrics) / len(metrics) if metrics else 0
    avg_bug_rate = sum(m.ai_code_bug_rate or 0 for m in metrics) / len(metrics) if metrics else 0
    avg_pr_rejection = sum(m.pr_rejection_rate or 0 for m in metrics) / len(metrics) if metrics else 0
    
    summary = {
        "avg_retention_rate": avg_retention,
        "avg_modification_rate": avg_modification,
        "avg_bug_rate": avg_bug_rate,
        "avg_pr_rejection_rate": avg_pr_rejection,
    }
    
    trends = [
        {
            "date": m.date.strftime("%b %d"),
            "retention_rate": m.ai_code_retention_rate or 0,
            "modification_rate": m.ai_code_modification_rate or 0,
            "bug_rate": m.ai_code_bug_rate or 0,
            "pr_rejection_rate": m.pr_rejection_rate or 0,
        }
        for m in metrics
    ]
    
    return {"summary": summary, "trends": trends}


@router.delete("/{metrics_id}")
def delete_metrics(metrics_id: int, db: Session = Depends(get_db)):
    """Delete a metrics record"""
    metrics = db.query(DailyMetrics).filter(DailyMetrics.id == metrics_id).first()
    if not metrics:
        raise HTTPException(status_code=404, detail="Metrics not found")
    
    db.delete(metrics)
    db.commit()
    return {"message": "Metrics deleted successfully"}
