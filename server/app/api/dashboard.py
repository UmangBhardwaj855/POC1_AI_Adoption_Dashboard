"""
Dashboard API Endpoints
Provides summary data for the main dashboard view
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, timedelta
from typing import Optional

from app.database.connection import get_db
from app.database.models import Organization, User, DailyMetrics, KPI

router = APIRouter()


@router.get("/summary")
def get_dashboard_summary(
    org_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Get dashboard summary with key metrics
    Returns all KPIs from research document
    """
    # Get latest metrics
    query = db.query(DailyMetrics).order_by(DailyMetrics.date.desc())
    if org_id:
        query = query.filter(DailyMetrics.organization_id == org_id)
    latest = query.first()
    
    # Get user counts
    user_query = db.query(User)
    if org_id:
        user_query = user_query.filter(User.organization_id == org_id)
    
    total_users = user_query.count()
    enabled_users = user_query.filter(User.copilot_enabled == True).count()
    active_users = user_query.filter(User.is_weekly_active == True).count()
    
    # Get maturity distribution
    maturity_dist = db.query(
        User.maturity_level,
        func.count(User.id)
    ).group_by(User.maturity_level).all()
    
    maturity_counts = {f"l{level}_count": count for level, count in maturity_dist}
    
    # Calculate rates
    activation_rate = (active_users / enabled_users * 100) if enabled_users > 0 else 0
    
    # Get KPIs
    kpis = db.query(KPI).all()
    kpi_data = {kpi.name: {"target": kpi.target_value, "current": kpi.current_value, "achieved": kpi.is_achieved} for kpi in kpis}
    
    return {
        # User Counts
        "total_users": total_users,
        "enabled_users": enabled_users,
        "active_users": active_users,
        "weekly_active_users": latest.weekly_active_users if latest else 0,
        "monthly_active_users": latest.monthly_active_users if latest else 0,
        
        # Adoption Metrics
        "activation_rate": round(activation_rate, 1),
        "acceptance_rate": latest.acceptance_rate if latest else 0,
        "prompts_per_user": latest.prompts_per_user if latest else 0,
        "features_utilized": latest.features_utilized if latest else 0,
        "team_activation_rate": latest.team_activation_rate if latest else 0,
        
        # Productivity Metrics
        "total_suggestions": latest.total_suggestions_shown if latest else 0,
        "accepted_suggestions": latest.total_suggestions_accepted if latest else 0,
        "chat_interactions": latest.total_chat_interactions if latest else 0,
        "ai_assisted_commits": latest.ai_assisted_commits if latest else 0,
        "ai_assisted_prs": latest.ai_assisted_prs if latest else 0,
        "ai_code_lines": latest.ai_code_lines if latest else 0,
        
        # Quality Metrics
        "code_retention_rate": latest.ai_code_retention_rate if latest else 0,
        "modification_rate": latest.ai_code_modification_rate if latest else 0,
        "bug_rate": latest.ai_code_bug_rate if latest else 0,
        "pr_rejection_rate": latest.pr_rejection_rate if latest else 0,
        
        # Maturity Distribution
        "l0_count": maturity_counts.get("l0_count", 0),
        "l1_count": maturity_counts.get("l1_count", 0),
        "l2_count": maturity_counts.get("l2_count", 0),
        "l3_count": maturity_counts.get("l3_count", 0),
        "l4_count": maturity_counts.get("l4_count", 0),
        "l5_count": maturity_counts.get("l5_count", 0),
        
        # KPIs
        "kpis": kpi_data,
        
        # Breakdowns
        "language_breakdown": latest.language_breakdown if latest else {},
        "editor_breakdown": latest.editor_breakdown if latest else {},
    }


@router.get("/trends")
def get_trends(
    days: int = 30,
    org_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get metrics trends for charts"""
    start_date = date.today() - timedelta(days=days)
    
    query = db.query(DailyMetrics).filter(DailyMetrics.date >= start_date)
    if org_id:
        query = query.filter(DailyMetrics.organization_id == org_id)
    
    metrics = query.order_by(DailyMetrics.date).all()
    
    return [
        {
            "date": m.date.isoformat(),
            # Adoption
            "active_users": m.active_users or 0,
            "activation_rate": m.activation_rate or 0,
            "weekly_active_users": m.weekly_active_users or 0,
            # Productivity
            "acceptance_rate": m.acceptance_rate or 0,
            "suggestions_shown": m.total_suggestions_shown or 0,
            "suggestions_accepted": m.total_suggestions_accepted or 0,
            "chat_interactions": m.total_chat_interactions or 0,
            "ai_assisted_commits": m.ai_assisted_commits or 0,
            "ai_code_lines": m.ai_code_lines or 0,
            # Quality
            "code_retention_rate": m.ai_code_retention_rate or 0,
            "modification_rate": m.ai_code_modification_rate or 0,
        }
        for m in metrics
    ]


@router.get("/maturity-distribution")
def get_maturity_distribution(
    org_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get current maturity level distribution"""
    query = db.query(
        User.maturity_level,
        func.count(User.id).label('count')
    )
    if org_id:
        query = query.filter(User.organization_id == org_id)
    
    result = query.group_by(User.maturity_level).all()
    
    levels = {
        0: {"name": "L0", "description": "Not Enabled", "color": "#ea4335"},
        1: {"name": "L1", "description": "Enabled", "color": "#fbbc05"},
        2: {"name": "L2", "description": "Active User", "color": "#34a853"},
        3: {"name": "L3", "description": "Working User", "color": "#4285f4"},
        4: {"name": "L4", "description": "Consistent User", "color": "#9c27b0"},
        5: {"name": "L5", "description": "Value User", "color": "#00bcd4"},
    }
    
    distribution = []
    for level in range(6):
        count = next((r[1] for r in result if r[0] == level), 0)
        info = levels.get(level, {})
        distribution.append({
            "level": level,
            "name": info.get("name", f"L{level}"),
            "description": info.get("description", ""),
            "color": info.get("color", "#666"),
            "count": count
        })
    
    return distribution


@router.get("/team-breakdown")
def get_team_breakdown(db: Session = Depends(get_db)):
    """Get metrics breakdown by team"""
    result = db.query(
        User.team,
        func.count(User.id).label('total'),
        func.sum(func.cast(User.copilot_enabled, Integer)).label('enabled'),
        func.sum(func.cast(User.is_weekly_active, Integer)).label('active'),
        func.avg(User.maturity_level).label('avg_maturity')
    ).group_by(User.team).all()
    
    from sqlalchemy import Integer
    
    return [
        {
            "team": team or "Unassigned",
            "total_users": total,
            "enabled_users": enabled or 0,
            "active_users": active or 0,
            "avg_maturity": round(float(avg_maturity or 0), 1),
            "activation_rate": round((active or 0) / (enabled or 1) * 100, 1)
        }
        for team, total, enabled, active, avg_maturity in result
    ]


@router.get("/kpis")
def get_kpis(db: Session = Depends(get_db)):
    """
    Get KPIs based on Phase Progression Model
    - Phase 1: Activation Rate target: 60%
    - Phase 2: Work Linkage target: 50%
    - Phase 3: Consistency Score target: 40%
    - Phase 4: KOIs Achieved target: 8+
    """
    kpis = db.query(KPI).order_by(KPI.phase, KPI.name).all()
    
    if not kpis:
        # Return default KPIs from research document
        return [
            {"phase": 1, "name": "Activation Rate", "target": 60, "current": 0, "achieved": False, "category": "adoption"},
            {"phase": 2, "name": "Work Linkage", "target": 50, "current": 0, "achieved": False, "category": "productivity"},
            {"phase": 3, "name": "Consistency Score", "target": 40, "current": 0, "achieved": False, "category": "productivity"},
            {"phase": 4, "name": "KOIs Achieved", "target": 8, "current": 0, "achieved": False, "category": "quality"},
        ]
    
    return [
        {
            "id": kpi.id,
            "phase": kpi.phase,
            "name": kpi.name,
            "category": kpi.category,
            "target": kpi.target_value,
            "current": kpi.current_value,
            "achieved": kpi.is_achieved
        }
        for kpi in kpis
    ]
