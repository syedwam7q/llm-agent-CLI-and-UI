"""
Tests for UI components of LLM Agent.
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))

def test_cli_initialization():
    """Test CLI initialization."""
    try:
        from ui.cli import CLI
        
        cli = CLI()
        assert cli is not None
        
    except Exception as e:
        pytest.fail(f"CLI initialization test failed: {e}")

def test_web_ui_routes():
    """Test web UI routes."""
    try:
        from fastapi import FastAPI
        from ui.simple_enhanced_web import create_app
        
        app = create_app()
        client = TestClient(app)
        
        # Test root route
        response = client.get("/")
        assert response.status_code == 200
        
        # Test static files route
        response = client.get("/static/js/main.js")
        assert response.status_code == 200
        
        # Test health check route
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
        
    except Exception as e:
        pytest.fail(f"Web UI routes test failed: {e}")

def test_session_management():
    """Test session management."""
    try:
        from core.agent import get_agent
        from core.memory import get_memory_manager

        agent = get_agent()
        memory_manager = get_memory_manager()

        # Create a new session
        session_id = agent.conversation_manager.create_session()
        assert session_id is not None

        # Get session
        session = agent.conversation_manager.get_session(session_id)
        assert session is not None

        # Test session stats
        stats = memory_manager.get_session_stats(session_id)
        assert stats is not None
        assert "total_turns" in stats

    except Exception as e:
        pytest.fail(f"Session management test failed: {e}")