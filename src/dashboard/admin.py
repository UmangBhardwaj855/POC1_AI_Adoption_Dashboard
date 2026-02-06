"""
POC 1: AI Adoption Metrics Dashboard
Admin Panel - Data Management Interface

Allows adding, editing, and deleting data from the database.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.database.connection import init_database, get_db_session
from src.database.models import Organization, User, DailyMetrics

# Page configuration
st.set_page_config(
    page_title="Admin Panel - AI Adoption Tracker",
    page_icon="⚙️",
    layout="wide"
)

st.title("⚙️ Admin Panel - Data Management")
st.markdown("Manage organizations, users, and metrics data in the database.")

# Initialize database
init_database()


def get_organizations():
    """Get all organizations from database."""
    with get_db_session() as session:
        orgs = session.query(Organization).all()
        return [{"id": o.id, "github_org": o.github_org, "name": o.name, "total_seats": o.total_seats} for o in orgs]


def get_users(org_id=None):
    """Get all users from database."""
    with get_db_session() as session:
        query = session.query(User)
        if org_id:
            query = query.filter(User.organization_id == org_id)
        users = query.all()
        return [{
            "id": u.id,
            "github_username": u.github_username,
            "name": u.name,
            "team": u.team,
            "copilot_enabled": u.copilot_enabled,
            "maturity_level": u.maturity_level,
            "is_weekly_active": u.is_weekly_active,
            "is_monthly_active": u.is_monthly_active
        } for u in users]


def get_daily_metrics(org_id=None, limit=30):
    """Get daily metrics from database."""
    with get_db_session() as session:
        query = session.query(DailyMetrics)
        if org_id:
            query = query.filter(DailyMetrics.organization_id == org_id)
        metrics = query.order_by(DailyMetrics.date.desc()).limit(limit).all()
        return [{
            "id": m.id,
            "date": m.date,
            "total_users": m.total_users,
            "enabled_users": m.enabled_users,
            "active_users": m.active_users,
            "weekly_active_users": m.weekly_active_users,
            "monthly_active_users": m.monthly_active_users,
            "acceptance_rate": m.acceptance_rate,
            "activation_rate": m.activation_rate,
            "ai_assisted_commits": m.ai_assisted_commits,
            "ai_assisted_prs": m.ai_assisted_prs,
            "l0_count": m.l0_count,
            "l1_count": m.l1_count,
            "l2_count": m.l2_count,
            "l3_count": m.l3_count,
            "l4_count": m.l4_count,
            "l5_count": m.l5_count
        } for m in metrics]


# Tabs for different management sections
tab1, tab2, tab3, tab4 = st.tabs(["🏢 Organizations", "👤 Users", "📊 Daily Metrics", "🗑️ Clear Data"])

# ==================== ORGANIZATIONS TAB ====================
with tab1:
    st.subheader("🏢 Manage Organizations")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("#### Add New Organization")
        with st.form("add_org_form"):
            org_github = st.text_input("GitHub Org Name*", placeholder="e.g., xoriant")
            org_name = st.text_input("Display Name", placeholder="e.g., Xoriant Corporation")
            org_seats = st.number_input("Total Seats", min_value=1, value=50)
            
            if st.form_submit_button("➕ Add Organization", type="primary"):
                if org_github:
                    try:
                        with get_db_session() as session:
                            new_org = Organization(
                                github_org=org_github,
                                name=org_name or org_github,
                                total_seats=org_seats
                            )
                            session.add(new_org)
                        st.success(f"✅ Organization '{org_github}' added!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
                else:
                    st.warning("⚠️ GitHub Org Name is required")
    
    with col2:
        st.markdown("#### Existing Organizations")
        orgs = get_organizations()
        if orgs:
            df = pd.DataFrame(orgs)
            st.dataframe(df, use_container_width=True)
            
            # Delete organization
            org_to_delete = st.selectbox("Select organization to delete", 
                                         options=[o["github_org"] for o in orgs],
                                         key="del_org")
            if st.button("🗑️ Delete Organization", type="secondary"):
                with get_db_session() as session:
                    org = session.query(Organization).filter(Organization.github_org == org_to_delete).first()
                    if org:
                        session.delete(org)
                        st.success(f"✅ Deleted '{org_to_delete}'")
                        st.rerun()
        else:
            st.info("No organizations found. Add one above.")


# ==================== USERS TAB ====================
with tab2:
    st.subheader("👤 Manage Users")
    
    orgs = get_organizations()
    if not orgs:
        st.warning("⚠️ Please add an organization first!")
    else:
        selected_org = st.selectbox("Select Organization", 
                                    options=[o["github_org"] for o in orgs],
                                    key="user_org")
        org_id = next((o["id"] for o in orgs if o["github_org"] == selected_org), None)
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("#### Add New User")
            with st.form("add_user_form"):
                username = st.text_input("GitHub Username*", placeholder="e.g., john_doe")
                name = st.text_input("Full Name", placeholder="e.g., John Doe")
                team = st.selectbox("Team", ["Frontend", "Backend", "DevOps", "QA", "Data", "Mobile", "Other"])
                copilot_enabled = st.checkbox("Copilot Enabled", value=True)
                maturity_level = st.selectbox("Maturity Level", [0, 1, 2, 3, 4, 5], 
                                              format_func=lambda x: f"L{x}")
                weekly_active = st.checkbox("Weekly Active")
                monthly_active = st.checkbox("Monthly Active")
                
                if st.form_submit_button("➕ Add User", type="primary"):
                    if username:
                        try:
                            with get_db_session() as session:
                                new_user = User(
                                    github_username=username,
                                    organization_id=org_id,
                                    name=name or username,
                                    team=team,
                                    copilot_enabled=copilot_enabled,
                                    maturity_level=maturity_level,
                                    is_weekly_active=weekly_active,
                                    is_monthly_active=monthly_active
                                )
                                session.add(new_user)
                            st.success(f"✅ User '{username}' added!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error: {e}")
                    else:
                        st.warning("⚠️ GitHub Username is required")
        
        with col2:
            st.markdown("#### Existing Users")
            users = get_users(org_id)
            if users:
                df = pd.DataFrame(users)
                st.dataframe(df, use_container_width=True, height=400)
                
                # Bulk add users
                st.markdown("#### Bulk Add Users (CSV)")
                st.markdown("Upload CSV with columns: `github_username`, `name`, `team`, `copilot_enabled`, `maturity_level`")
                uploaded_file = st.file_uploader("Choose CSV file", type="csv")
                if uploaded_file:
                    csv_df = pd.read_csv(uploaded_file)
                    st.dataframe(csv_df)
                    if st.button("📥 Import Users"):
                        with get_db_session() as session:
                            for _, row in csv_df.iterrows():
                                user = User(
                                    github_username=row.get("github_username"),
                                    organization_id=org_id,
                                    name=row.get("name", row.get("github_username")),
                                    team=row.get("team", "Other"),
                                    copilot_enabled=bool(row.get("copilot_enabled", True)),
                                    maturity_level=int(row.get("maturity_level", 1))
                                )
                                session.add(user)
                        st.success("✅ Users imported!")
                        st.rerun()
            else:
                st.info("No users found. Add one above.")


# ==================== DAILY METRICS TAB ====================
with tab3:
    st.subheader("📊 Manage Daily Metrics")
    
    orgs = get_organizations()
    if not orgs:
        st.warning("⚠️ Please add an organization first!")
    else:
        selected_org = st.selectbox("Select Organization", 
                                    options=[o["github_org"] for o in orgs],
                                    key="metrics_org")
        org_id = next((o["id"] for o in orgs if o["github_org"] == selected_org), None)
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("#### Add Daily Metrics")
            with st.form("add_metrics_form"):
                metric_date = st.date_input("Date", value=date.today())
                
                st.markdown("**User Counts**")
                total_users = st.number_input("Total Users", min_value=0, value=50)
                enabled_users = st.number_input("Enabled Users", min_value=0, value=45)
                active_users = st.number_input("Active Users", min_value=0, value=35)
                weekly_active = st.number_input("Weekly Active Users", min_value=0, value=30)
                monthly_active = st.number_input("Monthly Active Users", min_value=0, value=40)
                
                st.markdown("**Copilot Usage**")
                suggestions_shown = st.number_input("Suggestions Shown", min_value=0, value=500)
                suggestions_accepted = st.number_input("Suggestions Accepted", min_value=0, value=175)
                
                st.markdown("**Productivity**")
                ai_commits = st.number_input("AI-Assisted Commits", min_value=0, value=20)
                ai_prs = st.number_input("AI-Assisted PRs", min_value=0, value=8)
                total_commits = st.number_input("Total Commits", min_value=0, value=80)
                total_prs = st.number_input("Total PRs", min_value=0, value=25)
                
                st.markdown("**Maturity Distribution**")
                l0 = st.number_input("L0 Count", min_value=0, value=3)
                l1 = st.number_input("L1 Count", min_value=0, value=8)
                l2 = st.number_input("L2 Count", min_value=0, value=18)
                l3 = st.number_input("L3 Count", min_value=0, value=12)
                l4 = st.number_input("L4 Count", min_value=0, value=5)
                l5 = st.number_input("L5 Count", min_value=0, value=2)
                
                if st.form_submit_button("➕ Add Metrics", type="primary"):
                    try:
                        acceptance_rate = (suggestions_accepted / suggestions_shown * 100) if suggestions_shown > 0 else 0
                        activation_rate = (active_users / enabled_users * 100) if enabled_users > 0 else 0
                        
                        with get_db_session() as session:
                            new_metrics = DailyMetrics(
                                organization_id=org_id,
                                date=metric_date,
                                total_users=total_users,
                                enabled_users=enabled_users,
                                active_users=active_users,
                                weekly_active_users=weekly_active,
                                monthly_active_users=monthly_active,
                                total_suggestions_shown=suggestions_shown,
                                total_suggestions_accepted=suggestions_accepted,
                                acceptance_rate=round(acceptance_rate, 2),
                                activation_rate=round(activation_rate, 2),
                                ai_assisted_commits=ai_commits,
                                ai_assisted_prs=ai_prs,
                                total_commits=total_commits,
                                total_prs=total_prs,
                                l0_count=l0,
                                l1_count=l1,
                                l2_count=l2,
                                l3_count=l3,
                                l4_count=l4,
                                l5_count=l5
                            )
                            session.add(new_metrics)
                        st.success(f"✅ Metrics for {metric_date} added!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
        
        with col2:
            st.markdown("#### Recent Metrics")
            metrics = get_daily_metrics(org_id, limit=30)
            if metrics:
                df = pd.DataFrame(metrics)
                st.dataframe(df, use_container_width=True, height=500)
            else:
                st.info("No metrics found. Add data above.")


# ==================== CLEAR DATA TAB ====================
with tab4:
    st.subheader("🗑️ Clear Data")
    st.warning("⚠️ These actions are irreversible!")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### Clear Users")
        if st.button("🗑️ Delete All Users", type="secondary"):
            with get_db_session() as session:
                session.query(User).delete()
            st.success("✅ All users deleted!")
            st.rerun()
    
    with col2:
        st.markdown("#### Clear Metrics")
        if st.button("🗑️ Delete All Metrics", type="secondary"):
            with get_db_session() as session:
                session.query(DailyMetrics).delete()
            st.success("✅ All metrics deleted!")
            st.rerun()
    
    with col3:
        st.markdown("#### Clear Everything")
        if st.button("🗑️ DELETE ALL DATA", type="primary"):
            with get_db_session() as session:
                session.query(DailyMetrics).delete()
                session.query(User).delete()
                session.query(Organization).delete()
            st.success("✅ All data deleted!")
            st.rerun()


# Footer
st.markdown("---")
st.markdown("💡 **Tip:** Add data here, then view it in the main dashboard.")
st.markdown(f"📁 Database location: `{os.path.abspath('ai_adoption.db')}`")
