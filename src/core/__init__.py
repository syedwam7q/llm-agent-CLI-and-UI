"""Core package for the LLM Agent."""

import sys
from pathlib import Path

# Ensure proper path setup
current_dir = Path(__file__).parent
src_dir = current_dir.parent
sys.path.insert(0, str(src_dir))
sys.path.insert(0, str(current_dir))

from .llm import llm_manager, get_llm_manager, Message, FunctionCall
from .memory import MemoryManager, memory_manager, get_memory_manager
from .agent import Agent, ConversationManager, agent, get_agent

__all__ = [
    "llm_manager",
    "get_llm_manager", 
    "Message",
    "FunctionCall",
    "Agent",
    "ConversationManager",
    "MemoryManager",
    "agent",
    "get_agent",
    "memory_manager",
    "get_memory_manager"
]