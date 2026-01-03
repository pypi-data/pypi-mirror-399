"""
cdd-flow status command

Show current session state.
"""

import os
from datetime import datetime
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from cdd_flow.core.config import get_config
from cdd_flow.core.session import get_session

console = Console()


def format_duration(start_str: str) -> str:
    """Format duration from ISO timestamp to human readable."""
    start = datetime.fromisoformat(start_str)
    delta = datetime.now() - start
    
    hours, remainder = divmod(int(delta.total_seconds()), 3600)
    minutes, _ = divmod(remainder, 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"


@click.command()
@click.pass_context
def status(ctx):
    """Show current session state.
    
    Displays information about the active session, recent landings,
    and checkpoints.
    """
    project_dir = Path(ctx.obj.get("project") or os.getcwd()).resolve()
    config = get_config(project_dir)
    session = get_session(project_dir)
    
    console.print()
    
    # Project info
    console.print(f"[bold]Project:[/bold] {project_dir.name}")
    console.print(f"[dim]Path: {project_dir}[/dim]")
    console.print()
    
    if session is None:
        console.print(Panel(
            "No active session\n\n"
            "Start one with: [bold]cdd-flow start \"your goal\"[/bold]\n"
            "Or just use: [bold]cdd-flow land[/bold] for quick iteration",
            title="Session Status",
            border_style="dim"
        ))
        return
    
    # Session info
    duration = format_duration(session["started"])
    
    session_info = (
        f"[bold]Goal:[/bold] {session['goal']}\n"
        f"[bold]Status:[/bold] {session['status']}\n"
        f"[bold]Duration:[/bold] {duration}\n"
        f"[bold]Iteration:[/bold] {session['iteration']}"
    )
    
    console.print(Panel(session_info, title="Session", border_style="green"))
    
    # Recent landings
    landings = session.get("landings", [])
    if landings:
        console.print()
        table = Table(title="Recent Landings")
        table.add_column("#", style="dim")
        table.add_column("Artifact")
        table.add_column("Files")
        table.add_column("Time", style="dim")
        
        for landing in landings[-5:]:  # Last 5
            files = landing.get("files", [])
            files_str = f"{len(files)} file(s)"
            time_str = landing.get("timestamp", "")[:16]  # Trim to minute
            
            table.add_row(
                str(landing.get("iteration", "?")),
                landing.get("artifact", "?"),
                files_str,
                time_str
            )
        
        console.print(table)
    
    # Checkpoints
    checkpoints = session.get("checkpoints", [])
    if checkpoints:
        console.print()
        table = Table(title="Checkpoints")
        table.add_column("#", style="dim")
        table.add_column("Message")
        table.add_column("Commit", style="dim")
        
        for cp in checkpoints[-5:]:  # Last 5
            table.add_row(
                str(cp.get("iteration", "?")),
                cp.get("message", "?"),
                cp.get("commit", "?")[:7]  # Short SHA
            )
        
        console.print(table)
    
    console.print()
