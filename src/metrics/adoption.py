"""
POC 1: AI Adoption Metrics Dashboard
Adoption Metrics Calculator

Calculates adoption-related metrics from collected data.
"""

from datetime import datetime, date, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass

from ..data_collectors.copilot_api import CopilotAPIClient, CopilotSeatInfo
from ..database.models import User, DailyMetrics, Organization
from ..database.connection import get_db_session


@dataclass
class AdoptionMetrics:
    """Adoption metrics data class."""
    date: date
    total_engineers: int
    enabled_users: int
    active_users: int
    weekly_active_users: int
    monthly_active_users: int
    activation_rate: float  # active/enabled %
    adoption_rate: float    # enabled/total %
    features_per_user: float
    prompts_per_user_week: float
    maturity_distribution: Dict[str, int]


class AdoptionMetricsCalculator:
    """Calculator for adoption metrics."""
    
    # Maturity Level Definitions (L0-L5)
    MATURITY_LEVELS = {
        0: "L0: Not Enabled",
        1: "L1: Enabled",
        2: "L2: Active User",
        3: "L3: Working User",
        4: "L4: Consistent User",
        5: "L5: Value User"
    }
    
    def __init__(self, copilot_client: CopilotAPIClient = None):
        """
        Initialize adoption metrics calculator.
        
        Args:
            copilot_client: Copilot API client (optional)
        """
        self.copilot_client = copilot_client
    
    def calculate_maturity_level(
        self,
        is_enabled: bool,
        weekly_active: bool,
        monthly_active: bool,
        prompts_per_week: float,
        features_used: int,
        has_work_linkage: bool = False,
        has_business_outcomes: bool = False
    ) -> int:
        """
        Calculate maturity level for a user.
        
        L0: Not Enabled - Tool not available
        L1: Enabled - Tool available, minimal usage (<1 interaction/week)
        L2: Active User - Regular tool usage (weekly active)
        L3: Working User - AI embedded in real work
        L4: Consistent User - Habitual, daily usage
        L5: Value User - Measurable business outcomes
        
        Args:
            is_enabled: Whether Copilot is enabled
            weekly_active: Whether user is weekly active
            monthly_active: Whether user is monthly active
            prompts_per_week: Average prompts per week
            features_used: Number of features used
            has_work_linkage: Whether usage is linked to work items
            has_business_outcomes: Whether measurable outcomes exist
            
        Returns:
            Maturity level (0-5)
        """
        if not is_enabled:
            return 0  # L0: Not Enabled
        
        if not monthly_active or prompts_per_week < 1:
            return 1  # L1: Enabled but minimal usage
        
        if not weekly_active:
            return 1  # L1: Only monthly active
        
        # L2: Weekly active user
        if prompts_per_week < 5 or features_used < 3:
            return 2
        
        # L3: Working user (embedded in real work)
        if not has_work_linkage:
            if prompts_per_week >= 5 and features_used >= 4:
                return 3
            return 2
        
        # L4: Consistent user (habitual usage)
        if prompts_per_week >= 10 and features_used >= 6:
            if has_business_outcomes:
                return 5  # L5: Value user
            return 4
        
        return 3  # L3: Working user
    
    def get_adoption_metrics(self) -> AdoptionMetrics:
        """
        Get current adoption metrics.
        
        Returns:
            AdoptionMetrics object
        """
        metrics = AdoptionMetrics(
            date=date.today(),
            total_engineers=0,
            enabled_users=0,
            active_users=0,
            weekly_active_users=0,
            monthly_active_users=0,
            activation_rate=0.0,
            adoption_rate=0.0,
            features_per_user=0.0,
            prompts_per_user_week=0.0,
            maturity_distribution={level: 0 for level in self.MATURITY_LEVELS.values()}
        )
        
        # Try to get data from Copilot API
        if self.copilot_client:
            try:
                billing = self.copilot_client.get_copilot_billing()
                seats = self.copilot_client.get_all_copilot_seats()
                usage = self.copilot_client.get_usage_summary(days=7)
                
                seat_breakdown = billing.get("seat_breakdown", {})
                metrics.total_engineers = seat_breakdown.get("total", 0)
                metrics.enabled_users = seat_breakdown.get("total", 0)
                metrics.active_users = seat_breakdown.get("active_this_cycle", 0)
                
                # Calculate WAU/MAU from seats
                now = datetime.utcnow()
                week_ago = now - timedelta(days=7)
                month_ago = now - timedelta(days=30)
                
                wau = 0
                mau = 0
                for seat in seats:
                    if seat.last_activity_at:
                        if seat.last_activity_at >= week_ago:
                            wau += 1
                        if seat.last_activity_at >= month_ago:
                            mau += 1
                
                metrics.weekly_active_users = wau
                metrics.monthly_active_users = mau
                
                # Calculate rates
                if metrics.enabled_users > 0:
                    metrics.activation_rate = round(
                        (metrics.active_users / metrics.enabled_users) * 100, 2
                    )
                
                if metrics.total_engineers > 0:
                    metrics.adoption_rate = round(
                        (metrics.enabled_users / metrics.total_engineers) * 100, 2
                    )
                
                # Usage metrics
                if usage.get("avg_daily_active_users", 0) > 0:
                    total_suggestions = usage.get("total_suggestions", 0)
                    avg_users = usage.get("avg_daily_active_users", 1)
                    metrics.prompts_per_user_week = round(total_suggestions / avg_users / 7, 2)
                
            except Exception as e:
                print(f"Error fetching Copilot data: {e}")
        
        # Also try to get from database
        try:
            with get_db_session() as session:
                users = session.query(User).all()
                
                if users:
                    maturity_dist = {level: 0 for level in self.MATURITY_LEVELS.values()}
                    
                    for user in users:
                        level_name = self.MATURITY_LEVELS.get(user.maturity_level, "L0: Not Enabled")
                        maturity_dist[level_name] = maturity_dist.get(level_name, 0) + 1
                    
                    metrics.maturity_distribution = maturity_dist
        except Exception as e:
            print(f"Error fetching database data: {e}")
        
        return metrics
    
    def get_team_adoption(self) -> Dict[str, Dict]:
        """
        Get adoption metrics broken down by team.
        
        Returns:
            Dict with team-level metrics
        """
        teams = {}
        
        try:
            with get_db_session() as session:
                users = session.query(User).all()
                
                for user in users:
                    team = user.team or "Unassigned"
                    
                    if team not in teams:
                        teams[team] = {
                            "total": 0,
                            "enabled": 0,
                            "active": 0,
                            "maturity_sum": 0
                        }
                    
                    teams[team]["total"] += 1
                    if user.copilot_enabled:
                        teams[team]["enabled"] += 1
                    if user.is_weekly_active:
                        teams[team]["active"] += 1
                    teams[team]["maturity_sum"] += user.maturity_level
                
                # Calculate averages
                for team in teams:
                    total = teams[team]["total"]
                    if total > 0:
                        teams[team]["activation_rate"] = round(
                            (teams[team]["active"] / teams[team]["enabled"] * 100) 
                            if teams[team]["enabled"] > 0 else 0, 2
                        )
                        teams[team]["avg_maturity"] = round(
                            teams[team]["maturity_sum"] / total, 2
                        )
                    del teams[team]["maturity_sum"]
        except Exception as e:
            print(f"Error calculating team adoption: {e}")
        
        return teams
    
    def get_adoption_trend(self, days: int = 30) -> List[Dict]:
        """
        Get adoption trend over time.
        
        Args:
            days: Number of days to include
            
        Returns:
            List of daily adoption metrics
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
                        "total_users": dm.total_users,
                        "enabled_users": dm.enabled_users,
                        "active_users": dm.active_users,
                        "weekly_active_users": dm.weekly_active_users,
                        "activation_rate": dm.activation_rate
                    })
        except Exception as e:
            print(f"Error fetching adoption trend: {e}")
        
        return trend
    
    def calculate_kois(self) -> Dict:
        """
        Calculate Key Outcome Indicators for adoption.
        
        Returns:
            Dict with KOI status
        """
        metrics = self.get_adoption_metrics()
        
        kois = {
            "activation_rate": {
                "name": "Activation Rate",
                "target": 60.0,
                "current": metrics.activation_rate,
                "achieved": metrics.activation_rate >= 60.0,
                "unit": "%"
            },
            "weekly_active_percentage": {
                "name": "Weekly Active Users",
                "target": 70.0,
                "current": round(
                    (metrics.weekly_active_users / metrics.enabled_users * 100) 
                    if metrics.enabled_users > 0 else 0, 2
                ),
                "achieved": False,
                "unit": "%"
            },
            "l3_plus_percentage": {
                "name": "L3+ Maturity",
                "target": 40.0,
                "current": 0,
                "achieved": False,
                "unit": "%"
            },
            "prompts_per_week": {
                "name": "Prompts per User/Week",
                "target": 8.5,
                "current": metrics.prompts_per_user_week,
                "achieved": metrics.prompts_per_user_week >= 8.5,
                "unit": "prompts"
            }
        }
        
        # Calculate L3+ percentage
        total_users = sum(metrics.maturity_distribution.values())
        l3_plus = sum(
            count for level, count in metrics.maturity_distribution.items()
            if "L3" in level or "L4" in level or "L5" in level
        )
        if total_users > 0:
            kois["l3_plus_percentage"]["current"] = round(l3_plus / total_users * 100, 2)
            kois["l3_plus_percentage"]["achieved"] = kois["l3_plus_percentage"]["current"] >= 40.0
        
        # Update weekly active achieved status
        kois["weekly_active_percentage"]["achieved"] = kois["weekly_active_percentage"]["current"] >= 70.0
        
        return kois


def get_adoption_calculator(copilot_client: CopilotAPIClient = None) -> AdoptionMetricsCalculator:
    """Get adoption metrics calculator instance."""
    return AdoptionMetricsCalculator(copilot_client)
