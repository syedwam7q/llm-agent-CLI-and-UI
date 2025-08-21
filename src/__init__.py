"""LLM Agent - Advanced AI Assistant with Tools."""

__version__ = "2.0.0"
__author__ = "LLM Agent Team"
__description__ = "Advanced AI Assistant with Tools and Memory"

from .core.agent import get_agent
from .config import get_settings

__all__ = ["get_agent", "get_settings"]