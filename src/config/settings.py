"""
POC 1: AI Adoption Metrics Dashboard
Configuration Settings Module

This module handles all configuration using pydantic-settings
for type-safe environment variable loading.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
from functools import lru_cache
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # GitHub Configuration
    github_token: str = Field(
        default="",
        description="GitHub Personal Access Token with copilot and read:org scopes"
    )
    github_org: str = Field(
        default="",
        description="GitHub Organization name"
    )
    github_enterprise_url: Optional[str] = Field(
        default=None,
        description="GitHub Enterprise URL (leave empty for github.com)"
    )
    
    # Database Configuration
    database_url: str = Field(
        default="sqlite:///./data/metrics.db",
        description="Database connection URL"
    )
    
    # Dashboard Configuration
    dashboard_host: str = Field(default="0.0.0.0")
    dashboard_port: int = Field(default=8501)
    dashboard_debug: bool = Field(default=True)
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)
    
    # Data Settings
    data_refresh_interval: int = Field(
        default=60,
        description="Data refresh interval in minutes"
    )
    historical_days: int = Field(
        default=90,
        description="Number of days of historical data to fetch"
    )
    
    # MCP Configuration
    mcp_server_enabled: bool = Field(default=True)
    mcp_github_server_path: Optional[str] = Field(default=None)
    
    # Logging
    log_level: str = Field(default="INFO")
    log_file: str = Field(default="logs/app.log")
    
    # Feature Flags
    enable_mcp_tracking: bool = Field(default=True)
    enable_git_analysis: bool = Field(default=True)
    enable_quality_metrics: bool = Field(default=True)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @property
    def github_api_url(self) -> str:
        """Get the GitHub API base URL."""
        if self.github_enterprise_url:
            return f"{self.github_enterprise_url}/api/v3"
        return "https://api.github.com"
    
    @property
    def data_dir(self) -> Path:
        """Get the data directory path."""
        path = Path("./data")
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @property
    def logs_dir(self) -> Path:
        """Get the logs directory path."""
        path = Path("./logs")
        path.mkdir(parents=True, exist_ok=True)
        return path


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Convenience function to get settings
settings = get_settings()
