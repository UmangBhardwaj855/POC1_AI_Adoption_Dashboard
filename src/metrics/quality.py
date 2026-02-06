"""
POC 1: AI Adoption Metrics Dashboard
Quality Metrics Calculator

Calculates code quality metrics for AI-generated code.
"""

from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from ..data_collectors.git_analyzer import GitAnalyzer, CodeQualityReport
from ..database.models import CodeQualityMetric, DailyMetrics
from ..database.connection import get_db_session


@dataclass
class QualityMetrics:
    """Quality metrics data class."""
    date: date
    period_days: int
    
    # Code Retention
    ai_code_lines_total: int
    ai_code_lines_unchanged: int
    code_retention_rate: float  # % of AI code that remains unchanged
    
    # Code Modification
    ai_code_modified: int
    modification_rate: float  # % of AI code that was modified
    avg_days_to_modification: float
    
    # Bug/Fix Tracking
    ai_code_bugs: int
    bug_rate: float  # bugs per 1000 lines of AI code
    
    # PR Quality
    ai_prs_total: int
    ai_prs_rejected: int
    pr_rejection_rate: float
    
    # Review Feedback
    avg_review_comments_ai: float
    avg_review_comments_manual: float


class QualityMetricsCalculator:
    """Calculator for code quality metrics."""
    
    # Modification reasons
    MODIFICATION_REASONS = {
        "bug_fix": "Bug Fix",
        "refactor": "Refactoring",
        "feature": "Feature Enhancement",
        "style": "Style/Formatting",
        "performance": "Performance Improvement",
        "security": "Security Fix",
        "other": "Other"
    }
    
    def __init__(self, git_analyzer: GitAnalyzer = None):
        """
        Initialize quality metrics calculator.
        
        Args:
            git_analyzer: Git repository analyzer
        """
        self.git_analyzer = git_analyzer
    
    def get_quality_metrics(self, days: int = 30) -> QualityMetrics:
        """
        Get quality metrics for the specified period.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            QualityMetrics object
        """
        metrics = QualityMetrics(
            date=date.today(),
            period_days=days,
            ai_code_lines_total=0,
            ai_code_lines_unchanged=0,
            code_retention_rate=0.0,
            ai_code_modified=0,
            modification_rate=0.0,
            avg_days_to_modification=0.0,
            ai_code_bugs=0,
            bug_rate=0.0,
            ai_prs_total=0,
            ai_prs_rejected=0,
            pr_rejection_rate=0.0,
            avg_review_comments_ai=0.0,
            avg_review_comments_manual=0.0
        )
        
        # Get from Git analyzer
        if self.git_analyzer:
            try:
                quality_report = self.git_analyzer.analyze_code_quality(days=days)
                
                metrics.ai_code_lines_total = quality_report.ai_lines_added
                metrics.modification_rate = quality_report.modification_rate
                
                # Estimate unchanged lines
                estimated_modified = int(metrics.ai_code_lines_total * (metrics.modification_rate / 100))
                metrics.ai_code_modified = estimated_modified
                metrics.ai_code_lines_unchanged = metrics.ai_code_lines_total - estimated_modified
                
                if metrics.ai_code_lines_total > 0:
                    metrics.code_retention_rate = round(
                        (metrics.ai_code_lines_unchanged / metrics.ai_code_lines_total) * 100, 2
                    )
                    
            except Exception as e:
                print(f"Error analyzing Git quality: {e}")
        
        # Get from database
        try:
            with get_db_session() as session:
                since_date = date.today() - timedelta(days=days)
                
                # Get quality metrics from database
                quality_records = session.query(CodeQualityMetric).filter(
                    CodeQualityMetric.created_at >= since_date
                ).all()
                
                if quality_records:
                    total_ai_lines = sum(r.ai_lines_original for r in quality_records)
                    total_modified = sum(r.lines_modified for r in quality_records)
                    
                    # Bug fixes
                    bug_fixes = [r for r in quality_records if r.modification_reason == "bug_fix"]
                    metrics.ai_code_bugs = len(bug_fixes)
                    
                    if total_ai_lines > 0:
                        metrics.bug_rate = round((metrics.ai_code_bugs / total_ai_lines) * 1000, 2)
                    
                    # Average days to modification
                    days_list = [r.days_until_modification for r in quality_records if r.days_until_modification]
                    if days_list:
                        metrics.avg_days_to_modification = round(sum(days_list) / len(days_list), 1)
                
                # Get daily metrics for PR info
                daily_metrics = session.query(DailyMetrics).filter(
                    DailyMetrics.date >= since_date
                ).all()
                
                if daily_metrics:
                    metrics.ai_prs_total = sum(dm.ai_assisted_prs for dm in daily_metrics)
                    
        except Exception as e:
            print(f"Error fetching quality data from database: {e}")
        
        return metrics
    
    def track_code_modification(
        self,
        repository: str,
        commit_sha: str,
        file_path: str,
        is_ai_generated: bool,
        ai_lines_original: int,
        lines_modified: int,
        modification_reason: str = "other"
    ):
        """
        Track a code modification event.
        
        Args:
            repository: Repository name
            commit_sha: Commit SHA
            file_path: Path to the file
            is_ai_generated: Whether original code was AI-generated
            ai_lines_original: Original AI-generated lines
            lines_modified: Lines that were modified
            modification_reason: Reason for modification
        """
        try:
            with get_db_session() as session:
                metric = CodeQualityMetric(
                    repository=repository,
                    commit_sha=commit_sha,
                    file_path=file_path,
                    is_ai_generated=is_ai_generated,
                    ai_lines_original=ai_lines_original,
                    lines_modified=lines_modified,
                    modification_date=date.today(),
                    modification_reason=modification_reason
                )
                session.add(metric)
                
        except Exception as e:
            print(f"Error tracking code modification: {e}")
    
    def get_quality_trend(self, days: int = 30) -> List[Dict]:
        """
        Get quality metrics trend over time.
        
        Args:
            days: Number of days to include
            
        Returns:
            List of daily quality metrics
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
                        "ai_code_lines": dm.ai_code_lines,
                        "ai_code_modified": dm.ai_code_modified,
                        "retention_rate": dm.ai_code_retention_rate
                    })
        except Exception as e:
            print(f"Error fetching quality trend: {e}")
        
        return trend
    
    def get_modification_breakdown(self, days: int = 30) -> Dict[str, int]:
        """
        Get breakdown of code modifications by reason.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dict with modification counts by reason
        """
        breakdown = {reason: 0 for reason in self.MODIFICATION_REASONS.keys()}
        
        try:
            with get_db_session() as session:
                since_date = date.today() - timedelta(days=days)
                
                quality_records = session.query(CodeQualityMetric).filter(
                    CodeQualityMetric.created_at >= since_date,
                    CodeQualityMetric.is_ai_generated == True
                ).all()
                
                for record in quality_records:
                    reason = record.modification_reason or "other"
                    if reason in breakdown:
                        breakdown[reason] += 1
                    else:
                        breakdown["other"] += 1
                        
        except Exception as e:
            print(f"Error fetching modification breakdown: {e}")
        
        return breakdown
    
    def get_repository_quality(self, days: int = 30) -> Dict[str, Dict]:
        """
        Get quality metrics broken down by repository.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dict with repository-level quality metrics
        """
        repos = {}
        
        try:
            with get_db_session() as session:
                since_date = date.today() - timedelta(days=days)
                
                quality_records = session.query(CodeQualityMetric).filter(
                    CodeQualityMetric.created_at >= since_date
                ).all()
                
                for record in quality_records:
                    repo = record.repository
                    if repo not in repos:
                        repos[repo] = {
                            "total_ai_lines": 0,
                            "modified_lines": 0,
                            "bug_fixes": 0,
                            "files_tracked": 0
                        }
                    
                    repos[repo]["total_ai_lines"] += record.ai_lines_original
                    repos[repo]["modified_lines"] += record.lines_modified
                    repos[repo]["files_tracked"] += 1
                    if record.modification_reason == "bug_fix":
                        repos[repo]["bug_fixes"] += 1
                
                # Calculate rates
                for repo in repos:
                    total = repos[repo]["total_ai_lines"]
                    if total > 0:
                        repos[repo]["modification_rate"] = round(
                            (repos[repo]["modified_lines"] / total) * 100, 2
                        )
                        repos[repo]["retention_rate"] = round(
                            100 - repos[repo]["modification_rate"], 2
                        )
                        repos[repo]["bug_rate"] = round(
                            (repos[repo]["bug_fixes"] / total) * 1000, 2
                        )
                    else:
                        repos[repo]["modification_rate"] = 0
                        repos[repo]["retention_rate"] = 100
                        repos[repo]["bug_rate"] = 0
                        
        except Exception as e:
            print(f"Error fetching repository quality: {e}")
        
        return repos
    
    def calculate_kois(self) -> Dict:
        """
        Calculate Key Outcome Indicators for quality.
        
        Returns:
            Dict with KOI status
        """
        metrics = self.get_quality_metrics(days=30)
        
        kois = {
            "code_retention_rate": {
                "name": "Code Retention Rate",
                "target": 85.0,
                "current": metrics.code_retention_rate,
                "achieved": metrics.code_retention_rate >= 85.0,
                "unit": "%",
                "description": "Percentage of AI code that remains unchanged"
            },
            "modification_rate": {
                "name": "Modification Rate",
                "target": 15.0,  # Lower is better
                "current": metrics.modification_rate,
                "achieved": metrics.modification_rate <= 15.0,
                "unit": "%",
                "description": "Percentage of AI code requiring changes (lower is better)"
            },
            "bug_rate": {
                "name": "Bug Rate",
                "target": 5.0,  # Lower is better
                "current": metrics.bug_rate,
                "achieved": metrics.bug_rate <= 5.0,
                "unit": "per 1K LOC",
                "description": "Bugs per 1000 lines of AI code (lower is better)"
            },
            "pr_success_rate": {
                "name": "PR Success Rate",
                "target": 90.0,
                "current": round(100 - metrics.pr_rejection_rate, 2),
                "achieved": (100 - metrics.pr_rejection_rate) >= 90.0,
                "unit": "%",
                "description": "Percentage of AI PRs merged successfully"
            }
        }
        
        return kois


def get_quality_calculator(git_analyzer: GitAnalyzer = None) -> QualityMetricsCalculator:
    """Get quality metrics calculator instance."""
    return QualityMetricsCalculator(git_analyzer)
