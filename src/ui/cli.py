"""
Beautiful CLI interface for the LLM Agent.
"""
import asyncio
import sys
from typing import Optional
from datetime import datetime

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.live import Live
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory

import sys
from pathlib import Path

# Ensure proper path setup
current_dir = Path(__file__).parent
src_dir = current_dir.parent
sys.path.insert(0, str(src_dir))

from core import agent
from config.settings import settings
from tools import tool_registry


class CLI:
    """Rich CLI interface for the LLM Agent."""
    
    def __init__(self):
        self.console = Console()
        self.agent = agent
        self.session_id: Optional[str] = None
        self.history = InMemoryHistory()
        # Initialize prompt session without auto-suggest to avoid compatibility issues
        try:
            self.prompt_session = PromptSession(history=self.history)
        except Exception:
            # Fallback to basic prompt session
            self.prompt_session = PromptSession()
    
    def print_banner(self):
        """Print the application banner."""
        # Import settings locally to avoid conflicts
        from config.settings import settings as app_settings
        
        banner_text = f"""
╔══════════════════════════════════════════════════════════════╗
║                    🤖 {app_settings.agent_name} v{app_settings.agent_version}                       ║
║              Advanced AI Assistant with Tools                ║
║                     Created by Syed Wamiq                    ║
╚══════════════════════════════════════════════════════════════╝
        """
        
        self.console.print(Panel(
            banner_text,
            style="bold blue",
            border_style="bright_blue"
        ))
        
        # Show available features
        features = [
            "🔍 Web Search & Information Retrieval",
            "🧮 Mathematical Calculations & Code Execution", 
            "📁 File Operations & Data Analysis",
            "📊 Data Visualization & Processing",
            "💾 Conversation Memory & Context",
            "🔧 Extensible Tool System"
        ]
        
        features_text = "\n".join(features)
        self.console.print(Panel(
            features_text,
            title="✨ Features",
            style="green",
            border_style="bright_green"
        ))
    
    def print_help(self):
        """Print help information."""
        help_table = Table(title="Available Commands", show_header=True, header_style="bold magenta")
        help_table.add_column("Command", style="cyan", width=20)
        help_table.add_column("Description", style="white")
        
        commands = [
            ("/help", "Show this help message"),
            ("/tools", "List available tools"),
            ("/history", "Show conversation history"),
            ("/session", "Show current session info"),
            ("/search <query>", "Search conversation history"),
            ("/clear", "Clear the screen"),
            ("/export", "Export conversation"),
            ("/settings", "Show current settings"),
            ("/quit", "Exit the application")
        ]
        
        for cmd, desc in commands:
            help_table.add_row(cmd, desc)
        
        self.console.print(help_table)
    
    def print_tools(self):
        """Print available tools."""
        tools = self.agent.list_available_tools()
        
        tools_table = Table(title="Available Tools", show_header=True, header_style="bold magenta")
        tools_table.add_column("Tool", style="cyan", width=20)
        tools_table.add_column("Category", style="yellow", width=15)
        tools_table.add_column("Description", style="white")
        
        for tool in tools:
            tools_table.add_row(
                tool["name"],
                tool["category"],
                tool["description"]
            )
        
        self.console.print(tools_table)
    
    async def print_session_info(self):
        """Print current session information."""
        if not self.session_id:
            self.console.print("[yellow]No active session[/yellow]")
            return
        
        info = self.agent.get_session_info(self.session_id)
        
        if "error" in info:
            self.console.print(f"[red]Error: {info['error']}[/red]")
            return
        
        session_table = Table(title="Session Information", show_header=False)
        session_table.add_column("Property", style="cyan", width=20)
        session_table.add_column("Value", style="white")
        
        session_table.add_row("Session ID", info["session_id"])
        session_table.add_row("Created", info["created_at"])
        session_table.add_row("Last Activity", info["last_activity"])
        session_table.add_row("Total Turns", str(info["stats"]["total_turns"]))
        session_table.add_row("Total Characters", str(info["stats"]["total_characters"]))
        
        if info["stats"]["tools_used"]:
            tools_used = ", ".join([f"{tool}({count})" for tool, count in info["stats"]["tools_used"].items()])
            session_table.add_row("Tools Used", tools_used)
        
        self.console.print(session_table)
    
    async def search_history(self, query: str):
        """Search conversation history."""
        if not query.strip():
            self.console.print("[yellow]Please provide a search query[/yellow]")
            return
        
        results = await self.agent.search_conversation_history(query, self.session_id)
        
        if not results:
            self.console.print("[yellow]No results found[/yellow]")
            return
        
        self.console.print(f"\n[bold]Found {len(results)} results for '{query}':[/bold]\n")
        
        for i, result in enumerate(results, 1):
            timestamp = datetime.fromisoformat(result["timestamp"]).strftime("%Y-%m-%d %H:%M")
            
            panel_content = f"""
[bold cyan]User:[/bold cyan] {result['user_message']}

[bold green]Assistant:[/bold green] {result['assistant_message']}

[dim]Tools used: {', '.join(result['tools_used']) if result['tools_used'] else 'None'}[/dim]
            """
            
            self.console.print(Panel(
                panel_content.strip(),
                title=f"Result {i} - {timestamp}",
                border_style="dim"
            ))
    
    def print_settings(self):
        """Print current settings."""
        settings_table = Table(title="Current Settings", show_header=False)
        settings_table.add_column("Setting", style="cyan", width=25)
        settings_table.add_column("Value", style="white")
        
        settings_data = [
            ("Agent Name", settings.agent_name),
            ("Agent Version", settings.agent_version),
            ("Model", settings.agent_model),
            ("Temperature", str(settings.agent_temperature)),
            ("Max Tokens", str(settings.agent_max_tokens)),
            ("Web Search Enabled", "✅" if settings.enable_web_search else "❌"),
            ("Code Execution Enabled", "✅" if settings.enable_code_execution else "❌"),
            ("File Operations Enabled", "✅" if settings.enable_file_operations else "❌"),
            ("Web UI Enabled", "✅" if settings.web_ui_enabled else "❌"),
        ]
        
        for setting, value in settings_data:
            settings_table.add_row(setting, str(value))
        
        self.console.print(settings_table)
    
    async def process_user_input(self, user_input: str) -> bool:
        """Process user input and return whether to continue."""
        user_input = user_input.strip()
        
        # Handle commands
        if user_input.startswith('/'):
            command_parts = user_input[1:].split(' ', 1)
            command = command_parts[0].lower()
            args = command_parts[1] if len(command_parts) > 1 else ""
            
            if command in ['quit', 'exit', 'q']:
                return False
            elif command == 'help':
                self.print_help()
            elif command == 'tools':
                self.print_tools()
            elif command == 'session':
                await self.print_session_info()
            elif command == 'search':
                await self.search_history(args)
            elif command == 'clear':
                self.console.clear()
                self.print_banner()
            elif command == 'settings':
                self.print_settings()
            elif command == 'history':
                await self.search_history("")  # Show all history
            else:
                self.console.print(f"[red]Unknown command: {command}[/red]")
                self.console.print("Type [cyan]/help[/cyan] for available commands")
            
            return True
        
        # Handle regular messages
        if not user_input:
            return True
        
        # Create session if needed
        if not self.session_id:
            self.session_id = self.agent.conversation_manager.create_session()
            self.console.print(f"[dim]Started new session: {self.session_id[:8]}...[/dim]\n")
        
        # Show thinking indicator
        with self.console.status("[yellow]🤔 Thinking...[/yellow]"):
            try:
                # Get response from agent (synchronous for now)
                response = await self.agent.process_message_sync(
                    user_input, 
                    session_id=self.session_id
                )
                
                # Display response with better formatting
                response_panel = Panel(
                    Markdown(response),
                    title="🤖 AI Assistant",
                    subtitle=f"[dim]Powered by {settings.agent_model} • Created by Syed Wamiq[/dim]",
                    style="green",
                    border_style="bright_green",
                    padding=(1, 2)
                )
                self.console.print(response_panel)

                # Extract and print plain clickable links for terminal (Cmd/Ctrl+Click)
                try:
                    import re as _re
                    urls = []

                    # Markdown-style links: [text](https://...)
                    for m in _re.finditer(r"\[[^\]]+\]\((https?://[^\s)]+)\)", response):
                        url = m.group(1)
                        if url not in urls:
                            urls.append(url)

                    # Bare URLs: https://...
                    for m in _re.finditer(r"(https?://[^\s\)>\]]+)", response):
                        url = m.group(1)
                        # Strip trailing punctuation that often follows URLs in prose
                        url = url.rstrip('.,;!?)]')
                        if url not in urls:
                            urls.append(url)

                    if urls:
                        self.console.print()  # spacing
                        self.console.print("[bold]Links:[/bold]")
                        for u in urls:
                            # Print raw URL to ensure terminal auto-links it
                            self.console.print(u)
                except Exception:
                    # Never let link extraction break the chat flow
                    pass
            
            except Exception as e:
                self.console.print(Panel(
                    f"❌ Error: {str(e)}",
                    style="red",
                    border_style="red"
                ))
        
        self.console.print()  # Add spacing
        return True
    
    async def run(self):
        """Run the CLI interface."""
        self.console.clear()
        self.print_banner()
        
        self.console.print("\n[dim]Type your message or use /help for commands. Press Ctrl+C to exit.[/dim]\n")
        
        try:
            while True:
                try:
                    # Get user input with simple prompt to avoid compatibility issues
                    user_input = Prompt.ask("[bold cyan]💬 You[/bold cyan]")
                    
                    # Process input
                    should_continue = await self.process_user_input(user_input)
                    if not should_continue:
                        break
                
                except KeyboardInterrupt:
                    if Confirm.ask("\n[yellow]Are you sure you want to exit?[/yellow]"):
                        break
                    else:
                        self.console.print()
                        continue
                
                except EOFError:
                    break
        
        except Exception as e:
            self.console.print(f"\n[red]Unexpected error: {str(e)}[/red]")
        
        finally:
            self.console.print("\n[dim]Goodbye! 👋[/dim]")


# CLI application using Typer
app = typer.Typer(
    name="llm-agent",
    help="Advanced LLM Agent with Tools",
    add_completion=False
)


@app.command()
def chat(
    model: Optional[str] = typer.Option(None, "--model", "-m", help="LLM model to use"),
    temperature: Optional[float] = typer.Option(None, "--temperature", "-t", help="Temperature for generation"),
    web_ui: bool = typer.Option(False, "--web-ui", "-w", help="Start web UI instead of CLI")
):
    """Start the LLM Agent in interactive mode."""
    
    # Override settings if provided
    if model:
        settings.agent_model = model
    if temperature is not None:
        settings.agent_temperature = temperature
    
    if web_ui:
        # Web UI has been removed - CLI only
        print("❌ Web UI has been removed. This is now a CLI-only application.")
        print("💡 Use the CLI interface instead by running without --web-ui flag.")
        sys.exit(1)
    else:
        # Start CLI
        cli = CLI()
        asyncio.run(cli.run())


@app.command()
def tools():
    """List available tools."""
    console = Console()
    cli = CLI()
    cli.console = console
    cli.print_tools()


@app.command()
def show_settings():
    """Show current settings."""
    console = Console()
    cli = CLI()
    cli.console = console
    cli.print_settings()


if __name__ == "__main__":
    app()