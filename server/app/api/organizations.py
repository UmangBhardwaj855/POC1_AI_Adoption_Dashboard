"""
Organizations API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

from app.database.connection import get_db
from app.database.models import Organization

router = APIRouter()


class OrganizationCreate(BaseModel):
    github_org: str
    name: Optional[str] = None
    total_seats: Optional[int] = 0
    copilot_seats: Optional[int] = 0

class OrganizationResponse(BaseModel):
    id: int
    github_org: str
    name: Optional[str]
    total_seats: Optional[int]
    copilot_seats: Optional[int]
    created_at: Optional[datetime]
    
    class Config:
        from_attributes = True


@router.get("", response_model=List[OrganizationResponse])
def get_organizations(db: Session = Depends(get_db)):
    """Get all organizations"""
    return db.query(Organization).all()


@router.get("/{org_id}", response_model=OrganizationResponse)
def get_organization(org_id: int, db: Session = Depends(get_db)):
    """Get a specific organization"""
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org


@router.post("", response_model=OrganizationResponse)
def create_organization(org: OrganizationCreate, db: Session = Depends(get_db)):
    """Create a new organization"""
    existing = db.query(Organization).filter(Organization.github_org == org.github_org).first()
    if existing:
        raise HTTPException(status_code=400, detail="Organization already exists")
    
    db_org = Organization(
        github_org=org.github_org,
        name=org.name,
        total_seats=org.total_seats,
        copilot_seats=org.copilot_seats,
        created_at=datetime.now()
    )
    db.add(db_org)
    db.commit()
    db.refresh(db_org)
    return db_org


@router.delete("/{org_id}")
def delete_organization(org_id: int, db: Session = Depends(get_db)):
    """Delete an organization"""
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    db.delete(org)
    db.commit()
    return {"message": "Organization deleted successfully"}
