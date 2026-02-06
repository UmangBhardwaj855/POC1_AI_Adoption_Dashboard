"""
GitHub Organization Sync Script
Imports users from GitHub and syncs Copilot usage data to MySQL

Usage:
  python sync_github_data.py --token YOUR_GITHUB_TOKEN --org YOUR_ORG_NAME

Requirements:
  - GitHub Personal Access Token with scopes: read:org, copilot
  - Organization must have GitHub Copilot Business/Enterprise license
"""

import sys
import os
import argparse
from datetime import datetime, date, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.models import Organization, User, DailyMetrics, UserActivityLog
from app.integrations.github_copilot import GitHubCopilotClientSync

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/metrics.db")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)


def sync_organization(client: GitHubCopilotClientSync, session) -> Organization:
    """Create or update organization from GitHub"""
    print(f"\n📦 Syncing organization: {client.org}")
    
    # Get Copilot billing info
    try:
        billing = client.get_copilot_billing()
        total_seats = billing.get("seat_breakdown", {}).get("total", 0)
        active_seats = billing.get("seat_breakdown", {}).get("active_this_cycle", 0)
    except Exception as e:
        print(f"   ⚠️ Could not fetch Copilot billing: {e}")
        total_seats = 0
        active_seats = 0
    
    # Check if org exists
    org = session.query(Organization).filter(
        Organization.github_org == client.org
    ).first()
    
    if org:
        org.copilot_seats = active_seats
        org.total_seats = total_seats
        print(f"   ✅ Updated organization: {org.name}")
    else:
        org = Organization(
            github_org=client.org,
            name=client.org.title(),
            total_seats=total_seats,
            copilot_seats=active_seats
        )
        session.add(org)
        print(f"   ✅ Created organization: {org.name}")
    
    session.commit()
    return org


def sync_users(client: GitHubCopilotClientSync, session, org: Organization) -> list:
    """Import all org members and Copilot seat assignments"""
    print(f"\n👥 Syncing users from GitHub organization...")
    
    # Get all org members
    members = client.get_org_members()
    print(f"   Found {len(members)} members in organization")
    
    # Get Copilot seats
    try:
        seats_data = client.get_copilot_seats()
        copilot_users = {
            seat["assignee"]["login"]: seat 
            for seat in seats_data.get("seats", [])
        }
        print(f"   Found {len(copilot_users)} Copilot seats assigned")
    except Exception as e:
        print(f"   ⚠️ Could not fetch Copilot seats: {e}")
        copilot_users = {}
    
    users = []
    new_count = 0
    updated_count = 0
    
    for member in members:
        username = member["login"]
        
        # Check if user exists
        user = session.query(User).filter(
            User.github_username == username,
            User.organization_id == org.id
        ).first()
        
        # Get detailed user info
        try:
            user_details = client.get_user_details(username)
            name = user_details.get("name") or username
            email = user_details.get("email") or f"{username}@{client.org}.com"
        except:
            name = username
            email = f"{username}@{client.org}.com"
        
        # Check if user has Copilot seat
        copilot_seat = copilot_users.get(username)
        has_copilot = copilot_seat is not None
        
        # Parse Copilot enabled date
        copilot_date = None
        if copilot_seat and copilot_seat.get("created_at"):
            try:
                copilot_date = datetime.fromisoformat(
                    copilot_seat["created_at"].replace("Z", "+00:00")
                ).date()
            except:
                copilot_date = date.today()
        
        # Determine last activity
        last_activity = None
        if copilot_seat and copilot_seat.get("last_activity_at"):
            try:
                last_activity = datetime.fromisoformat(
                    copilot_seat["last_activity_at"].replace("Z", "+00:00")
                ).date()
            except:
                pass
        
        if user:
            # Update existing user
            user.name = name
            user.copilot_enabled = has_copilot
            user.copilot_enabled_date = copilot_date or user.copilot_enabled_date
            user.last_activity_date = last_activity
            updated_count += 1
        else:
            # Create new user
            user = User(
                organization_id=org.id,
                github_username=username,
                name=name,
                email=email,
                team="Unassigned",  # Can be updated manually later
                maturity_level=0 if not has_copilot else 1,
                copilot_enabled=has_copilot,
                copilot_enabled_date=copilot_date,
                is_weekly_active=False,
                is_monthly_active=False,
                last_activity_date=last_activity
            )
            session.add(user)
            new_count += 1
        
        users.append(user)
    
    session.commit()
    print(f"   ✅ Created {new_count} new users")
    print(f"   ✅ Updated {updated_count} existing users")
    
    return users


def sync_copilot_metrics(client: GitHubCopilotClientSync, session, org: Organization, days: int = 30):
    """Sync Copilot usage metrics (requires Enterprise)"""
    print(f"\n📊 Syncing Copilot usage metrics (last {days} days)...")
    
    try:
        since = date.today() - timedelta(days=days)
        usage_data = client.get_copilot_usage(since=since)
        
        if not usage_data:
            print("   ⚠️ No usage data returned (may require Enterprise license)")
            return
        
        synced_count = 0
        
        for day_data in usage_data:
            metric_date = datetime.fromisoformat(day_data["day"]).date()
            
            # Check if metrics exist for this date
            existing = session.query(DailyMetrics).filter(
                DailyMetrics.organization_id == org.id,
                DailyMetrics.date == metric_date
            ).first()
            
            # Calculate acceptance rate
            suggestions = day_data.get("total_suggestions_count", 0)
            acceptances = day_data.get("total_acceptances_count", 0)
            acceptance_rate = (acceptances / suggestions * 100) if suggestions > 0 else 0
            
            # Get breakdown data
            language_breakdown = {}
            editor_breakdown = {}
            
            for breakdown in day_data.get("breakdown", []):
                lang = breakdown.get("language")
                editor = breakdown.get("editor")
                accepts = breakdown.get("acceptances_count", 0)
                
                if lang:
                    language_breakdown[lang] = language_breakdown.get(lang, 0) + accepts
                if editor:
                    editor_breakdown[editor] = editor_breakdown.get(editor, 0) + accepts
            
            metrics_data = {
                "organization_id": org.id,
                "date": metric_date,
                "active_users": day_data.get("total_active_users", 0),
                "total_suggestions_shown": suggestions,
                "total_suggestions_accepted": acceptances,
                "acceptance_rate": acceptance_rate,
                "total_lines_suggested": day_data.get("total_lines_suggested", 0),
                "total_lines_accepted": day_data.get("total_lines_accepted", 0),
                "total_chat_interactions": day_data.get("total_chat_turns", 0),
                "language_breakdown": language_breakdown,
                "editor_breakdown": editor_breakdown,
            }
            
            if existing:
                for key, value in metrics_data.items():
                    setattr(existing, key, value)
            else:
                metrics = DailyMetrics(**metrics_data)
                session.add(metrics)
            
            synced_count += 1
        
        session.commit()
        print(f"   ✅ Synced {synced_count} days of metrics")
        
    except Exception as e:
        print(f"   ❌ Error syncing metrics: {e}")
        print("   Note: Usage API requires GitHub Copilot Enterprise license")


def calculate_maturity_levels(session, org: Organization):
    """Calculate maturity levels based on activity"""
    print(f"\n🎯 Calculating user maturity levels...")
    
    users = session.query(User).filter(User.organization_id == org.id).all()
    
    for user in users:
        if not user.copilot_enabled:
            user.maturity_level = 0  # L0: Not Enabled
            continue
        
        # Get user's activity logs from last 30 days
        thirty_days_ago = date.today() - timedelta(days=30)
        activities = session.query(UserActivityLog).filter(
            UserActivityLog.user_id == user.id,
            UserActivityLog.date >= thirty_days_ago
        ).all()
        
        if not activities:
            user.maturity_level = 1  # L1: Enabled but no activity
            continue
        
        # Calculate metrics
        total_suggestions = sum(a.suggestions_shown or 0 for a in activities)
        total_accepted = sum(a.suggestions_accepted or 0 for a in activities)
        active_days = len(activities)
        acceptance_rate = (total_accepted / total_suggestions * 100) if total_suggestions > 0 else 0
        
        # Determine maturity level
        if active_days < 5:
            user.maturity_level = 2  # L2: Active (some usage)
        elif active_days < 15:
            user.maturity_level = 3  # L3: Working (regular usage)
        elif acceptance_rate < 30:
            user.maturity_level = 4  # L4: Consistent (frequent usage)
        else:
            user.maturity_level = 5  # L5: Value User (high acceptance)
        
        # Update activity flags
        user.is_monthly_active = active_days > 0
        user.is_weekly_active = any(
            a.date >= (date.today() - timedelta(days=7)) for a in activities
        )
    
    session.commit()
    
    # Print distribution
    levels = [0, 0, 0, 0, 0, 0]
    for user in users:
        levels[user.maturity_level] += 1
    
    print(f"   Maturity Distribution:")
    labels = ["L0: Not Enabled", "L1: Enabled", "L2: Active", "L3: Working", "L4: Consistent", "L5: Value User"]
    for i, count in enumerate(levels):
        print(f"      {labels[i]}: {count} users")


def main():
    parser = argparse.ArgumentParser(description="Sync GitHub organization data")
    parser.add_argument("--token", required=True, help="GitHub Personal Access Token")
    parser.add_argument("--org", required=True, help="GitHub Organization name")
    parser.add_argument("--days", type=int, default=30, help="Days of history to sync")
    parser.add_argument("--skip-metrics", action="store_true", help="Skip Copilot metrics sync")
    
    args = parser.parse_args()
    
    print("\n" + "=" * 60)
    print("🚀 GitHub Organization Data Sync")
    print("=" * 60)
    
    # Initialize client
    client = GitHubCopilotClientSync(token=args.token, org=args.org)
    session = Session()
    
    try:
        # Sync organization
        org = sync_organization(client, session)
        
        # Sync users
        users = sync_users(client, session, org)
        
        # Sync Copilot metrics (if not skipped)
        if not args.skip_metrics:
            sync_copilot_metrics(client, session, org, days=args.days)
        
        # Calculate maturity levels
        calculate_maturity_levels(session, org)
        
        print("\n" + "=" * 60)
        print("✅ Sync completed successfully!")
        print("=" * 60)
        print(f"\n📊 Summary:")
        print(f"   Organization: {org.name}")
        print(f"   Total Users: {len(users)}")
        print(f"   Copilot Seats: {org.copilot_seats}")
        
    except Exception as e:
        session.rollback()
        print(f"\n❌ Error: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
