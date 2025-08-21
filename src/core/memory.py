"""
Memory management for the LLM Agent.
"""
import json
import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path

import sys
from pathlib import Path

# Ensure proper path setup
current_dir = Path(__file__).parent
src_dir = current_dir.parent
sys.path.insert(0, str(src_dir))
sys.path.insert(0, str(current_dir))

from config import settings
from .llm import Message


@dataclass
class ConversationTurn:
    """Represents a single turn in a conversation."""
    id: Optional[int] = None
    session_id: str = ""
    timestamp: datetime = None
    user_message: str = ""
    assistant_message: str = ""
    tools_used: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.tools_used is None:
            self.tools_used = []
        if self.metadata is None:
            self.metadata = {}


class MemoryManager:
    """Manages conversation history and context."""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or str(settings.data_dir / "memory.db")
        self._init_database()
    
    def _init_database(self):
        """Initialize the SQLite database."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    user_message TEXT NOT NULL,
                    assistant_message TEXT NOT NULL,
                    tools_used TEXT,
                    metadata TEXT
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_session_id 
                ON conversations(session_id)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON conversations(timestamp)
            """)
    
    def save_turn(self, turn: ConversationTurn) -> int:
        """Save a conversation turn to memory."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO conversations 
                (session_id, timestamp, user_message, assistant_message, tools_used, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                turn.session_id,
                turn.timestamp.isoformat(),
                turn.user_message,
                turn.assistant_message,
                json.dumps(turn.tools_used),
                json.dumps(turn.metadata)
            ))
            return cursor.lastrowid
    
    def get_conversation_history(
        self, 
        session_id: str, 
        limit: int = 10,
        include_system: bool = True
    ) -> List[Message]:
        """Get conversation history as a list of messages."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT user_message, assistant_message, tools_used
                FROM conversations 
                WHERE session_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (session_id, limit))
            
            messages = []
            
            # Add system message if requested
            if include_system:
                messages.append(Message(
                    role="system",
                    content=self._get_system_prompt()
                ))
            
            # Add conversation history in reverse order (oldest first)
            rows = cursor.fetchall()
            for user_msg, assistant_msg, tools_used in reversed(rows):
                messages.append(Message(role="user", content=user_msg))
                messages.append(Message(role="assistant", content=assistant_msg))
        
        return messages
    
    def get_recent_turns(self, session_id: str, limit: int = 5) -> List[ConversationTurn]:
        """Get recent conversation turns."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT id, session_id, timestamp, user_message, assistant_message, tools_used, metadata
                FROM conversations 
                WHERE session_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (session_id, limit))
            
            turns = []
            for row in cursor.fetchall():
                turn = ConversationTurn(
                    id=row[0],
                    session_id=row[1],
                    timestamp=datetime.fromisoformat(row[2]),
                    user_message=row[3],
                    assistant_message=row[4],
                    tools_used=json.loads(row[5]) if row[5] else [],
                    metadata=json.loads(row[6]) if row[6] else {}
                )
                turns.append(turn)
            
            return turns
    
    def search_conversations(
        self, 
        query: str, 
        session_id: Optional[str] = None,
        limit: int = 10
    ) -> List[ConversationTurn]:
        """Search conversations by content."""
        sql = """
            SELECT id, session_id, timestamp, user_message, assistant_message, tools_used, metadata
            FROM conversations 
            WHERE (user_message LIKE ? OR assistant_message LIKE ?)
        """
        params = [f"%{query}%", f"%{query}%"]
        
        if session_id:
            sql += " AND session_id = ?"
            params.append(session_id)
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(sql, params)
            
            turns = []
            for row in cursor.fetchall():
                turn = ConversationTurn(
                    id=row[0],
                    session_id=row[1],
                    timestamp=datetime.fromisoformat(row[2]),
                    user_message=row[3],
                    assistant_message=row[4],
                    tools_used=json.loads(row[5]) if row[5] else [],
                    metadata=json.loads(row[6]) if row[6] else {}
                )
                turns.append(turn)
            
            return turns
    
    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """Get statistics for a conversation session."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total_turns,
                    MIN(timestamp) as first_message,
                    MAX(timestamp) as last_message,
                    SUM(LENGTH(user_message) + LENGTH(assistant_message)) as total_chars
                FROM conversations 
                WHERE session_id = ?
            """, (session_id,))
            
            row = cursor.fetchone()
            
            # Get tool usage stats
            cursor = conn.execute("""
                SELECT tools_used
                FROM conversations 
                WHERE session_id = ? AND tools_used != '[]'
            """, (session_id,))
            
            all_tools = []
            for (tools_json,) in cursor.fetchall():
                tools = json.loads(tools_json)
                all_tools.extend(tools)
            
            tool_counts = {}
            for tool in all_tools:
                tool_counts[tool] = tool_counts.get(tool, 0) + 1
            
            return {
                "total_turns": row[0],
                "first_message": row[1],
                "last_message": row[2],
                "total_characters": row[3],
                "tools_used": tool_counts
            }
    
    def cleanup_old_conversations(self, days: int = 30) -> int:
        """Clean up conversations older than specified days."""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                DELETE FROM conversations 
                WHERE timestamp < ?
            """, (cutoff_date.isoformat(),))
            
            return cursor.rowcount
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the agent."""
        return f"""You are {settings.agent_name}, an advanced AI assistant with access to various tools.

Your capabilities include:
- Web search and information retrieval
- Mathematical calculations and code execution
- File operations and data analysis
- Data visualization and processing

Guidelines:
1. Always be helpful, accurate, and concise
2. Use tools when they can provide better or more current information
3. Explain your reasoning when using tools
4. If you're unsure about something, say so
5. Maintain context from previous messages in the conversation

Current session context: You have access to conversation history and can reference previous interactions."""


# Global memory manager instance
memory_manager = MemoryManager()


def get_memory_manager() -> MemoryManager:
    """Get the global memory manager instance."""
    return memory_manager