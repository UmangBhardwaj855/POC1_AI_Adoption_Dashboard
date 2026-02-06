"""
GitHub Copilot API Integration
Fetches real usage data from GitHub Copilot Business/Enterprise API
"""

import httpx
from datetime import datetime, date, timedelta
from typing import Optional, Dict, List
import os

class GitHubCopilotClient:
    """
    GitHub Copilot API Client
    
    Required:
    - GitHub Personal Access Token with scopes: read:org, copilot
    - Organization must have GitHub Copilot Business/Enterprise
    """
    
    BASE_URL = "https://api.github.com"
    
    def __init__(self, token: str, org: str):
        self.token = token
        self.org = org
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
    
    async def get_copilot_billing(self) -> Dict:
        """
        Get Copilot billing/seats information
        Endpoint: GET /orgs/{org}/copilot/billing
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/orgs/{self.org}/copilot/billing",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
    
    async def get_copilot_seats(self) -> Dict:
        """
        Get all Copilot seat assignments
        Endpoint: GET /orgs/{org}/copilot/billing/seats
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/orgs/{self.org}/copilot/billing/seats",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
    
    async def get_copilot_usage(self, since: Optional[date] = None, until: Optional[date] = None) -> List[Dict]:
        """
        Get Copilot usage metrics (Enterprise only)
        Endpoint: GET /orgs/{org}/copilot/usage
        
        Returns daily metrics:
        - total_suggestions_count
        - total_acceptances_count
        - total_lines_suggested
        - total_lines_accepted
        - total_active_users
        - breakdown by language/editor
        """
        params = {}
        if since:
            params["since"] = since.isoformat()
        if until:
            params["until"] = until.isoformat()
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/orgs/{self.org}/copilot/usage",
                headers=self.headers,
                params=params
            )
            response.raise_for_status()
            return response.json()
    
    async def get_org_members(self) -> List[Dict]:
        """
        Get all organization members
        Endpoint: GET /orgs/{org}/members
        """
        members = []
        page = 1
        
        async with httpx.AsyncClient() as client:
            while True:
                response = await client.get(
                    f"{self.BASE_URL}/orgs/{self.org}/members",
                    headers=self.headers,
                    params={"per_page": 100, "page": page}
                )
                response.raise_for_status()
                data = response.json()
                
                if not data:
                    break
                    
                members.extend(data)
                page += 1
        
        return members
    
    async def get_user_details(self, username: str) -> Dict:
        """
        Get detailed user information
        Endpoint: GET /users/{username}
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/users/{username}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()


# Sync version for simpler usage
class GitHubCopilotClientSync:
    """Synchronous version of the GitHub Copilot client"""
    
    BASE_URL = "https://api.github.com"
    
    def __init__(self, token: str, org: str):
        self.token = token
        self.org = org
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
    
    def get_copilot_billing(self) -> Dict:
        """Get Copilot billing information"""
        with httpx.Client() as client:
            response = client.get(
                f"{self.BASE_URL}/orgs/{self.org}/copilot/billing",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
    
    def get_copilot_seats(self) -> Dict:
        """Get all Copilot seat assignments"""
        with httpx.Client() as client:
            response = client.get(
                f"{self.BASE_URL}/orgs/{self.org}/copilot/billing/seats",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
    
    def get_copilot_usage(self, since: Optional[date] = None, until: Optional[date] = None) -> List[Dict]:
        """Get Copilot usage metrics"""
        params = {}
        if since:
            params["since"] = since.isoformat()
        if until:
            params["until"] = until.isoformat()
        
        with httpx.Client() as client:
            response = client.get(
                f"{self.BASE_URL}/orgs/{self.org}/copilot/usage",
                headers=self.headers,
                params=params
            )
            response.raise_for_status()
            return response.json()
    
    def get_org_members(self) -> List[Dict]:
        """Get all organization members"""
        members = []
        page = 1
        
        with httpx.Client() as client:
            while True:
                response = client.get(
                    f"{self.BASE_URL}/orgs/{self.org}/members",
                    headers=self.headers,
                    params={"per_page": 100, "page": page}
                )
                response.raise_for_status()
                data = response.json()
                
                if not data:
                    break
                    
                members.extend(data)
                page += 1
        
        return members
    
    def get_user_details(self, username: str) -> Dict:
        """Get detailed user information"""
        with httpx.Client() as client:
            response = client.get(
                f"{self.BASE_URL}/users/{username}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
