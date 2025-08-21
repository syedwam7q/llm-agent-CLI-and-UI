"""
Configuration management for the LLM Agent.
"""
import os
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path


class AgentSettings(BaseSettings):
    """Main configuration for the LLM Agent.
    
    Created by: Syed Wamiq
    """
    
    # Agent Identity
    agent_name: str = Field(default="LLM-Agent", description="Name of the agent")
    agent_version: str = Field(default="2.0.0", description="Agent version")
    agent_creator: str = Field(default="Syed Wamiq", description="Creator of the agent")
    
    # LLM Configuration
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API key")
    agent_model: str = Field(default="gpt-4-turbo-preview", description="Default LLM model")
    agent_temperature: float = Field(default=0.7, description="LLM temperature")
    agent_max_tokens: int = Field(default=4000, description="Max tokens per response")
    
    # Tool APIs
    tavily_api_key: Optional[str] = Field(default=None, description="Tavily search API key")
    serp_api_key: Optional[str] = Field(default=None, description="SerpAPI key")
    
    # Feature Flags
    enable_web_search: bool = Field(default=True, description="Enable web search tools")
    enable_code_execution: bool = Field(default=True, description="Enable code execution")
    enable_file_operations: bool = Field(default=True, description="Enable file operations")
    max_file_size_mb: int = Field(default=10, description="Max file size in MB")
    
    # Security
    secret_key: str = Field(default="dev-secret-key", description="Secret key for security")
    allowed_hosts: List[str] = Field(default=["localhost", "127.0.0.1"], description="Allowed hosts")
    
    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: str = Field(default="logs/agent.log", description="Log file path")
    
    # Database
    database_url: str = Field(default="sqlite:///./data/agent.db", description="Database URL")
    
    # Web UI
    web_ui_enabled: bool = Field(default=True, description="Enable web UI")
    web_ui_port: int = Field(default=8000, description="Web UI port")
    
    # Paths
    project_root: Path = Field(default_factory=lambda: Path(__file__).parent.parent.parent)
    data_dir: Path = Field(default_factory=lambda: Path(__file__).parent.parent.parent / "data")
    logs_dir: Path = Field(default_factory=lambda: Path(__file__).parent.parent.parent / "logs")
    
    # Security
    max_file_size_mb: int = Field(default=10, description="Maximum file size in MB")
    allowed_file_types: str = Field(default="txt,json,csv,pdf,docx,xlsx", description="Allowed file types")
    max_concurrent_requests: int = Field(default=10, description="Maximum concurrent requests")
    request_timeout_seconds: int = Field(default=30, description="Request timeout in seconds")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure directories exist
        self.data_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)


# Global settings instance
settings = AgentSettings()


def get_settings() -> AgentSettings:
    """Get the global settings instance."""
    return settings


def reload_settings() -> AgentSettings:
    """Reload settings from environment."""
    global settings
    settings = AgentSettings()
    return settings