"""UI package for the LLM Agent."""

import sys
from pathlib import Path

# Ensure proper path setup
current_dir = Path(__file__).parent
src_dir = current_dir.parent
sys.path.insert(0, str(src_dir))

from .cli import CLI

__all__ = ["CLI"]