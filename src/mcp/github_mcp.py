"""
POC 1: AI Adoption Metrics Dashboard
GitHub MCP Server Configuration

Configuration for connecting to GitHub MCP Server.
Reference: https://github.com/github/github-mcp-server
"""

import json
import os
from typing import Dict, Optional
from pathlib import Path

from ..config.settings import settings


# GitHub MCP Server configuration template
GITHUB_MCP_CONFIG = {
    "mcpServers": {
        "github": {
            "command": "npx",
            "args": [
                "-y",
                "@modelcontextprotocol/server-github"
            ],
            "env": {
                "GITHUB_PERSONAL_ACCESS_TOKEN": ""  # Will be set from settings
            }
        }
    }
}


def get_mcp_config() -> Dict:
    """
    Get MCP server configuration for GitHub.
    
    Returns:
        Dict with MCP configuration
    """
    config = GITHUB_MCP_CONFIG.copy()
    config["mcpServers"]["github"]["env"]["GITHUB_PERSONAL_ACCESS_TOKEN"] = settings.github_token
    return config


def generate_mcp_config_file(output_path: str = None) -> str:
    """
    Generate MCP configuration file for VS Code/Cursor.
    
    Args:
        output_path: Path to save config file (defaults to .vscode/mcp.json)
        
    Returns:
        Path to generated config file
    """
    if output_path is None:
        output_path = ".vscode/mcp.json"
    
    config = get_mcp_config()
    
    # Create directory if needed
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ MCP config generated at: {output_path}")
    return output_path


def get_mcp_tools_info() -> Dict:
    """
    Get information about available GitHub MCP tools.
    
    Returns:
        Dict with tool descriptions
    """
    return {
        "available_tools": [
            {
                "name": "create_or_update_file",
                "description": "Create or update a single file in a GitHub repository",
                "use_for": "Tracking AI file operations"
            },
            {
                "name": "push_files",
                "description": "Push multiple files to a GitHub repository in a single commit",
                "use_for": "Tracking AI bulk commits"
            },
            {
                "name": "create_issue",
                "description": "Create a new issue in a GitHub repository",
                "use_for": "Tracking AI-created issues"
            },
            {
                "name": "create_pull_request",
                "description": "Create a new pull request in a GitHub repository",
                "use_for": "Tracking AI-created PRs"
            },
            {
                "name": "create_branch",
                "description": "Create a new branch in a GitHub repository",
                "use_for": "Tracking AI branch operations"
            },
            {
                "name": "search_code",
                "description": "Search for code across GitHub repositories",
                "use_for": "Tracking AI code searches"
            },
            {
                "name": "search_issues",
                "description": "Search for issues and pull requests",
                "use_for": "Tracking AI issue searches"
            },
            {
                "name": "get_file_contents",
                "description": "Get the contents of a file from a GitHub repository",
                "use_for": "Tracking AI file reads"
            }
        ],
        "setup_instructions": [
            "1. Ensure you have Node.js installed (for npx)",
            "2. Set GITHUB_TOKEN in your .env file",
            "3. Run generate_mcp_config_file() to create config",
            "4. Restart VS Code/Cursor to load MCP server",
            "5. MCP events will be automatically tracked"
        ],
        "reference": "https://github.com/github/github-mcp-server"
    }


class MCPServerManager:
    """Manager for MCP server lifecycle and monitoring."""
    
    def __init__(self):
        """Initialize MCP Server Manager."""
        self.config_path = ".vscode/mcp.json"
        self.is_configured = self._check_config()
    
    def _check_config(self) -> bool:
        """Check if MCP server is configured."""
        return os.path.exists(self.config_path)
    
    def setup(self) -> Dict:
        """
        Set up MCP server configuration.
        
        Returns:
            Dict with setup status
        """
        if not settings.github_token:
            return {
                "status": "error",
                "message": "GitHub token not configured. Set GITHUB_TOKEN in .env"
            }
        
        try:
            config_file = generate_mcp_config_file(self.config_path)
            self.is_configured = True
            
            return {
                "status": "success",
                "message": "MCP server configured successfully",
                "config_file": config_file,
                "next_steps": [
                    "Restart VS Code/Cursor to load the MCP server",
                    "Use GitHub Copilot with MCP tools enabled",
                    "Events will be tracked automatically"
                ]
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to setup MCP server: {str(e)}"
            }
    
    def get_status(self) -> Dict:
        """
        Get MCP server status.
        
        Returns:
            Dict with status information
        """
        return {
            "configured": self.is_configured,
            "config_path": self.config_path,
            "enabled_in_settings": settings.mcp_server_enabled,
            "tools_available": len(get_mcp_tools_info()["available_tools"])
        }


# Export
def get_mcp_manager() -> MCPServerManager:
    """Get MCP server manager instance."""
    return MCPServerManager()
