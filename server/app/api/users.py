"""
Users API Endpoints
User management and maturity level tracking
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

from app.database.connection import get_db
from app.database.models import User

router = APIRouter()


# Pydantic Models
class UserCreate(BaseModel):
    github_username: str
    organization_id: Optional[int] = 1  # Default to org 1
    name: Optional[str] = None
    email: Optional[str] = None
    team: Optional[str] = None
    maturity_level: Optional[int] = 0
    copilot_enabled: Optional[bool] = False
    is_active: Optional[bool] = True  # Frontend sends is_active

class UserUpdate(BaseModel):
    github_username: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    team: Optional[str] = None
    maturity_level: Optional[int] = None
    copilot_enabled: Optional[bool] = None
    is_active: Optional[bool] = None  # Frontend sends is_active
    is_weekly_active: Optional[bool] = None
    is_monthly_active: Optional[bool] = None

class UserResponse(BaseModel):
    id: int
    github_username: str
    organization_id: Optional[int]
    name: Optional[str]
    email: Optional[str]
    team: Optional[str]
    maturity_level: Optional[int]
    copilot_enabled: Optional[bool]
    is_weekly_active: Optional[bool]
    is_monthly_active: Optional[bool]
    is_active: Optional[bool] = None  # For frontend compatibility
    created_at: Optional[datetime]
    
    class Config:
        from_attributes = True
    
    @classmethod
    def model_validate(cls, obj, **kwargs):
        # Map copilot_enabled to is_active for frontend
        instance = super().model_validate(obj, **kwargs)
        if instance.is_active is None:
            instance.is_active = instance.copilot_enabled
        return instance


@router.get("", response_model=List[UserResponse])
def get_users(
    org_id: Optional[int] = None,
    team: Optional[str] = None,
    maturity_level: Optional[int] = None,
    active_only: bool = False,
    db: Session = Depends(get_db)
):
    """Get all users with optional filters"""
    query = db.query(User)
    
    if org_id:
        query = query.filter(User.organization_id == org_id)
    if team:
        query = query.filter(User.team == team)
    if maturity_level is not None:
        query = query.filter(User.maturity_level == maturity_level)
    if active_only:
        query = query.filter(User.is_weekly_active == True)
    
    users = query.order_by(User.github_username).all()
    
    # Add is_active field for frontend compatibility
    result = []
    for user in users:
        user_dict = {
            "id": user.id,
            "github_username": user.github_username,
            "organization_id": user.organization_id,
            "name": user.name,
            "email": user.email,
            "team": user.team,
            "maturity_level": user.maturity_level,
            "copilot_enabled": user.copilot_enabled,
            "is_weekly_active": user.is_weekly_active,
            "is_monthly_active": user.is_monthly_active,
            "is_active": user.copilot_enabled,
            "created_at": user.created_at
        }
        result.append(user_dict)
    
    return result


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get a specific user by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    # Check if username already exists
    existing = db.query(User).filter(User.github_username == user.github_username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Map is_active to copilot_enabled
    copilot_enabled = user.copilot_enabled if user.copilot_enabled is not None else user.is_active
    
    db_user = User(
        github_username=user.github_username,
        organization_id=user.organization_id or 1,
        name=user.name or user.github_username,
        email=user.email,
        team=user.team,
        maturity_level=user.maturity_level or 0,
        copilot_enabled=copilot_enabled,
        is_weekly_active=user.maturity_level >= 2 if user.maturity_level else False,
        is_monthly_active=user.maturity_level >= 1 if user.maturity_level else False,
        created_at=datetime.now()
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    """Update a user"""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = user.model_dump(exclude_unset=True)
    
    # Map is_active to copilot_enabled
    if 'is_active' in update_data:
        update_data['copilot_enabled'] = update_data.pop('is_active')
    
    for key, value in update_data.items():
        if hasattr(db_user, key):
            setattr(db_user, key, value)
    
    db_user.updated_at = datetime.now()
    db.commit()
    db.refresh(db_user)
    return db_user


@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Delete a user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}


@router.get("/stats/by-team")
def get_users_by_team(db: Session = Depends(get_db)):
    """Get user statistics by team"""
    result = db.query(
        User.team,
        func.count(User.id).label('count'),
        func.avg(User.maturity_level).label('avg_maturity')
    ).group_by(User.team).all()
    
    return [
        {
            "team": team or "Unassigned",
            "count": count,
            "avg_maturity": round(float(avg_maturity or 0), 1)
        }
        for team, count, avg_maturity in result
    ]


@router.get("/stats/by-maturity")
def get_users_by_maturity(db: Session = Depends(get_db)):
    """Get user count by maturity level"""
    result = db.query(
        User.maturity_level,
        func.count(User.id).label('count')
    ).group_by(User.maturity_level).all()
    
    level_names = {
        0: "L0 - Not Enabled",
        1: "L1 - Enabled",
        2: "L2 - Active User",
        3: "L3 - Working User",
        4: "L4 - Consistent User",
        5: "L5 - Value User"
    }
    
    return [
        {
            "level": level,
            "name": level_names.get(level, f"L{level}"),
            "count": count
        }
        for level, count in result
    ]
