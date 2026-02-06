"""
POC 1: AI Adoption Metrics Dashboard
GitHub Copilot Metrics API Client

Fetches usage data from GitHub Copilot Metrics API.
Reference: https://docs.github.com/en/rest/copilot
"""

import requests
from datetime import datetime, date, timedelta
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
import json

from ..config.settings import settings


@dataclass
class CopilotUsageData:
    """Data class for Copilot usage metrics."""
    date: date
    total_active_users: int
    total_suggestions_shown: int
    total_suggestions_accepted: int
    total_lines_suggested: int
    total_lines_accepted: int
    total_chat_interactions: int
    breakdown_by_language: Dict[str, Any]
    breakdown_by_editor: Dict[str, Any]
    
    @property
    def acceptance_rate(self) -> float:
        """Calculate suggestion acceptance rate."""
        if self.total_suggestions_shown == 0:
            return 0.0
        return (self.total_suggestions_accepted / self.total_suggestions_shown) * 100
    
    @property
    def lines_acceptance_rate(self) -> float:
        """Calculate lines acceptance rate."""
        if self.total_lines_suggested == 0:
            return 0.0
        return (self.total_lines_accepted / self.total_lines_suggested) * 100


@dataclass
class CopilotSeatInfo:
    """Data class for Copilot seat information."""
    login: str
    created_at: datetime
    last_activity_at: Optional[datetime]
    last_activity_editor: Optional[str]
    

class CopilotAPIClient:
    """Client for GitHub Copilot Metrics API."""
    
    def __init__(self, token: str = None, org: str = None):
        """
        Initialize the Copilot API client.
        
        Args:
            token: GitHub Personal Access Token (defaults to settings)
            org: GitHub Organization name (defaults to settings)
        """
        self.token = token or settings.github_token
        self.org = org or settings.github_org
        self.base_url = settings.github_api_url
        
        if not self.token:
            raise ValueError("GitHub token is required. Set GITHUB_TOKEN in .env")
        if not self.org:
            raise ValueError("GitHub organization is required. Set GITHUB_ORG in .env")
        
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
    
    def _make_request(self, endpoint: str, method: str = "GET", params: Dict = None) -> Dict:
        """Make API request to GitHub."""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                raise Exception("Authentication failed. Check your GitHub token.")
            elif response.status_code == 403:
                raise Exception("Access forbidden. Ensure token has 'copilot' and 'read:org' scopes.")
            elif response.status_code == 404:
                raise Exception(f"Endpoint not found or organization '{self.org}' doesn't exist.")
            else:
                raise Exception(f"API Error: {response.status_code} - {response.text}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")
    
    def get_copilot_billing(self) -> Dict:
        """
        Get Copilot billing/seat information for the organization.
        
        Returns:
            Dict with seat_breakdown, seat_management_setting, etc.
        """
        endpoint = f"/orgs/{self.org}/copilot/billing"
        return self._make_request(endpoint)
    
    def get_copilot_seats(self, page: int = 1, per_page: int = 100) -> Dict:
        """
        Get list of users with Copilot seats.
        
        Args:
            page: Page number for pagination
            per_page: Results per page (max 100)
            
        Returns:
            Dict with total_seats and seats list
        """
        endpoint = f"/orgs/{self.org}/copilot/billing/seats"
        params = {"page": page, "per_page": per_page}
        return self._make_request(endpoint, params=params)
    
    def get_all_copilot_seats(self) -> List[CopilotSeatInfo]:
        """
        Get all Copilot seats with pagination.
        
        Returns:
            List of CopilotSeatInfo objects
        """
        all_seats = []
        page = 1
        
        while True:
            response = self.get_copilot_seats(page=page)
            seats = response.get("seats", [])
            
            if not seats:
                break
            
            for seat in seats:
                assignee = seat.get("assignee", {})
                seat_info = CopilotSeatInfo(
                    login=assignee.get("login", ""),
                    created_at=datetime.fromisoformat(seat["created_at"].replace("Z", "+00:00")),
                    last_activity_at=datetime.fromisoformat(seat["last_activity_at"].replace("Z", "+00:00")) if seat.get("last_activity_at") else None,
                    last_activity_editor=seat.get("last_activity_editor")
                )
                all_seats.append(seat_info)
            
            if len(seats) < 100:
                break
            page += 1
        
        return all_seats
    
    def get_copilot_usage(self, since: date = None, until: date = None) -> List[Dict]:
        """
        Get Copilot usage metrics for the organization.
        
        Args:
            since: Start date (defaults to 28 days ago)
            until: End date (defaults to today)
            
        Returns:
            List of daily usage data
        """
        endpoint = f"/orgs/{self.org}/copilot/usage"
        
        params = {}
        if since:
            params["since"] = since.isoformat()
        if until:
            params["until"] = until.isoformat()
        
        return self._make_request(endpoint, params=params)
    
    def get_usage_summary(self, days: int = 28) -> Dict:
        """
        Get summarized usage metrics for the specified period.
        
        Args:
            days: Number of days to summarize
            
        Returns:
            Dict with summarized metrics
        """
        until_date = date.today()
        since_date = until_date - timedelta(days=days)
        
        usage_data = self.get_copilot_usage(since=since_date, until=until_date)
        
        if not usage_data:
            return {
                "period_days": days,
                "total_active_users": 0,
                "avg_daily_active_users": 0,
                "total_suggestions": 0,
                "total_acceptances": 0,
                "acceptance_rate": 0,
                "language_breakdown": {},
                "editor_breakdown": {}
            }
        
        # Aggregate metrics
        total_suggestions = sum(d.get("total_suggestions_count", 0) for d in usage_data)
        total_acceptances = sum(d.get("total_acceptances_count", 0) for d in usage_data)
        total_lines_suggested = sum(d.get("total_lines_suggested", 0) for d in usage_data)
        total_lines_accepted = sum(d.get("total_lines_accepted", 0) for d in usage_data)
        
        # Get unique active users (this is approximate)
        daily_active_users = [d.get("total_active_users", 0) for d in usage_data]
        max_active_users = max(daily_active_users) if daily_active_users else 0
        avg_daily_active = sum(daily_active_users) / len(daily_active_users) if daily_active_users else 0
        
        # Aggregate language breakdown
        language_breakdown = {}
        for day_data in usage_data:
            for breakdown in day_data.get("breakdown", []):
                lang = breakdown.get("language", "unknown")
                if lang not in language_breakdown:
                    language_breakdown[lang] = {
                        "suggestions_shown": 0,
                        "suggestions_accepted": 0,
                        "lines_suggested": 0,
                        "lines_accepted": 0
                    }
                language_breakdown[lang]["suggestions_shown"] += breakdown.get("suggestions_count", 0)
                language_breakdown[lang]["suggestions_accepted"] += breakdown.get("acceptances_count", 0)
                language_breakdown[lang]["lines_suggested"] += breakdown.get("lines_suggested", 0)
                language_breakdown[lang]["lines_accepted"] += breakdown.get("lines_accepted", 0)
        
        # Aggregate editor breakdown
        editor_breakdown = {}
        for day_data in usage_data:
            for breakdown in day_data.get("breakdown", []):
                editor = breakdown.get("editor", "unknown")
                if editor not in editor_breakdown:
                    editor_breakdown[editor] = {"active_users": 0}
                editor_breakdown[editor]["active_users"] += breakdown.get("active_users", 0)
        
        return {
            "period_days": days,
            "data_points": len(usage_data),
            "total_active_users": max_active_users,
            "avg_daily_active_users": round(avg_daily_active, 1),
            "total_suggestions": total_suggestions,
            "total_acceptances": total_acceptances,
            "acceptance_rate": round((total_acceptances / total_suggestions * 100) if total_suggestions > 0 else 0, 2),
            "total_lines_suggested": total_lines_suggested,
            "total_lines_accepted": total_lines_accepted,
            "lines_acceptance_rate": round((total_lines_accepted / total_lines_suggested * 100) if total_lines_suggested > 0 else 0, 2),
            "language_breakdown": language_breakdown,
            "editor_breakdown": editor_breakdown
        }
    
    def test_connection(self) -> Dict:
        """
        Test API connection and return organization info.
        
        Returns:
            Dict with connection status and org info
        """
        try:
            # Test basic org access
            org_endpoint = f"/orgs/{self.org}"
            org_info = self._make_request(org_endpoint)
            
            # Test Copilot access
            billing_info = self.get_copilot_billing()
            
            return {
                "status": "success",
                "organization": {
                    "name": org_info.get("name", self.org),
                    "login": org_info.get("login"),
                    "description": org_info.get("description"),
                    "public_repos": org_info.get("public_repos"),
                    "total_private_repos": org_info.get("total_private_repos")
                },
                "copilot": {
                    "seat_management_setting": billing_info.get("seat_management_setting"),
                    "total_seats": billing_info.get("seat_breakdown", {}).get("total", 0),
                    "active_seats": billing_info.get("seat_breakdown", {}).get("active_this_cycle", 0),
                    "inactive_seats": billing_info.get("seat_breakdown", {}).get("inactive_this_cycle", 0)
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }


# Convenience function
def get_copilot_client() -> CopilotAPIClient:
    """Get a configured Copilot API client."""
    return CopilotAPIClient()
