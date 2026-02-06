"""
POC 1: AI Adoption Metrics Dashboard
MCP Event Tracker

Tracks AI-assisted GitHub operations through Model Context Protocol.
"""

import json
from datetime import datetime, date
from typing import Optional, Dict, List, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio

from ..config.settings import settings
from ..database.models import MCPEvent
from ..database.connection import get_db_session


class MCPEventType(Enum):
    """Types of MCP events to track."""
    COMMIT = "commit"
    PULL_REQUEST = "pull_request"
    BRANCH = "branch"
    FILE_CREATE = "file_create"
    FILE_EDIT = "file_edit"
    CODE_REVIEW = "code_review"
    ISSUE = "issue"
    SEARCH = "search"


@dataclass
class MCPEventData:
    """Data structure for MCP events."""
    event_type: str
    timestamp: datetime
    github_username: str
    repository: str
    details: Dict[str, Any]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "github_username": self.github_username,
            "repository": self.repository,
            "details": self.details
        }


class MCPEventTracker:
    """
    Tracker for MCP (Model Context Protocol) events.
    
    This class provides functionality to:
    1. Log AI-assisted GitHub operations
    2. Query historical MCP events
    3. Aggregate metrics from MCP usage
    
    Note: In a production environment, this would integrate with 
    an actual MCP server to receive real-time events.
    """
    
    def __init__(self):
        """Initialize MCP Event Tracker."""
        self.enabled = settings.enable_mcp_tracking
        self._event_handlers: List[Callable] = []
    
    def register_handler(self, handler: Callable):
        """Register an event handler callback."""
        self._event_handlers.append(handler)
    
    def _notify_handlers(self, event: MCPEventData):
        """Notify all registered handlers of a new event."""
        for handler in self._event_handlers:
            try:
                handler(event)
            except Exception as e:
                print(f"Error in event handler: {e}")
    
    def log_event(
        self,
        event_type: MCPEventType,
        github_username: str,
        repository: str,
        details: Dict[str, Any] = None
    ) -> MCPEventData:
        """
        Log an MCP event.
        
        Args:
            event_type: Type of event
            github_username: GitHub username who triggered the event
            repository: Repository where event occurred
            details: Additional event details
            
        Returns:
            MCPEventData object
        """
        if not self.enabled:
            return None
        
        event = MCPEventData(
            event_type=event_type.value,
            timestamp=datetime.utcnow(),
            github_username=github_username,
            repository=repository,
            details=details or {}
        )
        
        # Save to database
        try:
            with get_db_session() as session:
                db_event = MCPEvent(
                    event_type=event.event_type,
                    github_username=event.github_username,
                    repository=event.repository,
                    event_data=event.details,
                    event_timestamp=event.timestamp
                )
                session.add(db_event)
        except Exception as e:
            print(f"Error saving MCP event: {e}")
        
        # Notify handlers
        self._notify_handlers(event)
        
        return event
    
    def log_commit(
        self,
        github_username: str,
        repository: str,
        commit_sha: str,
        message: str,
        files_changed: int = 0,
        lines_added: int = 0,
        lines_removed: int = 0
    ) -> MCPEventData:
        """Log an AI-assisted commit."""
        return self.log_event(
            event_type=MCPEventType.COMMIT,
            github_username=github_username,
            repository=repository,
            details={
                "commit_sha": commit_sha,
                "message": message,
                "files_changed": files_changed,
                "lines_added": lines_added,
                "lines_removed": lines_removed
            }
        )
    
    def log_pull_request(
        self,
        github_username: str,
        repository: str,
        pr_number: int,
        title: str,
        action: str = "created"  # created, updated, merged
    ) -> MCPEventData:
        """Log an AI-assisted pull request."""
        return self.log_event(
            event_type=MCPEventType.PULL_REQUEST,
            github_username=github_username,
            repository=repository,
            details={
                "pr_number": pr_number,
                "title": title,
                "action": action
            }
        )
    
    def log_branch(
        self,
        github_username: str,
        repository: str,
        branch_name: str,
        action: str = "created"
    ) -> MCPEventData:
        """Log an AI-assisted branch operation."""
        return self.log_event(
            event_type=MCPEventType.BRANCH,
            github_username=github_username,
            repository=repository,
            details={
                "branch_name": branch_name,
                "action": action
            }
        )
    
    def log_file_operation(
        self,
        github_username: str,
        repository: str,
        file_path: str,
        operation: str,  # create, edit, delete
        lines_changed: int = 0
    ) -> MCPEventData:
        """Log an AI-assisted file operation."""
        event_type = MCPEventType.FILE_CREATE if operation == "create" else MCPEventType.FILE_EDIT
        return self.log_event(
            event_type=event_type,
            github_username=github_username,
            repository=repository,
            details={
                "file_path": file_path,
                "operation": operation,
                "lines_changed": lines_changed
            }
        )
    
    def get_events(
        self,
        event_type: MCPEventType = None,
        github_username: str = None,
        repository: str = None,
        since: datetime = None,
        until: datetime = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Query MCP events from database.
        
        Args:
            event_type: Filter by event type
            github_username: Filter by username
            repository: Filter by repository
            since: Start datetime
            until: End datetime
            limit: Maximum results
            
        Returns:
            List of event dictionaries
        """
        events = []
        
        try:
            with get_db_session() as session:
                query = session.query(MCPEvent)
                
                if event_type:
                    query = query.filter(MCPEvent.event_type == event_type.value)
                if github_username:
                    query = query.filter(MCPEvent.github_username == github_username)
                if repository:
                    query = query.filter(MCPEvent.repository == repository)
                if since:
                    query = query.filter(MCPEvent.event_timestamp >= since)
                if until:
                    query = query.filter(MCPEvent.event_timestamp <= until)
                
                query = query.order_by(MCPEvent.event_timestamp.desc()).limit(limit)
                
                for event in query.all():
                    events.append({
                        "id": event.id,
                        "event_type": event.event_type,
                        "github_username": event.github_username,
                        "repository": event.repository,
                        "event_data": event.event_data,
                        "timestamp": event.event_timestamp.isoformat()
                    })
        except Exception as e:
            print(f"Error querying MCP events: {e}")
        
        return events
    
    def get_metrics(self, since: datetime = None, until: datetime = None) -> Dict:
        """
        Get aggregated MCP metrics.
        
        Args:
            since: Start datetime
            until: End datetime
            
        Returns:
            Dict with aggregated metrics
        """
        events = self.get_events(since=since, until=until, limit=10000)
        
        if not events:
            return {
                "total_events": 0,
                "ai_commits": 0,
                "ai_pull_requests": 0,
                "ai_branches": 0,
                "ai_file_operations": 0,
                "unique_users": 0,
                "unique_repositories": 0,
                "events_by_type": {},
                "events_by_user": {},
                "events_by_repo": {}
            }
        
        # Aggregate metrics
        events_by_type = {}
        events_by_user = {}
        events_by_repo = {}
        
        for event in events:
            # By type
            etype = event["event_type"]
            events_by_type[etype] = events_by_type.get(etype, 0) + 1
            
            # By user
            user = event["github_username"]
            if user:
                events_by_user[user] = events_by_user.get(user, 0) + 1
            
            # By repo
            repo = event["repository"]
            if repo:
                events_by_repo[repo] = events_by_repo.get(repo, 0) + 1
        
        return {
            "total_events": len(events),
            "ai_commits": events_by_type.get("commit", 0),
            "ai_pull_requests": events_by_type.get("pull_request", 0),
            "ai_branches": events_by_type.get("branch", 0),
            "ai_file_operations": events_by_type.get("file_create", 0) + events_by_type.get("file_edit", 0),
            "unique_users": len(events_by_user),
            "unique_repositories": len(events_by_repo),
            "events_by_type": events_by_type,
            "events_by_user": events_by_user,
            "events_by_repo": events_by_repo
        }
    
    def get_user_activity(self, github_username: str, days: int = 30) -> Dict:
        """
        Get MCP activity for a specific user.
        
        Args:
            github_username: GitHub username
            days: Number of days to look back
            
        Returns:
            Dict with user activity metrics
        """
        from datetime import timedelta
        since = datetime.utcnow() - timedelta(days=days)
        
        events = self.get_events(github_username=github_username, since=since, limit=1000)
        
        activity = {
            "username": github_username,
            "period_days": days,
            "total_events": len(events),
            "commits": 0,
            "pull_requests": 0,
            "file_operations": 0,
            "repositories": set(),
            "daily_activity": {}
        }
        
        for event in events:
            etype = event["event_type"]
            
            if etype == "commit":
                activity["commits"] += 1
            elif etype == "pull_request":
                activity["pull_requests"] += 1
            elif etype in ["file_create", "file_edit"]:
                activity["file_operations"] += 1
            
            if event["repository"]:
                activity["repositories"].add(event["repository"])
            
            # Daily breakdown
            event_date = event["timestamp"][:10]  # YYYY-MM-DD
            if event_date not in activity["daily_activity"]:
                activity["daily_activity"][event_date] = 0
            activity["daily_activity"][event_date] += 1
        
        activity["repositories"] = list(activity["repositories"])
        
        return activity


# Singleton instance
_tracker_instance = None


def get_mcp_tracker() -> MCPEventTracker:
    """Get the MCP event tracker singleton."""
    global _tracker_instance
    if _tracker_instance is None:
        _tracker_instance = MCPEventTracker()
    return _tracker_instance
