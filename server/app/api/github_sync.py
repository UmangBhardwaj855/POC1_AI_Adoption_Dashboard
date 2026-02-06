"""
GitHub Sync API Endpoints
Allows syncing data from GitHub via the dashboard
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from datetime import date, timedelta

from app.database.connection import get_db
from app.database.models import Organization, User, DailyMetrics
from app.integrations.github_copilot import GitHubCopilotClientSync
from sqlalchemy.orm import Session
from fastapi import Depends

router = APIRouter()


class GitHubSyncRequest(BaseModel):
    token: str
    org: str
    sync_users: bool = True
    sync_metrics: bool = True
    days: int = 30


class GitHubSyncResponse(BaseModel):
    success: bool
    message: str
    org_name: Optional[str] = None
    users_synced: Optional[int] = None
    metrics_synced: Optional[int] = None


@router.post("/sync", response_model=GitHubSyncResponse)
def sync_github_data(request: GitHubSyncRequest, db: Session = Depends(get_db)):
    """
    Sync organization data from GitHub
    
    Requires:
    - GitHub Personal Access Token with read:org and copilot scopes
    - Organization must have GitHub Copilot Business/Enterprise
    """
    try:
        client = GitHubCopilotClientSync(token=request.token, org=request.org)
        
        # Sync organization
        try:
            billing = client.get_copilot_billing()
            total_seats = billing.get("seat_breakdown", {}).get("total", 0)
            active_seats = billing.get("seat_breakdown", {}).get("active_this_cycle", 0)
        except Exception as e:
            # If billing fails, still try to create org
            total_seats = 0
            active_seats = 0
        
        org = db.query(Organization).filter(
            Organization.github_org == request.org
        ).first()
        
        if org:
            org.copilot_seats = active_seats
            org.total_seats = total_seats
        else:
            org = Organization(
                github_org=request.org,
                name=request.org.title(),
                total_seats=total_seats,
                copilot_seats=active_seats
            )
            db.add(org)
        
        db.commit()
        db.refresh(org)
        
        users_synced = 0
        metrics_synced = 0
        
        # Sync users
        if request.sync_users:
            members = client.get_org_members()
            
            # Get Copilot seats
            try:
                seats_data = client.get_copilot_seats()
                copilot_users = {
                    seat["assignee"]["login"]: seat 
                    for seat in seats_data.get("seats", [])
                }
            except:
                copilot_users = {}
            
            for member in members:
                username = member["login"]
                
                user = db.query(User).filter(
                    User.github_username == username,
                    User.organization_id == org.id
                ).first()
                
                has_copilot = username in copilot_users
                
                if not user:
                    user = User(
                        organization_id=org.id,
                        github_username=username,
                        name=username,
                        email=f"{username}@{request.org}.com",
                        team="Unassigned",
                        maturity_level=1 if has_copilot else 0,
                        copilot_enabled=has_copilot,
                        is_weekly_active=False,
                        is_monthly_active=False
                    )
                    db.add(user)
                    users_synced += 1
                else:
                    user.copilot_enabled = has_copilot
                    users_synced += 1
            
            db.commit()
        
        # Sync metrics (Enterprise only)
        if request.sync_metrics:
            try:
                since = date.today() - timedelta(days=request.days)
                usage_data = client.get_copilot_usage(since=since)
                
                for day_data in usage_data:
                    metric_date = date.fromisoformat(day_data["day"][:10])
                    
                    suggestions = day_data.get("total_suggestions_count", 0)
                    acceptances = day_data.get("total_acceptances_count", 0)
                    acceptance_rate = (acceptances / suggestions * 100) if suggestions > 0 else 0
                    
                    existing = db.query(DailyMetrics).filter(
                        DailyMetrics.organization_id == org.id,
                        DailyMetrics.date == metric_date
                    ).first()
                    
                    if not existing:
                        metrics = DailyMetrics(
                            organization_id=org.id,
                            date=metric_date,
                            active_users=day_data.get("total_active_users", 0),
                            total_suggestions_shown=suggestions,
                            total_suggestions_accepted=acceptances,
                            acceptance_rate=acceptance_rate,
                            total_lines_suggested=day_data.get("total_lines_suggested", 0),
                            total_lines_accepted=day_data.get("total_lines_accepted", 0),
                        )
                        db.add(metrics)
                    
                    metrics_synced += 1
                
                db.commit()
            except Exception as e:
                # Metrics API might not be available (Enterprise only)
                pass
        
        return GitHubSyncResponse(
            success=True,
            message="Sync completed successfully",
            org_name=org.name,
            users_synced=users_synced,
            metrics_synced=metrics_synced
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/test-connection")
def test_github_connection(token: str, org: str):
    """Test GitHub API connection"""
    try:
        client = GitHubCopilotClientSync(token=token, org=org)
        members = client.get_org_members()
        
        return {
            "success": True,
            "message": f"Successfully connected to {org}",
            "members_count": len(members)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
