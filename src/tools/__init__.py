"""Tools package for the LLM Agent."""

import sys
from pathlib import Path

# Ensure proper path setup
current_dir = Path(__file__).parent
src_dir = current_dir.parent
sys.path.insert(0, str(src_dir))
sys.path.insert(0, str(current_dir))

from base import BaseTool, ToolResult, ToolCategory, tool_registry, register_tool, get_tool_registry

# Import all tool modules to register them
import search_tools
import computation_tools
import file_tools
import data_tools

__all__ = [
    "BaseTool",
    "ToolResult", 
    "ToolCategory",
    "tool_registry",
    "register_tool",
    "get_tool_registry"
]