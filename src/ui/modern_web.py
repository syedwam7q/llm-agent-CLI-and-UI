"""
Modern Web UI for LLM Agent - Inspired by ChatGPT/Gemini
Created by: Syed Wamiq

Features:
- Modern ChatGPT-like design with glassmorphism effects
- Real-time streaming with WebSocket communication
- Drag & Drop file upload with multiple format support
- Responsive design for all devices
- Session/chat management with create/delete/switch functionality
- Markdown support with syntax highlighting
- Error handling with user-friendly messages
- Performance optimization for smooth interactions
"""

import os
import json
import uuid
import asyncio
import aiofiles
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import sys
current_dir = Path(__file__).parent
src_dir = current_dir.parent
sys.path.insert(0, str(src_dir))

from core.agent import agent
from config.settings import settings
from utils.file_utils import FileProcessor


class ChatMessage(BaseModel):
    """Chat message model."""
    id: str
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime
    tools_used: List[str] = []
    file_attachments: List[Dict[str, Any]] = []


class ChatSession(BaseModel):
    """Chat session model."""
    id: str
    title: str
    created_at: datetime
    last_activity: datetime
    message_count: int = 0


class ConnectionManager:
    """Manages WebSocket connections for real-time communication."""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.session_connections: Dict[str, str] = {}  # session_id -> connection_id
    
    async def connect(self, websocket: WebSocket, connection_id: str):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections[connection_id] = websocket
    
    def disconnect(self, connection_id: str):
        """Remove a WebSocket connection."""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        
        # Remove from session connections
        for session_id, conn_id in list(self.session_connections.items()):
            if conn_id == connection_id:
                del self.session_connections[session_id]
    
    async def send_message(self, connection_id: str, message: dict):
        """Send a message to a specific connection."""
        if connection_id in self.active_connections:
            websocket = self.active_connections[connection_id]
            try:
                await websocket.send_json(message)
            except Exception:
                self.disconnect(connection_id)
    
    async def stream_response(self, connection_id: str, session_id: str, user_message: str, files: List[Dict[str, Any]] = None):
        """Stream AI response to client."""
        try:
            # Send typing indicator
            await self.send_message(connection_id, {
                "type": "typing_start",
                "session_id": session_id
            })
            
            # Process files and include in message context
            enhanced_message = user_message
            if files:
                file_context = "\n\n--- Files Already Uploaded and Processed ---\n"
                file_context += "Note: The following file contents are already available for analysis. Do not use the filereader tool.\n\n"
                
                for file_info in files:
                    file_context += f"📄 File: {file_info['filename']} ({file_info['type'].upper()}, {file_info['size']} bytes)\n"
                    file_context += f"Content:\n{file_info['full_content']}\n"
                    file_context += "--- End of File ---\n\n"
                
                enhanced_message = f"{user_message}\n{file_context}"
            
            # Process message with streaming
            response_parts = []
            async for chunk in agent.process_message_stream(enhanced_message, session_id):
                response_parts.append(chunk)
                await self.send_message(connection_id, {
                    "type": "stream_chunk",
                    "session_id": session_id,
                    "content": chunk
                })
            
            # Send completion
            full_response = "".join(response_parts)
            await self.send_message(connection_id, {
                "type": "stream_complete",
                "session_id": session_id,
                "full_content": full_response
            })
            
        except Exception as e:
            await self.send_message(connection_id, {
                "type": "error",
                "session_id": session_id,
                "message": f"Error processing message: {str(e)}"
            })


# Initialize FastAPI app
app = FastAPI(
    title="LLM Agent - Modern Web UI",
    description="Advanced AI Assistant with Modern ChatGPT-like Interface",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize connection manager
manager = ConnectionManager()

# Setup static files and templates
static_dir = Path(__file__).parent / "static"
templates_dir = Path(__file__).parent / "templates"

# Create directories if they don't exist
static_dir.mkdir(exist_ok=True)
templates_dir.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
templates = Jinja2Templates(directory=str(templates_dir))

# File processor for uploads
file_processor = FileProcessor()

# In-memory session storage (in production, use Redis or database)
chat_sessions: Dict[str, ChatSession] = {}
session_messages: Dict[str, List[ChatMessage]] = {}


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main chat interface."""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "agent_name": settings.agent_name,
        "agent_version": settings.agent_version,
        "creator": settings.agent_creator
    })


@app.websocket("/ws/{connection_id}")
async def websocket_endpoint(websocket: WebSocket, connection_id: str):
    """WebSocket endpoint for real-time communication."""
    await manager.connect(websocket, connection_id)
    
    try:
        while True:
            data = await websocket.receive_json()
            message_type = data.get("type")
            
            if message_type == "chat_message":
                session_id = data.get("session_id")
                user_message = data.get("message")
                files = data.get("files", [])
                
                if not session_id or not user_message:
                    continue
                
                # Store session connection mapping
                manager.session_connections[session_id] = connection_id
                
                # Add user message to session
                if session_id not in session_messages:
                    session_messages[session_id] = []
                
                user_msg = ChatMessage(
                    id=str(uuid.uuid4()),
                    role="user",
                    content=user_message,
                    timestamp=datetime.now(),
                    file_attachments=files
                )
                session_messages[session_id].append(user_msg)
                
                # Update session activity
                if session_id in chat_sessions:
                    chat_sessions[session_id].last_activity = datetime.now()
                    chat_sessions[session_id].message_count += 1
                
                # Stream AI response with files
                await manager.stream_response(connection_id, session_id, user_message, files)
            
            elif message_type == "ping":
                await websocket.send_json({"type": "pong"})
    
    except WebSocketDisconnect:
        manager.disconnect(connection_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(connection_id)


@app.post("/api/sessions")
async def create_session():
    """Create a new chat session."""
    session_id = str(uuid.uuid4())
    session = ChatSession(
        id=session_id,
        title="New Chat",
        created_at=datetime.now(),
        last_activity=datetime.now()
    )
    
    chat_sessions[session_id] = session
    session_messages[session_id] = []
    
    return {"session": session.dict()}


@app.get("/api/sessions")
async def get_sessions():
    """Get all chat sessions."""
    sessions = [session.dict() for session in chat_sessions.values()]
    sessions.sort(key=lambda x: x["last_activity"], reverse=True)
    return {"sessions": sessions}


@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """Get a specific session with messages."""
    if session_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = chat_sessions[session_id]
    messages = session_messages.get(session_id, [])
    
    return {
        "session": session.dict(),
        "messages": [msg.dict() for msg in messages]
    }


@app.put("/api/sessions/{session_id}")
async def update_session(session_id: str, title: str = Form(...)):
    """Update session title."""
    if session_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    chat_sessions[session_id].title = title
    return {"success": True}


@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a chat session."""
    if session_id in chat_sessions:
        del chat_sessions[session_id]
    if session_id in session_messages:
        del session_messages[session_id]
    
    return {"success": True}


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Handle file uploads with support for multiple formats."""
    try:
        # Validate file size
        file_size = 0
        content = await file.read()
        file_size = len(content)
        
        if file_size > settings.max_file_size_mb * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {settings.max_file_size_mb}MB"
            )
        
        # Validate file type
        allowed_types = settings.allowed_file_types.split(",")
        file_ext = file.filename.split(".")[-1].lower() if "." in file.filename else ""
        
        if file_ext not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"File type not allowed. Supported types: {', '.join(allowed_types)}"
            )
        
        # Save file
        file_id = str(uuid.uuid4())
        file_path = settings.data_dir / "uploads" / f"{file_id}.{file_ext}"
        
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(content)
        
        # Process file content
        try:
            processed_content = await file_processor.process_file(file_path)
            
            return {
                "file_id": file_id,
                "filename": file.filename,
                "size": file_size,
                "type": file_ext,
                "content_preview": processed_content[:500] + "..." if len(processed_content) > 500 else processed_content,
                "full_content": processed_content
            }
        
        except Exception as e:
            # Clean up file if processing fails
            if file_path.exists():
                file_path.unlink()
            raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.get("/api/tools")
async def get_tools():
    """Get available tools."""
    tools = agent.list_available_tools()
    return {"tools": tools}


@app.get("/api/settings")
async def get_settings():
    """Get current settings."""
    return {
        "agent_name": settings.agent_name,
        "agent_version": settings.agent_version,
        "creator": settings.agent_creator,
        "model": settings.agent_model,
        "temperature": settings.agent_temperature,
        "max_tokens": settings.agent_max_tokens,
        "features": {
            "web_search": settings.enable_web_search,
            "code_execution": settings.enable_code_execution,
            "file_operations": settings.enable_file_operations
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": settings.agent_version,
        "active_sessions": len(chat_sessions),
        "active_connections": len(manager.active_connections)
    }


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    return app


async def start_server(host: str = "0.0.0.0", port: int = 8000):
    """Start the web server."""
    config = uvicorn.Config(
        app,
        host=host,
        port=port,
        log_level="info",
        access_log=True
    )
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    uvicorn.run(
        "modern_web:app",
        host="0.0.0.0",
        port=settings.web_ui_port,
        reload=True,
        log_level="info"
    )