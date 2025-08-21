"""
Main entry point for the LLM Agent.
"""
import sys
from pathlib import Path

# Add src to path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

import asyncio
import typer
from typing import Optional

from config import settings

app = typer.Typer(
    name="llm-agent",
    help="Advanced LLM Agent with Tools and Memory - Created by Syed Wamiq",
    add_completion=False
)


@app.command()
def chat(
    model: Optional[str] = typer.Option(None, "--model", "-m", help="LLM model to use"),
    temperature: Optional[float] = typer.Option(None, "--temperature", "-t", help="Temperature for generation"),
    web_ui: bool = typer.Option(False, "--web-ui", "-w", help="Start web UI instead of CLI"),
    port: Optional[int] = typer.Option(None, "--port", "-p", help="Port for web UI")
):
    """Start the LLM Agent chat interface."""
    
    # Override settings if provided
    if model:
        settings.agent_model = model
    if temperature is not None:
        settings.agent_temperature = temperature
    if port:
        settings.web_ui_port = port
    
    if web_ui:
        # Start modern web UI
        print(f"🚀 Starting modern web UI on port {settings.web_ui_port}...")
        print(f"🌐 Open your browser to: http://localhost:{settings.web_ui_port}")
        
        from ui.modern_web import start_server
        asyncio.run(start_server(port=settings.web_ui_port))
    else:
        # Start CLI
        from ui.cli import CLI
        cli = CLI()
        asyncio.run(cli.run())


@app.command()
def tools():
    """List available tools."""
    from tools import tool_registry
    from rich.console import Console
    from rich.table import Table
    
    console = Console()
    
    table = Table(title="🛠️  Available Tools")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Category", style="magenta")
    table.add_column("Description", style="white")
    
    tools = tool_registry.list_tools()
    for tool_name in tools:
        tool = tool_registry.get_tool(tool_name)
        if tool:
            table.add_row(
                tool_name,
                tool.category.value,
                tool.description
            )
    
    console.print(table)


@app.command()
def settings_cmd():
    """Show current settings."""
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    
    console = Console()
    
    settings_text = Text()
    settings_text.append("🤖 Agent Configuration\n\n", style="bold cyan")
    settings_text.append(f"Name: {settings.agent_name}\n", style="white")
    settings_text.append(f"Version: {settings.agent_version}\n", style="white")
    settings_text.append(f"Model: {settings.agent_model}\n", style="white")
    settings_text.append(f"Temperature: {settings.agent_temperature}\n", style="white")
    settings_text.append(f"Max Tokens: {settings.agent_max_tokens}\n", style="white")
    settings_text.append(f"\n🔧 Features\n\n", style="bold cyan")
    settings_text.append(f"Web Search: {'✅' if settings.enable_web_search else '❌'}\n", style="white")
    settings_text.append(f"Code Execution: {'✅' if settings.enable_code_execution else '❌'}\n", style="white")
    settings_text.append(f"File Operations: {'✅' if settings.enable_file_operations else '❌'}\n", style="white")
    settings_text.append(f"\n🌐 Web UI\n\n", style="bold cyan")
    settings_text.append(f"Enabled: {'✅' if settings.web_ui_enabled else '❌'}\n", style="white")
    settings_text.append(f"Port: {settings.web_ui_port}\n", style="white")
    
    panel = Panel(settings_text, title="Settings", border_style="blue")
    console.print(panel)


@app.command()
def test():
    """Run basic functionality tests."""
    from rich.console import Console
    console = Console()
    
    console.print("🧪 Running basic functionality tests...", style="bold cyan")
    
    try:
        # Test imports
        console.print("✓ Testing imports...", style="green")
        from core import get_agent, get_memory_manager
        from tools import tool_registry
        from config import settings
        
        # Test agent initialization
        console.print("✓ Testing agent initialization...", style="green")
        agent = get_agent()
        memory = get_memory_manager()
        
        # Test tools
        console.print("✓ Testing tools registry...", style="green")
        tools = tool_registry.list_tools()
        console.print(f"  Found {len(tools)} tools", style="white")
        
        # Test settings
        console.print("✓ Testing settings...", style="green")
        console.print(f"  Agent: {settings.agent_name} v{settings.agent_version}", style="white")
        console.print(f"  Model: {settings.agent_model}", style="white")
        
        console.print("\n🎉 All basic tests passed!", style="bold green")
        
    except Exception as e:
        console.print(f"\n❌ Test failed: {str(e)}", style="bold red")
        sys.exit(1)


def main():
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()