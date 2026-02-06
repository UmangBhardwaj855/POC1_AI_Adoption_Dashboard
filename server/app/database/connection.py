"""
Database Connection and Session Management
Tier 3: MySQL Database Layer
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
import os
from dotenv import load_dotenv

from app.database.models import Base

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:Tango%404556@localhost:3306/ai_adoption_db"
)

def get_engine():
    """Create database engine"""
    if DATABASE_URL.startswith("mysql"):
        return create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=False
        )
    # SQLite fallback
    return create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False
    )

engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_database():
    """Initialize database tables"""
    # Only drop tables if explicitly requested
    if os.getenv("RESET_DB", "false").lower() == "true":
        Base.metadata.drop_all(bind=engine)
        print("Database tables dropped")
    
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    print("Database tables created/verified")
    
    # Seed initial data (will check if data exists first)
    seed_sample_data()

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db_session() -> Session:
    """Context manager for database sessions"""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def seed_sample_data():
    """Seed sample data for development"""
    from datetime import datetime, timedelta
    import random
    from app.database.models import Organization, User, DailyMetrics, KPI
    
    with get_db_session() as db:
        # Check if data already exists
        if db.query(Organization).first():
            print("Sample data already exists")
            return
        
        # Create organization
        org = Organization(github_org="xoriant", name="Xoriant", total_seats=20, copilot_seats=15)
        db.add(org)
        db.flush()
        
        # Create users with different maturity levels
        teams = ["Platform", "Backend", "Frontend", "DevOps", "QA"]
        users = []
        for i in range(10):
            user = User(
                organization_id=org.id,
                github_username=f"dev{i+1}",
                email=f"dev{i+1}@xoriant.com",
                team=teams[i % len(teams)],
                maturity_level=random.randint(0, 5),
                copilot_enabled=True
            )
            users.append(user)
            db.add(user)
        
        db.flush()
        
        # Create daily metrics for last 30 days
        today = datetime.now().date()
        for day_offset in range(30):
            date = today - timedelta(days=day_offset)
            active = random.randint(6, 10)
            suggestions_shown = random.randint(500, 1000)
            suggestions_accepted = int(suggestions_shown * random.uniform(0.25, 0.40))
            
            metrics = DailyMetrics(
                organization_id=org.id,
                date=date,
                total_users=10,
                enabled_users=random.randint(8, 10),
                active_users=active,
                weekly_active_users=active,
                monthly_active_users=10,
                activation_rate=active * 10.0,
                prompts_per_user=random.uniform(15, 45),
                features_utilized=random.randint(3, 6),
                team_activation_rate=random.uniform(55, 75),
                l0_count=random.randint(0, 2),
                l1_count=random.randint(1, 2),
                l2_count=random.randint(1, 3),
                l3_count=random.randint(2, 3),
                l4_count=random.randint(1, 2),
                l5_count=random.randint(0, 2),
                total_suggestions_shown=suggestions_shown,
                total_suggestions_accepted=suggestions_accepted,
                acceptance_rate=(suggestions_accepted / suggestions_shown) * 100,
                total_lines_suggested=random.randint(2000, 5000),
                total_lines_accepted=random.randint(600, 2000),
                total_chat_interactions=random.randint(50, 150),
                ai_assisted_commits=random.randint(20, 50),
                ai_assisted_prs=random.randint(5, 15),
                total_commits=random.randint(40, 80),
                total_prs=random.randint(10, 25),
                ai_code_lines=random.randint(500, 1500),
                avg_time_to_first_commit=random.uniform(1.5, 4.0),
                avg_pr_cycle_time=random.uniform(4.0, 12.0),
                ai_code_retention_rate=random.uniform(80, 95),
                ai_code_modification_rate=random.uniform(5, 20),
                ai_code_bug_rate=random.uniform(1, 5),
                pr_rejection_rate=random.uniform(2, 10),
                avg_review_comments=random.uniform(1, 4)
            )
            db.add(metrics)
        
        # Create KPIs
        from datetime import date
        kpis = [
            KPI(name="Activation Rate", category="adoption", phase=1, target_value=60.0, current_value=65.0, measurement_date=date.today()),
            KPI(name="Work Linkage", category="productivity", phase=2, target_value=50.0, current_value=45.0, measurement_date=date.today()),
            KPI(name="Consistency", category="productivity", phase=3, target_value=40.0, current_value=38.0, measurement_date=date.today()),
            KPI(name="KOIs Achieved", category="quality", phase=4, target_value=8.0, current_value=6.0, measurement_date=date.today()),
        ]
        for kpi in kpis:
            db.add(kpi)
        
        print("Sample data seeded successfully")
