"""
Seed Script for AI Adoption Dashboard
Adds realistic sample data to MySQL database
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta, date
import random
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.models import Base, Organization, User, DailyMetrics, KPI, UserActivityLog

# Database connection
DATABASE_URL = "mysql+pymysql://root:Tango%404556@localhost:3306/ai_adoption_db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# Sample data
TEAMS = ["Platform", "Backend", "Frontend", "DevOps", "QA", "Data Engineering", "Mobile", "Security"]

DEVELOPERS = [
    {"username": "rahul.sharma", "name": "Rahul Sharma", "team": "Backend"},
    {"username": "priya.patel", "name": "Priya Patel", "team": "Frontend"},
    {"username": "amit.kumar", "name": "Amit Kumar", "team": "Platform"},
    {"username": "sneha.gupta", "name": "Sneha Gupta", "team": "DevOps"},
    {"username": "vikram.singh", "name": "Vikram Singh", "team": "QA"},
    {"username": "ananya.reddy", "name": "Ananya Reddy", "team": "Data Engineering"},
    {"username": "karthik.nair", "name": "Karthik Nair", "team": "Mobile"},
    {"username": "deepa.iyer", "name": "Deepa Iyer", "team": "Security"},
    {"username": "arjun.menon", "name": "Arjun Menon", "team": "Backend"},
    {"username": "meera.krishnan", "name": "Meera Krishnan", "team": "Frontend"},
    {"username": "suresh.rajan", "name": "Suresh Rajan", "team": "Platform"},
    {"username": "kavitha.sundaram", "name": "Kavitha Sundaram", "team": "DevOps"},
    {"username": "rajesh.verma", "name": "Rajesh Verma", "team": "QA"},
    {"username": "pooja.sharma", "name": "Pooja Sharma", "team": "Data Engineering"},
    {"username": "nikhil.joshi", "name": "Nikhil Joshi", "team": "Mobile"},
    {"username": "divya.krishna", "name": "Divya Krishna", "team": "Security"},
    {"username": "sanjay.pillai", "name": "Sanjay Pillai", "team": "Backend"},
    {"username": "lakshmi.venkat", "name": "Lakshmi Venkat", "team": "Frontend"},
    {"username": "arun.prakash", "name": "Arun Prakash", "team": "Platform"},
    {"username": "nisha.rao", "name": "Nisha Rao", "team": "DevOps"},
]


def clear_data(session):
    """Clear existing data"""
    session.query(UserActivityLog).delete()
    session.query(DailyMetrics).delete()
    session.query(KPI).delete()
    session.query(User).delete()
    session.query(Organization).delete()
    session.commit()
    print("✅ Cleared existing data")


def seed_organization(session):
    """Create organization"""
    org = Organization(
        github_org="xoriant",
        name="Xoriant Solutions",
        total_seats=50,
        copilot_seats=25
    )
    session.add(org)
    session.commit()
    print(f"✅ Created organization: {org.name}")
    return org


def seed_users(session, org):
    """Create users with realistic data"""
    users = []
    maturity_weights = [0.05, 0.10, 0.20, 0.30, 0.25, 0.10]  # L0-L5 distribution
    
    for dev in DEVELOPERS:
        # Assign maturity level based on weights
        maturity = random.choices(range(6), weights=maturity_weights)[0]
        
        # Higher maturity = more likely to be active
        is_active = maturity >= 2 or random.random() < 0.3
        is_weekly_active = maturity >= 3 or (is_active and random.random() < 0.5)
        
        user = User(
            organization_id=org.id,
            github_username=dev["username"],
            name=dev["name"],
            email=f"{dev['username']}@xoriant.com",
            team=dev["team"],
            maturity_level=maturity,
            copilot_enabled=True,
            copilot_enabled_date=date.today() - timedelta(days=random.randint(30, 180)),
            is_weekly_active=is_weekly_active,
            is_monthly_active=is_active,
            last_activity_date=date.today() - timedelta(days=random.randint(0, 7)) if is_active else None
        )
        users.append(user)
        session.add(user)
    
    session.commit()
    print(f"✅ Created {len(users)} users")
    return users


def seed_daily_metrics(session, org):
    """Create 30 days of metrics data"""
    today = date.today()
    
    for day_offset in range(30):
        metric_date = today - timedelta(days=day_offset)
        
        # Create realistic daily variations
        base_active = 15 + random.randint(-3, 3)
        suggestions_shown = random.randint(800, 1500)
        acceptance_rate = random.uniform(0.28, 0.38)
        suggestions_accepted = int(suggestions_shown * acceptance_rate)
        
        # Weekend dip
        if metric_date.weekday() >= 5:
            base_active = int(base_active * 0.4)
            suggestions_shown = int(suggestions_shown * 0.3)
            suggestions_accepted = int(suggestions_accepted * 0.3)
        
        metrics = DailyMetrics(
            organization_id=org.id,
            date=metric_date,
            
            # Adoption Metrics
            total_users=20,
            enabled_users=20,
            active_users=base_active,
            weekly_active_users=base_active,
            monthly_active_users=18,
            activation_rate=(base_active / 20) * 100,
            prompts_per_user=random.uniform(20, 50),
            features_utilized=random.randint(4, 6),
            team_activation_rate=random.uniform(60, 80),
            
            # Maturity counts (realistic distribution)
            l0_count=random.randint(0, 2),
            l1_count=random.randint(1, 3),
            l2_count=random.randint(3, 5),
            l3_count=random.randint(4, 6),
            l4_count=random.randint(3, 5),
            l5_count=random.randint(1, 3),
            
            # Productivity Metrics
            total_suggestions_shown=suggestions_shown,
            total_suggestions_accepted=suggestions_accepted,
            acceptance_rate=acceptance_rate * 100,
            total_lines_suggested=random.randint(3000, 6000),
            total_lines_accepted=random.randint(1000, 2500),
            total_chat_interactions=random.randint(80, 200),
            ai_assisted_commits=random.randint(30, 60),
            ai_assisted_prs=random.randint(8, 20),
            total_commits=random.randint(50, 100),
            total_prs=random.randint(15, 35),
            ai_code_lines=random.randint(800, 2000),
            avg_time_to_first_commit=random.uniform(1.5, 3.5),
            avg_pr_cycle_time=random.uniform(4.0, 10.0),
            
            # Quality Metrics
            ai_code_retention_rate=random.uniform(82, 95),
            ai_code_modification_rate=random.uniform(5, 18),
            ai_code_bug_rate=random.uniform(1, 4),
            pr_rejection_rate=random.uniform(2, 8),
            avg_review_comments=random.uniform(1.5, 4.0),
            
            # Breakdown data
            language_breakdown={
                "Java": random.randint(30, 40),
                "Python": random.randint(20, 30),
                "JavaScript": random.randint(15, 25),
                "TypeScript": random.randint(10, 20),
                "SQL": random.randint(5, 10)
            },
            editor_breakdown={
                "VS Code": random.randint(60, 75),
                "IntelliJ": random.randint(20, 30),
                "PyCharm": random.randint(5, 15)
            }
        )
        session.add(metrics)
    
    session.commit()
    print("✅ Created 30 days of metrics data")


def seed_kpis(session):
    """Create KPIs based on Phase Progression Model"""
    kpis = [
        KPI(
            name="Activation Rate",
            category="adoption",
            phase=1,
            target_value=60.0,
            current_value=72.5,
            is_achieved=True,
            measurement_date=date.today()
        ),
        KPI(
            name="Work Linkage",
            category="productivity",
            phase=2,
            target_value=50.0,
            current_value=48.3,
            is_achieved=False,
            measurement_date=date.today()
        ),
        KPI(
            name="Consistency Score",
            category="productivity",
            phase=3,
            target_value=40.0,
            current_value=42.1,
            is_achieved=True,
            measurement_date=date.today()
        ),
        KPI(
            name="KOIs Achieved",
            category="quality",
            phase=4,
            target_value=8.0,
            current_value=7.0,
            is_achieved=False,
            measurement_date=date.today()
        ),
    ]
    
    for kpi in kpis:
        session.add(kpi)
    
    session.commit()
    print("✅ Created KPIs")


def seed_activity_logs(session, users):
    """Create user activity logs"""
    today = date.today()
    features = ["completions", "chat", "inline", "docstring", "test_generation"]
    
    for user in users:
        if user.maturity_level < 2:
            continue  # Low maturity users have less activity
            
        # Create activity for last 7 days
        for day_offset in range(7):
            if random.random() < 0.3:  # 30% chance of no activity on a day
                continue
                
            activity_date = today - timedelta(days=day_offset)
            
            # Weekend less activity
            if activity_date.weekday() >= 5 and random.random() < 0.7:
                continue
            
            suggestions = random.randint(20, 100)
            accepted = int(suggestions * random.uniform(0.25, 0.40))
            
            log = UserActivityLog(
                user_id=user.id,
                date=activity_date,
                suggestions_shown=suggestions,
                suggestions_accepted=accepted,
                lines_suggested=random.randint(100, 500),
                lines_accepted=random.randint(30, 200),
                chat_interactions=random.randint(5, 30),
                features_used=random.sample(features, random.randint(2, 4)),
                commits_count=random.randint(2, 10),
                ai_assisted_commits=random.randint(1, 6),
                prs_created=random.randint(0, 3),
                ai_assisted_prs=random.randint(0, 2)
            )
            session.add(log)
    
    session.commit()
    print("✅ Created user activity logs")


def main():
    print("\n🚀 Seeding AI Adoption Dashboard Database\n")
    print("=" * 50)
    
    session = Session()
    
    try:
        # Clear existing data
        clear_data(session)
        
        # Seed data
        org = seed_organization(session)
        users = seed_users(session, org)
        seed_daily_metrics(session, org)
        seed_kpis(session)
        seed_activity_logs(session, users)
        
        print("\n" + "=" * 50)
        print("✅ Database seeding completed successfully!")
        print(f"\n📊 Summary:")
        print(f"   - 1 Organization")
        print(f"   - {len(users)} Users")
        print(f"   - 30 Days of Metrics")
        print(f"   - 4 KPIs")
        print(f"   - Activity logs for active users")
        
    except Exception as e:
        session.rollback()
        print(f"\n❌ Error: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
