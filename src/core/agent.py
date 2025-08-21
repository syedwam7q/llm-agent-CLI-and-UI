"""
Main agent implementation with LLM integration and tool orchestration.
"""
import json
import uuid
import asyncio
from typing import List, Dict, Any, Optional, AsyncGenerator
from datetime import datetime

import sys
from pathlib import Path

# Ensure proper path setup
current_dir = Path(__file__).parent
src_dir = current_dir.parent
sys.path.insert(0, str(src_dir))
sys.path.insert(0, str(current_dir))

from .llm import llm_manager, Message, FunctionCall
from .memory import memory_manager, ConversationTurn
from tools import tool_registry, ToolResult
from config import settings


class ConversationManager:
    """Manages conversation sessions and context."""
    
    def __init__(self):
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
    
    def create_session(self, user_id: Optional[str] = None) -> str:
        """Create a new conversation session."""
        session_id = str(uuid.uuid4())
        self.active_sessions[session_id] = {
            "user_id": user_id,
            "created_at": datetime.now(),
            "last_activity": datetime.now(),
            "context": {}
        }
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session information."""
        return self.active_sessions.get(session_id)
    
    def update_session_activity(self, session_id: str):
        """Update last activity timestamp for a session."""
        if session_id in self.active_sessions:
            self.active_sessions[session_id]["last_activity"] = datetime.now()
    
    def cleanup_inactive_sessions(self, hours: int = 24):
        """Clean up inactive sessions."""
        cutoff = datetime.now().timestamp() - (hours * 3600)
        inactive_sessions = [
            sid for sid, session in self.active_sessions.items()
            if session["last_activity"].timestamp() < cutoff
        ]
        
        for session_id in inactive_sessions:
            del self.active_sessions[session_id]
        
        return len(inactive_sessions)


class Agent:
    """Main LLM Agent with tool integration and memory."""
    
    def __init__(self):
        self.llm = llm_manager
        self.tools = tool_registry
        self.memory = memory_manager
        self.conversation_manager = ConversationManager()
    
    def process_message(
        self, 
        message: str, 
        session_id: Optional[str] = None,
        stream: bool = False
    ):
        """Process a user message and return response."""
        if stream:
            # Return the async generator directly
            return self.process_message_stream(message, session_id)
        else:
            # Return a coroutine for non-streaming
            return self.process_message_sync(message, session_id)
    
    async def process_message_sync(
        self, 
        message: str, 
        session_id: Optional[str] = None
    ) -> str:
        """Process a user message and return complete response."""
        
        # Create session if not provided
        if not session_id:
            session_id = self.conversation_manager.create_session()
        
        # Update session activity
        self.conversation_manager.update_session_activity(session_id)
        
        try:
            # Get conversation history
            conversation_history = self.memory.get_conversation_history(
                session_id, limit=10
            )
            
            # Add current user message
            conversation_history.append(Message(role="user", content=message))
            
            # Get available tools
            function_schemas = self.tools.to_function_schemas()
            
            # Non-streaming response
            response = await self._generate_response(
                conversation_history, function_schemas, session_id, message
            )
            return response
        
        except Exception as e:
            return f"I encountered an error: {str(e)}"
    
    async def process_message_stream(
        self, 
        message: str, 
        session_id: Optional[str] = None
    ):
        """Process a user message and stream response."""
        
        # Create session if not provided
        if not session_id:
            session_id = self.conversation_manager.create_session()
        
        # Update session activity
        self.conversation_manager.update_session_activity(session_id)
        
        try:
            # Get conversation history
            conversation_history = self.memory.get_conversation_history(
                session_id, limit=10
            )
            
            # Add current user message
            conversation_history.append(Message(role="user", content=message))
            
            # Get available tools
            function_schemas = self.tools.to_function_schemas()
            
            # Stream response
            async for chunk in self._stream_response(
                conversation_history, function_schemas, session_id, message
            ):
                yield chunk
        
        except Exception as e:
            yield f"I encountered an error: {str(e)}"
    
    async def _generate_response(
        self, 
        conversation_history: List[Message],
        function_schemas: List[Dict[str, Any]],
        session_id: str,
        original_message: str
    ) -> str:
        """Generate a complete response."""
        
        tools_used = []
        max_iterations = 5  # Prevent infinite loops
        iteration = 0
        
        current_messages = conversation_history.copy()
        
        while iteration < max_iterations:
            iteration += 1
            
            # Get LLM response
            response = await self.llm.chat_completion(
                messages=current_messages,
                functions=function_schemas if function_schemas else None
            )
            
            # Handle function calls
            if isinstance(response, FunctionCall):
                # Execute the tool
                tool_result = await self.tools.execute_tool(
                    response.name, **response.arguments
                )
                tools_used.append(response.name)
                
                # Add function call and result to conversation
                current_messages.append(Message(
                    role="assistant",
                    content="",
                    function_call={
                        "name": response.name,
                        "arguments": json.dumps(response.arguments)
                    }
                ))
                
                current_messages.append(Message(
                    role="function",
                    name=response.name,
                    content=json.dumps(tool_result.to_dict())
                ))
                
                # Continue the loop to get final response
                continue
            
            else:
                # We have a final text response
                final_response = response
                break
        
        else:
            final_response = "I apologize, but I reached the maximum number of tool calls. Please try rephrasing your request."
        
        # Save conversation turn to memory
        turn = ConversationTurn(
            session_id=session_id,
            user_message=original_message,
            assistant_message=final_response,
            tools_used=tools_used,
            metadata={"iterations": iteration}
        )
        self.memory.save_turn(turn)
        
        return final_response
    
    async def _stream_response(
        self,
        conversation_history: List[Message],
        function_schemas: List[Dict[str, Any]],
        session_id: str,
        original_message: str
    ) -> AsyncGenerator[str, None]:
        """Stream response with tool execution."""
        
        tools_used = []
        max_iterations = 5
        iteration = 0
        
        current_messages = conversation_history.copy()
        final_response_parts = []
        
        while iteration < max_iterations:
            iteration += 1
            
            # Check if we need to use tools first
            response = await self.llm.chat_completion(
                messages=current_messages,
                functions=function_schemas if function_schemas else None
            )
            
            if isinstance(response, FunctionCall):
                # Notify about tool usage
                yield f"\n🔧 Using tool: {response.name}\n"
                
                # Execute the tool
                tool_result = await self.tools.execute_tool(
                    response.name, **response.arguments
                )
                tools_used.append(response.name)
                
                # Add function call and result to conversation
                current_messages.append(Message(
                    role="assistant",
                    content="",
                    function_call={
                        "name": response.name,
                        "arguments": json.dumps(response.arguments)
                    }
                ))
                
                current_messages.append(Message(
                    role="function",
                    name=response.name,
                    content=json.dumps(tool_result.to_dict())
                ))
                
                # Show tool result summary
                if tool_result.success:
                    yield f"✅ Tool completed successfully\n\n"
                else:
                    yield f"❌ Tool failed: {tool_result.error}\n\n"
                
                continue
            
            else:
                # Stream the final response
                async for chunk in self.llm.stream_completion(
                    messages=current_messages
                ):
                    final_response_parts.append(chunk)
                    yield chunk
                
                break
        
        # Save conversation turn to memory
        final_response = "".join(final_response_parts)
        turn = ConversationTurn(
            session_id=session_id,
            user_message=original_message,
            assistant_message=final_response,
            tools_used=tools_used,
            metadata={"iterations": iteration, "streamed": True}
        )
        self.memory.save_turn(turn)
    
    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """Get information about a conversation session."""
        session = self.conversation_manager.get_session(session_id)
        if not session:
            return {"error": "Session not found"}
        
        stats = self.memory.get_session_stats(session_id)
        
        return {
            "session_id": session_id,
            "created_at": session["created_at"].isoformat(),
            "last_activity": session["last_activity"].isoformat(),
            "stats": stats
        }
    
    def list_available_tools(self) -> List[Dict[str, Any]]:
        """List all available tools with their descriptions."""
        tools_info = []
        
        for tool_name, tool in self.tools.tools.items():
            tools_info.append({
                "name": tool_name,
                "description": tool.description,
                "category": tool.category.value,
                "parameters": [
                    {
                        "name": param.name,
                        "type": param.type,
                        "description": param.description,
                        "required": param.required
                    }
                    for param in tool.parameters
                ]
            })
        
        return tools_info
    
    async def search_conversation_history(
        self, 
        query: str, 
        session_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search conversation history."""
        turns = self.memory.search_conversations(query, session_id)
        
        return [
            {
                "id": turn.id,
                "session_id": turn.session_id,
                "timestamp": turn.timestamp.isoformat(),
                "user_message": turn.user_message[:200] + "..." if len(turn.user_message) > 200 else turn.user_message,
                "assistant_message": turn.assistant_message[:200] + "..." if len(turn.assistant_message) > 200 else turn.assistant_message,
                "tools_used": turn.tools_used
            }
            for turn in turns
        ]


# Global agent instance
agent = Agent()


def get_agent() -> Agent:
    """Get the global agent instance."""
    return agent