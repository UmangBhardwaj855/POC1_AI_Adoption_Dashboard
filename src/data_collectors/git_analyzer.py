"""
POC 1: AI Adoption Metrics Dashboard
Git Repository Analyzer

Analyzes Git repositories for code quality metrics and AI code tracking.
"""

import os
from datetime import datetime, date, timedelta
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass
from pathlib import Path
import re

try:
    from git import Repo, Commit
    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False
    print("⚠️ GitPython not installed. Git analysis features will be limited.")

from ..config.settings import settings


@dataclass
class CommitInfo:
    """Information about a single commit."""
    sha: str
    author: str
    author_email: str
    date: datetime
    message: str
    files_changed: int
    insertions: int
    deletions: int
    is_ai_assisted: bool = False
    ai_indicators: List[str] = None
    
    def __post_init__(self):
        if self.ai_indicators is None:
            self.ai_indicators = []


@dataclass
class FileChange:
    """Information about a file change."""
    file_path: str
    commit_sha: str
    change_type: str  # added, modified, deleted
    insertions: int
    deletions: int
    is_ai_generated: bool = False


@dataclass
class CodeQualityReport:
    """Code quality analysis report."""
    repository: str
    analysis_date: date
    total_commits: int
    ai_assisted_commits: int
    total_lines_added: int
    ai_lines_added: int
    files_modified: int
    ai_files_modified: int
    modification_rate: float  # % of AI code that was later modified


class GitAnalyzer:
    """Analyzer for Git repositories to track AI-assisted development."""
    
    # Patterns that might indicate AI-assisted commits
    AI_COMMIT_PATTERNS = [
        r'copilot',
        r'ai.generated',
        r'ai.assisted',
        r'generated.by.ai',
        r'auto.generated',
        r'\[ai\]',
        r'github.copilot',
        r'cursor',
        r'tabnine',
        r'codewhisperer',
    ]
    
    def __init__(self, repo_path: str = None):
        """
        Initialize Git analyzer.
        
        Args:
            repo_path: Path to Git repository (optional)
        """
        if not GIT_AVAILABLE:
            raise ImportError("GitPython is required for Git analysis. Install with: pip install gitpython")
        
        self.repo_path = repo_path
        self.repo = None
        
        if repo_path and os.path.exists(repo_path):
            self._load_repo(repo_path)
    
    def _load_repo(self, repo_path: str):
        """Load a Git repository."""
        try:
            self.repo = Repo(repo_path)
            if self.repo.bare:
                raise ValueError(f"Repository at {repo_path} is bare")
            self.repo_path = repo_path
        except Exception as e:
            raise ValueError(f"Failed to load repository: {str(e)}")
    
    def set_repository(self, repo_path: str):
        """Set or change the repository to analyze."""
        self._load_repo(repo_path)
    
    def _is_ai_assisted_commit(self, commit: Commit) -> Tuple[bool, List[str]]:
        """
        Check if a commit appears to be AI-assisted.
        
        Args:
            commit: Git commit object
            
        Returns:
            Tuple of (is_ai_assisted, list of indicators found)
        """
        indicators = []
        message = commit.message.lower()
        
        for pattern in self.AI_COMMIT_PATTERNS:
            if re.search(pattern, message, re.IGNORECASE):
                indicators.append(pattern)
        
        # Check for co-authored-by patterns
        if 'co-authored-by' in message and 'copilot' in message.lower():
            indicators.append('co-authored-by-copilot')
        
        # Check commit author (some tools add specific authors)
        author_name = commit.author.name.lower() if commit.author else ""
        if 'copilot' in author_name or 'bot' in author_name:
            indicators.append('ai-author')
        
        return len(indicators) > 0, indicators
    
    def get_commits(
        self, 
        since: date = None, 
        until: date = None,
        branch: str = None,
        max_count: int = None
    ) -> List[CommitInfo]:
        """
        Get commits from the repository.
        
        Args:
            since: Start date
            until: End date
            branch: Branch name (defaults to active branch)
            max_count: Maximum number of commits to return
            
        Returns:
            List of CommitInfo objects
        """
        if not self.repo:
            raise ValueError("No repository loaded. Call set_repository() first.")
        
        commits = []
        
        # Build git log arguments
        kwargs = {}
        if since:
            kwargs['since'] = since.isoformat()
        if until:
            kwargs['until'] = until.isoformat()
        if max_count:
            kwargs['max_count'] = max_count
        
        # Get the branch
        if branch:
            ref = branch
        else:
            ref = self.repo.active_branch.name
        
        try:
            for commit in self.repo.iter_commits(ref, **kwargs):
                is_ai, indicators = self._is_ai_assisted_commit(commit)
                
                # Get stats
                stats = commit.stats
                
                commit_info = CommitInfo(
                    sha=commit.hexsha,
                    author=commit.author.name if commit.author else "Unknown",
                    author_email=commit.author.email if commit.author else "",
                    date=datetime.fromtimestamp(commit.committed_date),
                    message=commit.message.strip()[:200],  # Limit message length
                    files_changed=stats.total.get('files', 0),
                    insertions=stats.total.get('insertions', 0),
                    deletions=stats.total.get('deletions', 0),
                    is_ai_assisted=is_ai,
                    ai_indicators=indicators
                )
                commits.append(commit_info)
        except Exception as e:
            print(f"Error iterating commits: {str(e)}")
        
        return commits
    
    def get_commit_stats(self, since: date = None, until: date = None) -> Dict:
        """
        Get aggregated commit statistics.
        
        Args:
            since: Start date
            until: End date
            
        Returns:
            Dict with commit statistics
        """
        commits = self.get_commits(since=since, until=until)
        
        if not commits:
            return {
                "total_commits": 0,
                "ai_assisted_commits": 0,
                "ai_percentage": 0,
                "total_insertions": 0,
                "total_deletions": 0,
                "unique_authors": 0,
                "ai_authors": [],
                "commits_by_author": {}
            }
        
        ai_commits = [c for c in commits if c.is_ai_assisted]
        authors = set(c.author for c in commits)
        ai_authors = set(c.author for c in ai_commits)
        
        # Commits by author
        commits_by_author = {}
        for commit in commits:
            if commit.author not in commits_by_author:
                commits_by_author[commit.author] = {
                    "total": 0,
                    "ai_assisted": 0,
                    "insertions": 0,
                    "deletions": 0
                }
            commits_by_author[commit.author]["total"] += 1
            commits_by_author[commit.author]["insertions"] += commit.insertions
            commits_by_author[commit.author]["deletions"] += commit.deletions
            if commit.is_ai_assisted:
                commits_by_author[commit.author]["ai_assisted"] += 1
        
        return {
            "total_commits": len(commits),
            "ai_assisted_commits": len(ai_commits),
            "ai_percentage": round(len(ai_commits) / len(commits) * 100, 2) if commits else 0,
            "total_insertions": sum(c.insertions for c in commits),
            "total_deletions": sum(c.deletions for c in commits),
            "ai_insertions": sum(c.insertions for c in ai_commits),
            "ai_deletions": sum(c.deletions for c in ai_commits),
            "unique_authors": len(authors),
            "ai_authors": list(ai_authors),
            "commits_by_author": commits_by_author
        }
    
    def track_file_modifications(
        self, 
        file_path: str, 
        since_commit: str = None,
        days: int = 30
    ) -> Dict:
        """
        Track modifications to a specific file.
        
        Args:
            file_path: Path to the file within the repository
            since_commit: Starting commit SHA
            days: Number of days to look back
            
        Returns:
            Dict with modification history
        """
        if not self.repo:
            raise ValueError("No repository loaded.")
        
        since_date = date.today() - timedelta(days=days)
        
        modifications = []
        try:
            for commit in self.repo.iter_commits(paths=file_path, since=since_date.isoformat()):
                is_ai, indicators = self._is_ai_assisted_commit(commit)
                
                modifications.append({
                    "sha": commit.hexsha[:8],
                    "date": datetime.fromtimestamp(commit.committed_date).isoformat(),
                    "author": commit.author.name if commit.author else "Unknown",
                    "message": commit.message.strip()[:100],
                    "is_ai_assisted": is_ai
                })
        except Exception as e:
            print(f"Error tracking file modifications: {str(e)}")
        
        return {
            "file_path": file_path,
            "total_modifications": len(modifications),
            "ai_modifications": sum(1 for m in modifications if m["is_ai_assisted"]),
            "history": modifications
        }
    
    def analyze_code_quality(self, days: int = 30) -> CodeQualityReport:
        """
        Analyze code quality metrics over a period.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            CodeQualityReport with analysis results
        """
        since_date = date.today() - timedelta(days=days)
        commits = self.get_commits(since=since_date)
        
        ai_commits = [c for c in commits if c.is_ai_assisted]
        
        # Calculate total lines
        total_lines = sum(c.insertions for c in commits)
        ai_lines = sum(c.insertions for c in ai_commits)
        
        # Estimate modification rate (simplified)
        # In real implementation, this would track specific lines/files
        modification_rate = 0.0
        if ai_commits and len(commits) > len(ai_commits):
            # Rough estimate: if there are follow-up commits, some might be fixes
            potential_fixes = len(commits) - len(ai_commits)
            modification_rate = min(potential_fixes / len(ai_commits) * 10, 100)
        
        return CodeQualityReport(
            repository=self.repo_path or "unknown",
            analysis_date=date.today(),
            total_commits=len(commits),
            ai_assisted_commits=len(ai_commits),
            total_lines_added=total_lines,
            ai_lines_added=ai_lines,
            files_modified=sum(c.files_changed for c in commits),
            ai_files_modified=sum(c.files_changed for c in ai_commits),
            modification_rate=round(modification_rate, 2)
        )
    
    def get_repository_info(self) -> Dict:
        """Get basic repository information."""
        if not self.repo:
            return {"error": "No repository loaded"}
        
        try:
            return {
                "path": self.repo_path,
                "active_branch": self.repo.active_branch.name,
                "branches": [b.name for b in self.repo.branches],
                "remotes": [r.name for r in self.repo.remotes],
                "is_dirty": self.repo.is_dirty(),
                "head_commit": self.repo.head.commit.hexsha[:8]
            }
        except Exception as e:
            return {"error": str(e)}


# Factory function
def get_git_analyzer(repo_path: str = None) -> GitAnalyzer:
    """Get a Git analyzer instance."""
    return GitAnalyzer(repo_path)
