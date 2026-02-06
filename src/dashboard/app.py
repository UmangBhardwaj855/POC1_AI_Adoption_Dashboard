

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, date, timedelta
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.config.settings import settings
from src.database.connection import init_database, get_db_session
from src.database.models import Organization, User, DailyMetrics
from src.data_collectors.copilot_api import CopilotAPIClient

# Page configuration
st.set_page_config(
    page_title="AI Adoption Tracker",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Google-style CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Product+Sans:wght@400;500;700&family=Roboto:wght@300;400;500;700&display=swap');
    
    .stApp {
        background-color: #ffffff;
        font-family: 'Roboto', sans-serif;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .google-header {
        background: linear-gradient(135deg, #4285f4 0%, #34a853 50%, #fbbc05 75%, #ea4335 100%);
        padding: 3px;
        border-radius: 16px;
        margin-bottom: 24px;
    }
    
    .google-header-inner {
        background: white;
        border-radius: 14px;
        padding: 28px 36px;
    }
    
    .google-title {
        font-family: 'Roboto', sans-serif;
        font-size: 32px;
        font-weight: 400;
        color: #202124;
        margin: 0;
    }
    
    .google-subtitle {
        font-family: 'Roboto', sans-serif;
        font-size: 14px;
        color: #5f6368;
        margin-top: 6px;
    }
    
    .google-card {
        background: #ffffff;
        border: 1px solid #e8eaed;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 16px;
        box-shadow: 0 1px 3px rgba(60,64,67,0.15);
        transition: box-shadow 0.2s, transform 0.2s;
    }
    
    .google-card:hover {
        box-shadow: 0 4px 12px rgba(60,64,67,0.2);
        transform: translateY(-2px);
    }
    
    .google-card-title {
        font-family: 'Roboto', sans-serif;
        font-size: 16px;
        font-weight: 500;
        color: #202124;
        margin-bottom: 16px;
    }
    
    .metric-card {
        background: #ffffff;
        border: 1px solid #e8eaed;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 1px 3px rgba(60,64,67,0.15);
        transition: all 0.2s;
    }
    
    .metric-card:hover {
        box-shadow: 0 4px 12px rgba(60,64,67,0.2);
        border-color: #4285f4;
    }
    
    .metric-value {
        font-family: 'Roboto', sans-serif;
        font-size: 42px;
        font-weight: 400;
        color: #202124;
        line-height: 1.1;
    }
    
    .metric-label {
        font-family: 'Roboto', sans-serif;
        font-size: 14px;
        color: #5f6368;
        margin-top: 8px;
    }
    
    .metric-delta-positive {
        font-size: 13px;
        color: #34a853;
        font-weight: 500;
        margin-top: 4px;
    }
    
    .metric-delta-negative {
        font-size: 13px;
        color: #ea4335;
        font-weight: 500;
        margin-top: 4px;
    }
    
    .pill-blue { background: #e8f0fe; color: #1967d2; padding: 6px 14px; border-radius: 20px; font-size: 13px; font-weight: 500; display: inline-block; }
    .pill-green { background: #e6f4ea; color: #137333; padding: 6px 14px; border-radius: 20px; font-size: 13px; font-weight: 500; display: inline-block; }
    .pill-yellow { background: #fef7e0; color: #ea8600; padding: 6px 14px; border-radius: 20px; font-size: 13px; font-weight: 500; display: inline-block; }
    .pill-red { background: #fce8e6; color: #c5221f; padding: 6px 14px; border-radius: 20px; font-size: 13px; font-weight: 500; display: inline-block; }
    .pill-purple { background: #f3e8fd; color: #7627bb; padding: 6px 14px; border-radius: 20px; font-size: 13px; font-weight: 500; display: inline-block; }
    
    .progress-container {
        background: #e8eaed;
        border-radius: 8px;
        height: 10px;
        margin: 12px 0;
        overflow: hidden;
    }
    
    .phase-card {
        background: #ffffff;
        border: 1px solid #e8eaed;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 12px;
        transition: all 0.2s;
    }
    
    .phase-card:hover {
        border-color: #4285f4;
        box-shadow: 0 2px 8px rgba(66, 133, 244, 0.15);
    }
    
    .phase-title {
        font-family: 'Roboto', sans-serif;
        font-size: 15px;
        font-weight: 500;
        color: #202124;
    }
    
    .phase-status {
        font-size: 12px;
        color: #5f6368;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background-color: #f8f9fa;
        padding: 6px;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 8px;
        color: #5f6368;
        font-family: 'Roboto', sans-serif;
        font-weight: 500;
        padding: 10px 20px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #ffffff;
        color: #1967d2;
        box-shadow: 0 1px 3px rgba(60,64,67,0.15);
    }
    
    .google-footer {
        text-align: center;
        padding: 32px;
        color: #5f6368;
        font-size: 13px;
        margin-top: 48px;
        border-top: 1px solid #e8eaed;
    }
    
    .maturity-l0 { background: #fce8e6; color: #c5221f; padding: 4px 12px; border-radius: 16px; font-size: 12px; font-weight: 500; }
    .maturity-l1 { background: #fef7e0; color: #ea8600; padding: 4px 12px; border-radius: 16px; font-size: 12px; font-weight: 500; }
    .maturity-l2 { background: #e8f0fe; color: #1967d2; padding: 4px 12px; border-radius: 16px; font-size: 12px; font-weight: 500; }
    .maturity-l3 { background: #e6f4ea; color: #137333; padding: 4px 12px; border-radius: 16px; font-size: 12px; font-weight: 500; }
    .maturity-l4 { background: #e6f4ea; color: #0d652d; padding: 4px 12px; border-radius: 16px; font-size: 12px; font-weight: 500; }
    .maturity-l5 { background: #f3e8fd; color: #7627bb; padding: 4px 12px; border-radius: 16px; font-size: 12px; font-weight: 500; }
</style>
""", unsafe_allow_html=True)


def check_database_has_data():
    """Check if database has any data."""
    try:
        init_database()
        with get_db_session() as session:
            org_count = session.query(Organization).count()
            user_count = session.query(User).count()
            metrics_count = session.query(DailyMetrics).count()
            return org_count > 0 and user_count > 0 and metrics_count > 0
    except Exception as e:
        print(f"Error checking database: {e}")
        return False


def get_metrics_data():
    """Get metrics data from database."""
    try:
        with get_db_session() as session:
            latest_obj = session.query(DailyMetrics).order_by(DailyMetrics.date.desc()).first()
            
            latest = None
            if latest_obj:
                latest = {
                    'date': latest_obj.date,
                    'total_users': latest_obj.total_users,
                    'enabled_users': latest_obj.enabled_users,
                    'active_users': latest_obj.active_users,
                    'weekly_active_users': latest_obj.weekly_active_users,
                    'monthly_active_users': latest_obj.monthly_active_users,
                    'total_suggestions_shown': latest_obj.total_suggestions_shown,
                    'total_suggestions_accepted': latest_obj.total_suggestions_accepted,
                    'total_lines_suggested': latest_obj.total_lines_suggested,
                    'total_lines_accepted': latest_obj.total_lines_accepted,
                    'total_chat_interactions': latest_obj.total_chat_interactions or 0,
                    'acceptance_rate': latest_obj.acceptance_rate,
                    'activation_rate': latest_obj.activation_rate,
                    'ai_assisted_commits': latest_obj.ai_assisted_commits,
                    'ai_assisted_prs': latest_obj.ai_assisted_prs,
                    'total_commits': latest_obj.total_commits,
                    'total_prs': latest_obj.total_prs,
                    'ai_code_lines': latest_obj.ai_code_lines,
                    'ai_code_modified': latest_obj.ai_code_modified,
                    'ai_code_retention_rate': latest_obj.ai_code_retention_rate,
                    'l0_count': latest_obj.l0_count,
                    'l1_count': latest_obj.l1_count,
                    'l2_count': latest_obj.l2_count,
                    'l3_count': latest_obj.l3_count,
                    'l4_count': latest_obj.l4_count,
                    'l5_count': latest_obj.l5_count,
                }
            
            trend_objs = session.query(DailyMetrics).order_by(DailyMetrics.date).all()
            trend = [{
                'date': t.date,
                'total_users': t.total_users,
                'enabled_users': t.enabled_users,
                'active_users': t.active_users,
                'weekly_active_users': t.weekly_active_users,
                'monthly_active_users': t.monthly_active_users,
                'acceptance_rate': t.acceptance_rate,
                'activation_rate': t.activation_rate,
                'ai_assisted_commits': t.ai_assisted_commits,
                'ai_assisted_prs': t.ai_assisted_prs,
                'total_commits': t.total_commits,
                'total_prs': t.total_prs,
                'ai_code_retention_rate': t.ai_code_retention_rate,
                'l0_count': t.l0_count,
                'l1_count': t.l1_count,
                'l2_count': t.l2_count,
                'l3_count': t.l3_count,
                'l4_count': t.l4_count,
                'l5_count': t.l5_count,
            } for t in trend_objs]
            
            user_objs = session.query(User).all()
            users = [{
                'github_username': u.github_username,
                'name': u.name,
                'team': u.team,
                'copilot_enabled': u.copilot_enabled,
                'maturity_level': u.maturity_level,
                'is_weekly_active': u.is_weekly_active,
                'is_monthly_active': u.is_monthly_active,
            } for u in user_objs]
            
            return latest, trend, users
    except Exception as e:
        print(f"Error getting metrics: {e}")
        return None, [], []


def render_header():
    """Render Google-style header."""
    st.markdown("""
    <div class="google-header">
        <div class="google-header-inner">
            <h1 class="google-title">
                <span style="color: #4285f4;">A</span><span style="color: #ea4335;">I</span> 
                <span style="color: #fbbc05;">Adoption</span> 
                <span style="color: #34a853;">Tracker</span>
            </h1>
            <p class="google-subtitle">Engineering Division • Q1 2026 • Real-time Copilot Metrics Dashboard</p>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_executive_summary(latest, users):
    """Render executive summary."""
    if not latest:
        st.warning("⚠️ No metrics data available.")
        return
    
    total = latest['l0_count'] + latest['l1_count'] + latest['l2_count'] + latest['l3_count'] + latest['l4_count'] + latest['l5_count']
    l2_plus = latest['l2_count'] + latest['l3_count'] + latest['l4_count'] + latest['l5_count']
    l2_plus_pct = round((l2_plus / total) * 100) if total > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
                <span class="pill-blue">L2</span>
                <span style="color: #5f6368; font-size: 13px;">Current Level</span>
            </div>
            <div class="metric-value" style="font-size: 28px;">Organization</div>
            <div class="metric-label">Maturity Level</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{latest['total_users']}</div>
            <div class="metric-label">Total Engineers</div>
            <div class="metric-delta-positive">↑ {latest['enabled_users']} enabled</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{l2_plus_pct}%</div>
            <div class="metric-label">Active Users (L2+)</div>
            <div class="metric-delta-positive">↑ Target: 60%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">9/14</div>
            <div class="metric-label">KOIs Achieved</div>
            <span class="pill-green" style="margin-top: 8px;">On Track</span>
        </div>
        """, unsafe_allow_html=True)


def render_phase_progression(latest):
    """Render phase progression."""
    st.markdown("### 📈 Phase Progression")
    
    phases = [
        {"name": "User Adoption", "desc": "Getting developers to use AI tools", "progress": 65, "status": "In Progress", "color": "#4285f4"},
        {"name": "Behavioral Adoption", "desc": "Transitioning to real work", "progress": 42, "status": "In Progress", "color": "#fbbc05"},
        {"name": "Sustained Adoption", "desc": "Making AI usage habitual", "progress": 18, "status": "Starting", "color": "#ea4335"},
        {"name": "Outcome Adoption", "desc": "Proving business value", "progress": 5, "status": "Pending", "color": "#5f6368"},
    ]
    
    cols = st.columns(4)
    for i, phase in enumerate(phases):
        with cols[i]:
            status_color = "#34a853" if phase["status"] == "In Progress" else "#5f6368"
            st.markdown(f"""
            <div class="phase-card">
                <div class="phase-title">{phase['name']}</div>
                <div class="phase-status" style="color: {status_color};">● {phase['status']}</div>
                <p style="font-size: 12px; color: #5f6368; margin: 8px 0;">{phase['desc']}</p>
                <div class="progress-container">
                    <div style="background: {phase['color']}; height: 100%; width: {phase['progress']}%; border-radius: 8px;"></div>
                </div>
                <div style="font-size: 28px; font-weight: 500; color: #202124;">{phase['progress']}%</div>
            </div>
            """, unsafe_allow_html=True)


def render_maturity_distribution(latest):
    """Render maturity distribution."""
    st.markdown("### 👥 Maturity Distribution")
    
    levels = ['L0', 'L1', 'L2', 'L3', 'L4', 'L5']
    counts = [latest['l0_count'], latest['l1_count'], latest['l2_count'], 
              latest['l3_count'], latest['l4_count'], latest['l5_count']]
    colors = ['#ea4335', '#fbbc05', '#4285f4', '#34a853', '#0d652d', '#7627bb']
    total = sum(counts)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=levels,
        x=counts,
        orientation='h',
        marker_color=colors,
        text=[f'{c} ({round(c/total*100)}%)' for c in counts],
        textposition='outside'
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Roboto', size=13, color='#202124'),
        height=320,
        margin=dict(l=50, r=80, t=20, b=20),
        xaxis=dict(showgrid=True, gridcolor='#e8eaed', zeroline=False),
        yaxis=dict(showgrid=False)
    )
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("""
        <div class="google-card">
            <div class="google-card-title">Maturity Levels Guide</div>
            <div style="font-size: 13px; line-height: 2;">
                <p><span class="maturity-l0">L0</span> Not Enabled</p>
                <p><span class="maturity-l1">L1</span> Enabled, minimal use</p>
                <p><span class="maturity-l2">L2</span> Regular usage</p>
                <p><span class="maturity-l3">L3</span> AI in real work</p>
                <p><span class="maturity-l4">L4</span> Habitual usage</p>
                <p><span class="maturity-l5">L5</span> Business outcomes</p>
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_adoption_tab(trend, latest):
    """Render adoption tab."""
    st.markdown("### 📊 Adoption Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Activation Rate", f"{latest['activation_rate']}%", "+8% this month")
    with col2:
        st.metric("Weekly Active Users", latest['weekly_active_users'], "+5")
    with col3:
        st.metric("Monthly Active Users", latest['monthly_active_users'], "+12")
    with col4:
        st.metric("Enabled Users", latest['enabled_users'], f"/{latest['total_users']}")
    
    if trend:
        df = pd.DataFrame(trend)
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig.add_trace(go.Scatter(x=df['date'], y=df['active_users'], name='Active Users', 
                                  line=dict(color='#4285f4', width=3)), secondary_y=False)
        fig.add_trace(go.Scatter(x=df['date'], y=df['activation_rate'], name='Activation Rate %',
                                  line=dict(color='#34a853', width=2, dash='dot')), secondary_y=True)
        
        fig.update_layout(
            title='User Adoption Trend (Last 30 Days)',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Roboto'),
            height=400,
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            hovermode='x unified'
        )
        fig.update_xaxes(showgrid=True, gridcolor='#e8eaed')
        fig.update_yaxes(showgrid=True, gridcolor='#e8eaed')
        
        st.plotly_chart(fig, use_container_width=True)


def render_productivity_tab(trend, latest):
    """Render productivity tab."""
    st.markdown("### ⚡ Productivity Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Acceptance Rate", f"{latest['acceptance_rate']}%", "+2.5%")
    with col2:
        ai_commit_rate = round((latest['ai_assisted_commits'] / latest['total_commits']) * 100) if latest['total_commits'] > 0 else 0
        st.metric("AI-Assisted Commits", f"{ai_commit_rate}%", f"{latest['ai_assisted_commits']}/{latest['total_commits']}")
    with col3:
        ai_pr_rate = round((latest['ai_assisted_prs'] / latest['total_prs']) * 100) if latest['total_prs'] > 0 else 0
        st.metric("AI-Assisted PRs", f"{ai_pr_rate}%", f"{latest['ai_assisted_prs']}/{latest['total_prs']}")
    with col4:
        st.metric("Chat Interactions", latest['total_chat_interactions'], "+15")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if trend:
            df = pd.DataFrame(trend)
            fig = go.Figure()
            fig.add_trace(go.Bar(x=df['date'], y=df['ai_assisted_commits'], name='AI Commits', marker_color='#4285f4'))
            fig.add_trace(go.Bar(x=df['date'], y=[t['total_commits'] - t['ai_assisted_commits'] for t in trend], name='Manual Commits', marker_color='#e8eaed'))
            
            fig.update_layout(title='AI vs Manual Commits', barmode='stack', paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)', font=dict(family='Roboto'), height=350,
                            legend=dict(orientation="h", yanchor="bottom", y=1.02))
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if trend:
            df = pd.DataFrame(trend)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df['date'], y=df['acceptance_rate'], mode='lines+markers',
                                    name='Acceptance Rate', line=dict(color='#34a853', width=3),
                                    fill='tozeroy', fillcolor='rgba(52, 168, 83, 0.1)'))
            
            fig.update_layout(title='Code Suggestion Acceptance Rate', paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)', font=dict(family='Roboto'), height=350,
                            yaxis=dict(range=[0, 100]))
            st.plotly_chart(fig, use_container_width=True)


def render_quality_tab(trend, latest):
    """Render quality tab."""
    st.markdown("### 🎯 Code Quality Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Code Retention Rate", f"{latest['ai_code_retention_rate']}%", "+1.2%")
    with col2:
        mod_rate = 100 - latest['ai_code_retention_rate']
        st.metric("Modification Rate", f"{round(mod_rate, 1)}%", "Lower is better", delta_color="inverse")
    with col3:
        st.metric("AI Code Lines", f"{latest['ai_code_lines']:,}", "+350")
    with col4:
        st.metric("Lines Modified", f"{latest['ai_code_modified']:,}", "After generation")
    
    if trend:
        df = pd.DataFrame(trend)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['date'], y=df['ai_code_retention_rate'], mode='lines+markers',
                                name='Retention Rate', line=dict(color='#4285f4', width=3),
                                fill='tozeroy', fillcolor='rgba(66, 133, 244, 0.1)'))
        fig.add_hline(y=90, line_dash="dash", line_color="#34a853", annotation_text="Target: 90%")
        
        fig.update_layout(title='AI Code Retention Rate Over Time', paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)', font=dict(family='Roboto'), height=400,
                        yaxis=dict(range=[80, 100]))
        st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="google-card">
            <div class="google-card-title">📊 Quality Indicators</div>
            <table style="width: 100%; font-size: 14px;">
                <tr style="border-bottom: 1px solid #e8eaed;"><td style="padding: 12px 0;">Code passing first review</td><td style="text-align: right;"><span class="pill-green">85%</span></td></tr>
                <tr style="border-bottom: 1px solid #e8eaed;"><td style="padding: 12px 0;">Tests passing on first run</td><td style="text-align: right;"><span class="pill-green">78%</span></td></tr>
                <tr style="border-bottom: 1px solid #e8eaed;"><td style="padding: 12px 0;">No bugs in 7 days</td><td style="text-align: right;"><span class="pill-blue">92%</span></td></tr>
                <tr><td style="padding: 12px 0;">Security issues</td><td style="text-align: right;"><span class="pill-green">0</span></td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="google-card">
            <div class="google-card-title">🔍 MCP Tracking Impact</div>
            <p style="font-size: 13px; color: #5f6368; margin-bottom: 16px;">AI-assisted actions via GitHub MCP Server</p>
            <table style="width: 100%; font-size: 14px;">
                <tr style="border-bottom: 1px solid #e8eaed;"><td style="padding: 12px 0;">🔗 commit_create</td><td style="text-align: right; font-weight: 500;">78</td></tr>
                <tr style="border-bottom: 1px solid #e8eaed;"><td style="padding: 12px 0;">🔀 pr_create</td><td style="text-align: right; font-weight: 500;">34</td></tr>
                <tr style="border-bottom: 1px solid #e8eaed;"><td style="padding: 12px 0;">🌿 branch_create</td><td style="text-align: right; font-weight: 500;">45</td></tr>
                <tr><td style="padding: 12px 0;">⬆️ code_push</td><td style="text-align: right; font-weight: 500;">89</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)


def render_users_tab(users):
    """Render users tab."""
    st.markdown("### 👤 User Details")
    
    if not users:
        st.info("No user data available.")
        return
    
    df = pd.DataFrame(users)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        team_filter = st.selectbox("Filter by Team", ["All"] + list(df['team'].unique()))
    with col2:
        level_filter = st.selectbox("Filter by Level", ["All", "L0", "L1", "L2", "L3", "L4", "L5"])
    with col3:
        status_filter = st.selectbox("Filter by Status", ["All", "Enabled", "Weekly Active", "Monthly Active"])
    
    filtered_df = df.copy()
    if team_filter != "All":
        filtered_df = filtered_df[filtered_df['team'] == team_filter]
    if level_filter != "All":
        filtered_df = filtered_df[filtered_df['maturity_level'] == int(level_filter[1])]
    if status_filter == "Enabled":
        filtered_df = filtered_df[filtered_df['copilot_enabled'] == True]
    elif status_filter == "Weekly Active":
        filtered_df = filtered_df[filtered_df['is_weekly_active'] == True]
    elif status_filter == "Monthly Active":
        filtered_df = filtered_df[filtered_df['is_monthly_active'] == True]
    
    st.markdown(f"**Showing {len(filtered_df)} of {len(df)} users**")
    
    display_df = filtered_df.copy()
    display_df['Level'] = display_df['maturity_level'].apply(lambda x: f'L{x}')
    display_df['Status'] = display_df.apply(
        lambda row: '🟢 Active' if row['is_weekly_active'] else ('🟡 Enabled' if row['copilot_enabled'] else '⚪ Not Enabled'), axis=1)
    
    display_df = display_df[['name', 'team', 'Level', 'Status', 'is_weekly_active', 'is_monthly_active']]
    display_df.columns = ['Name', 'Team', 'Level', 'Status', 'Weekly Active', 'Monthly Active']
    
    st.dataframe(display_df, use_container_width=True, height=400)


def render_footer():
    """Render footer."""
    st.markdown("""
    <div class="google-footer">
        <p>AI Adoption Tracker • Developed by Umang Bhardwaj • Powered by GitHub Copilot Metrics API & MCP</p>
        <p style="margin-top: 8px;">© 2026 Engineering Division</p>
    </div>
    """, unsafe_allow_html=True)


def fetch_live_data():
    """Fetch live data from GitHub Copilot API."""
    try:
        client = CopilotAPIClient()
        
        # Test connection first
        conn_test = client.test_connection()
        if conn_test["status"] == "error":
            return None, None, None, conn_test["error"]
        
        # Get billing/seat info
        billing = client.get_copilot_billing()
        seat_breakdown = billing.get("seat_breakdown", {})
        total_seats = seat_breakdown.get("total", 0)
        active_seats = seat_breakdown.get("active_this_cycle", 0)
        inactive_seats = seat_breakdown.get("inactive_this_cycle", 0)
        
        # Get usage summary
        usage = client.get_usage_summary(days=28)
        
        # Get all seats (users)
        seats = client.get_all_copilot_seats()
        
        # Build latest metrics dict
        acceptance_rate = usage.get("acceptance_rate", 0)
        activation_rate = round((active_seats / total_seats * 100) if total_seats > 0 else 0, 2)
        
        # Estimate maturity levels based on activity
        # L0: No Copilot, L1: Enabled but inactive, L2-L5: Active with varying engagement
        l0_count = 0  # We only get Copilot users
        l1_count = inactive_seats
        active_breakdown = active_seats
        # Distribute active users across L2-L5 based on typical adoption curve
        l2_count = int(active_breakdown * 0.4)  # 40% basic usage
        l3_count = int(active_breakdown * 0.3)  # 30% regular
        l4_count = int(active_breakdown * 0.2)  # 20% proficient
        l5_count = active_breakdown - l2_count - l3_count - l4_count  # Rest are champions
        
        latest = {
            'date': date.today(),
            'total_users': total_seats,
            'enabled_users': total_seats,
            'active_users': active_seats,
            'weekly_active_users': int(active_seats * 0.8),
            'monthly_active_users': active_seats,
            'total_suggestions_shown': usage.get("total_suggestions", 0),
            'total_suggestions_accepted': usage.get("total_acceptances", 0),
            'total_lines_suggested': usage.get("total_lines_suggested", 0),
            'total_lines_accepted': usage.get("total_lines_accepted", 0),
            'total_chat_interactions': 0,
            'acceptance_rate': acceptance_rate,
            'activation_rate': activation_rate,
            'ai_assisted_commits': 0,  # Not available from API
            'ai_assisted_prs': 0,
            'total_commits': 0,
            'total_prs': 0,
            'ai_code_lines': usage.get("total_lines_accepted", 0),
            'ai_code_modified': 0,
            'ai_code_retention_rate': 85.0,  # Estimated
            'l0_count': l0_count,
            'l1_count': l1_count,
            'l2_count': l2_count,
            'l3_count': l3_count,
            'l4_count': l4_count,
            'l5_count': l5_count,
        }
        
        # Build trend data (single day for now)
        trend = [latest]
        
        # Build users list from seats
        users = []
        for seat in seats:
            # Determine maturity level based on activity
            if seat.last_activity_at:
                days_since_activity = (datetime.now(seat.last_activity_at.tzinfo) - seat.last_activity_at).days if seat.last_activity_at.tzinfo else (datetime.now() - seat.last_activity_at.replace(tzinfo=None)).days
                if days_since_activity <= 1:
                    level = 4
                elif days_since_activity <= 7:
                    level = 3
                elif days_since_activity <= 14:
                    level = 2
                else:
                    level = 1
            else:
                level = 1
            
            users.append({
                'github_username': seat.login,
                'name': seat.login,
                'team': 'Unknown',
                'copilot_enabled': True,
                'maturity_level': level,
                'is_weekly_active': level >= 3,
                'is_monthly_active': level >= 2,
                'last_activity': seat.last_activity_at.strftime('%Y-%m-%d') if seat.last_activity_at else 'Never',
                'editor': seat.last_activity_editor or 'Unknown'
            })
        
        return latest, trend, users, None
    
    except Exception as e:
        return None, None, None, str(e)


def render_data_source_selector():
    """Render data source selector and connection status."""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        data_source = st.radio(
            "📊 Data Source",
            ["🔴 Live (GitHub API)", "🟢 Demo Data"],
            horizontal=True,
            key="data_source"
        )
    
    with col2:
        if "🔴 Live" in data_source:
            if settings.github_token and settings.github_org:
                st.markdown(f'<span class="pill-green">✓ Connected to {settings.github_org}</span>', unsafe_allow_html=True)
            else:
                st.markdown('<span class="pill-red">⚠️ Missing credentials</span>', unsafe_allow_html=True)
    
    return "live" if "Live" in data_source else "demo"


def main():
    """Main application."""
    # Initialize database
    init_database()
    
    render_header()
    
    # Check if database has data
    has_data = check_database_has_data()
    
    if not has_data:
        st.warning("⚠️ **No data in database!** Please add data using the Admin Panel.")
        st.info("👉 Run `streamlit run src/dashboard/admin.py` to open the Admin Panel and add organizations, users, and metrics.")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            ### How to add data:
            1. Open Admin Panel: `streamlit run src/dashboard/admin.py --server.port=8503`
            2. Add an **Organization** (e.g., 'xoriant')
            3. Add **Users** with their maturity levels
            4. Add **Daily Metrics** data
            5. Refresh this dashboard
            """)
        with col2:
            st.markdown("""
            ### Database Info:
            - **Database:** SQLite
            - **Location:** `ai_adoption.db`
            - **Tables:** organizations, users, daily_metrics
            """)
        return
    
    st.markdown("---")
    
    # Load data from database
    latest, trend, users = get_metrics_data()
    
    if latest:
        st.success("✅ Data loaded from database")
    
    render_executive_summary(latest, users)
    
    if latest:
        st.markdown("---")
        render_phase_progression(latest)
        
        st.markdown("---")
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Overview", "👥 Adoption", "⚡ Productivity", "🎯 Quality", "👤 Users"])
        
        with tab1:
            render_maturity_distribution(latest)
        with tab2:
            render_adoption_tab(trend, latest)
        with tab3:
            render_productivity_tab(trend, latest)
        with tab4:
            render_quality_tab(trend, latest)
        with tab5:
            render_users_tab(users)
    
    render_footer()


if __name__ == "__main__":
    main()
