"""
POC 1: AI Adoption Metrics Dashboard
Productivity Metrics Calculator

Calculates productivity-related metrics from AI-assisted development.
"""

from datetime import datetime, date, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass

from ..data_collectors.copilot_api import CopilotAPIClient
from ..data_collectors.git_analyzer import GitAnalyzer
from ..mcp.event_tracker import MCPEventTracker, MCPEventType
from ..database.models import DailyMetrics, UserActivityLog
from ..database.connection import get_db_session


@dataclass
class ProductivityMetrics:
    """Productivity metrics data class."""
    date: date
    period_days: int
    
    # Copilot Usage
    total_suggestions: int
    accepted_suggestions: int
    acceptance_rate: float
    total_lines_suggested: int
    lines_accepted: int
    lines_acceptance_rate: float
    
    # AI-Assisted Actions (from MCP)
    ai_assisted_commits: int
    ai_assisted_prs: int
    ai_file_operations: int
    
    # Overall Activity
    total_commits: int
    total_prs: int
    ai_commit_percentage: float
    ai_pr_percentage: float
    
    # Lines of Code
    total_loc_added: int
    ai_loc_added: int
    ai_loc_percentage: float


class ProductivityMetricsCalculator:
    """Calculator for productivity metrics."""
    
    def __init__(
        self,
        copilot_client: CopilotAPIClient = None,
        git_analyzer: GitAnalyzer = None,
        mcp_tracker: MCPEventTracker = None
    ):
        """
        Initialize productivity metrics calculator.
        
        Args:
            copilot_client: Copilot API client
            git_analyzer: Git repository analyzer
            mcp_tracker: MCP event tracker
        """
        self.copilot_client = copilot_client
        self.git_analyzer = git_analyzer
        self.mcp_tracker = mcp_tracker
    
    def get_productivity_metrics(self, days: int = 7) -> ProductivityMetrics:
        """
        Get productivity metrics for the specified period.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            ProductivityMetrics object
        """
        since_date = date.today() - timedelta(days=days)
        since_datetime = datetime.combine(since_date, datetime.min.time())
        
        metrics = ProductivityMetrics(
            date=date.today(),
            period_days=days,
            total_suggestions=0,
            accepted_suggestions=0,
            acceptance_rate=0.0,
            total_lines_suggested=0,
            lines_accepted=0,
            lines_acceptance_rate=0.0,
            ai_assisted_commits=0,
            ai_assisted_prs=0,
            ai_file_operations=0,
            total_commits=0,
            total_prs=0,
            ai_commit_percentage=0.0,
            ai_pr_percentage=0.0,
            total_loc_added=0,
            ai_loc_added=0,
            ai_loc_percentage=0.0
        )
        
        # Get Copilot usage data
        if self.copilot_client:
            try:
                usage = self.copilot_client.get_usage_summary(days=days)
                
                metrics.total_suggestions = usage.get("total_suggestions", 0)
                metrics.accepted_suggestions = usage.get("total_acceptances", 0)
                metrics.acceptance_rate = usage.get("acceptance_rate", 0.0)
                metrics.total_lines_suggested = usage.get("total_lines_suggested", 0)
                metrics.lines_accepted = usage.get("total_lines_accepted", 0)
                metrics.lines_acceptance_rate = usage.get("lines_acceptance_rate", 0.0)
                
                # Estimate AI LOC from accepted lines
                metrics.ai_loc_added = metrics.lines_accepted
                
            except Exception as e:
                print(f"Error fetching Copilot usage: {e}")
        
        # Get MCP metrics
        if self.mcp_tracker:
            try:
                mcp_metrics = self.mcp_tracker.get_metrics(since=since_datetime)
                
                metrics.ai_assisted_commits = mcp_metrics.get("ai_commits", 0)
                metrics.ai_assisted_prs = mcp_metrics.get("ai_pull_requests", 0)
                metrics.ai_file_operations = mcp_metrics.get("ai_file_operations", 0)
                
            except Exception as e:
                print(f"Error fetching MCP metrics: {e}")
        
        # Get Git metrics
        if self.git_analyzer:
            try:
                git_stats = self.git_analyzer.get_commit_stats(since=since_date)
                
                metrics.total_commits = git_stats.get("total_commits", 0)
                metrics.total_loc_added = git_stats.get("total_insertions", 0)
                
                # AI commits from git analysis
                ai_commits_git = git_stats.get("ai_assisted_commits", 0)
                metrics.ai_assisted_commits = max(metrics.ai_assisted_commits, ai_commits_git)
                
            except Exception as e:
                print(f"Error fetching Git stats: {e}")
        
        # Calculate percentages
        if metrics.total_commits > 0:
            metrics.ai_commit_percentage = round(
                (metrics.ai_assisted_commits / metrics.total_commits) * 100, 2
            )
        
        if metrics.total_prs > 0:
            metrics.ai_pr_percentage = round(
                (metrics.ai_assisted_prs / metrics.total_prs) * 100, 2
            )
        
        if metrics.total_loc_added > 0:
            metrics.ai_loc_percentage = round(
                (metrics.ai_loc_added / metrics.total_loc_added) * 100, 2
            )
        
        return metrics
    
    def get_productivity_by_user(self, days: int = 7) -> Dict[str, Dict]:
        """
        Get productivity metrics broken down by user.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dict with user-level metrics
        """
        users = {}
        since_datetime = datetime.utcnow() - timedelta(days=days)
        
        # Get from MCP tracker
        if self.mcp_tracker:
            try:
                mcp_metrics = self.mcp_tracker.get_metrics(since=since_datetime)
                
                for username, count in mcp_metrics.get("events_by_user", {}).items():
                    if username not in users:
                        users[username] = {
                            "total_events": 0,
                            "commits": 0,
                            "prs": 0,
                            "file_ops": 0
                        }
                    users[username]["total_events"] = count
                
                # Get detailed per-user activity
                for username in list(users.keys()):
                    activity = self.mcp_tracker.get_user_activity(username, days=days)
                    users[username].update({
                        "commits": activity.get("commits", 0),
                        "prs": activity.get("pull_requests", 0),
                        "file_ops": activity.get("file_operations", 0)
                    })
                    
            except Exception as e:
                print(f"Error fetching user MCP data: {e}")
        
        # Supplement from database
        try:
            with get_db_session() as session:
                since_date = date.today() - timedelta(days=days)
                
                activity_logs = session.query(UserActivityLog).filter(
                    UserActivityLog.date >= since_date
                ).all()
                
                for log in activity_logs:
                    user = log.user
                    if user and user.github_username:
                        username = user.github_username
                        if username not in users:
                            users[username] = {
                                "total_events": 0,
                                "commits": 0,
                                "prs": 0,
                                "file_ops": 0
                            }
                        users[username]["commits"] += log.commits_count
                        users[username]["prs"] += log.prs_created
                        
        except Exception as e:
            print(f"Error fetching user database data: {e}")
        
        return users
    
    def get_productivity_trend(self, days: int = 30) -> List[Dict]:
        """
        Get productivity trend over time.
        
        Args:
            days: Number of days to include
            
        Returns:
            List of daily productivity metrics
        """
        trend = []
        
        try:
            with get_db_session() as session:
                since_date = date.today() - timedelta(days=days)
                
                daily_metrics = session.query(DailyMetrics).filter(
                    DailyMetrics.date >= since_date
                ).order_by(DailyMetrics.date).all()
                
                for dm in daily_metrics:
                    trend.append({
                        "date": dm.date.isoformat(),
                        "suggestions_shown": dm.total_suggestions_shown,
                        "suggestions_accepted": dm.total_suggestions_accepted,
                        "acceptance_rate": dm.acceptance_rate,
                        "ai_commits": dm.ai_assisted_commits,
                        "total_commits": dm.total_commits,
                        "ai_prs": dm.ai_assisted_prs,
                        "total_prs": dm.total_prs
                    })
        except Exception as e:
            print(f"Error fetching productivity trend: {e}")
        
        return trend
    
    def get_language_productivity(self, days: int = 7) -> Dict[str, Dict]:
        """
        Get productivity metrics broken down by programming language.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dict with language-level metrics
        """
        languages = {}
        
        if self.copilot_client:
            try:
                usage = self.copilot_client.get_usage_summary(days=days)
                
                for lang, data in usage.get("language_breakdown", {}).items():
                    suggestions = data.get("suggestions_shown", 0)
                    accepted = data.get("suggestions_accepted", 0)
                    
                    languages[lang] = {
                        "suggestions_shown": suggestions,
                        "suggestions_accepted": accepted,
                        "acceptance_rate": round(
                            (accepted / suggestions * 100) if suggestions > 0 else 0, 2
                        ),
                        "lines_suggested": data.get("lines_suggested", 0),
                        "lines_accepted": data.get("lines_accepted", 0)
                    }
                    
            except Exception as e:
                print(f"Error fetching language productivity: {e}")
        
        return languages
    
    def calculate_kois(self) -> Dict:
        """
        Calculate Key Outcome Indicators for productivity.
        
        Returns:
            Dict with KOI status
        """
        metrics = self.get_productivity_metrics(days=7)
        
        kois = {
            "acceptance_rate": {
                "name": "Code Acceptance Rate",
                "target": 30.0,
                "current": metrics.acceptance_rate,
                "achieved": metrics.acceptance_rate >= 30.0,
                "unit": "%",
                "description": "Percentage of Copilot suggestions accepted"
            },
            "ai_commit_rate": {
                "name": "AI-Assisted Commit Rate",
                "target": 20.0,
                "current": metrics.ai_commit_percentage,
                "achieved": metrics.ai_commit_percentage >= 20.0,
                "unit": "%",
                "description": "Percentage of commits with AI assistance"
            },
            "ai_loc_rate": {
                "name": "AI-Generated LOC Rate",
                "target": 25.0,
                "current": metrics.ai_loc_percentage,
                "achieved": metrics.ai_loc_percentage >= 25.0,
                "unit": "%",
                "description": "Percentage of code lines generated by AI"
            },
            "weekly_ai_commits": {
                "name": "Weekly AI Commits",
                "target": 50,
                "current": metrics.ai_assisted_commits,
                "achieved": metrics.ai_assisted_commits >= 50,
                "unit": "commits",
                "description": "Number of AI-assisted commits per week"
            }
        }
        
        return kois


def get_productivity_calculator(
    copilot_client: CopilotAPIClient = None,
    git_analyzer: GitAnalyzer = None,
    mcp_tracker: MCPEventTracker = None
) -> ProductivityMetricsCalculator:
    """Get productivity metrics calculator instance."""
    return ProductivityMetricsCalculator(copilot_client, git_analyzer, mcp_tracker)
