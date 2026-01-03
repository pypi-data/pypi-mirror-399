"""
cdd-flow history command

Show session iterations and checkpoints.
"""

import os
from datetime import datetime
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from cdd_flow.core.session import get_session, get_session_history

console = Console()


def format_timestamp(iso_str: str) -> str:
    """Format ISO timestamp to human readable."""
    try:
        dt = datetime.fromisoformat(iso_str)
        return dt.strftime("%Y-%m-%d %H:%M")
    except (ValueError, TypeError):
        return iso_str[:16] if iso_str else "?"


def format_duration(seconds: int) -> str:
    """Format seconds to human readable duration."""
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m"
    elif minutes > 0:
        return f"{minutes}m"
    return f"{secs}s"


@click.command()
@click.option("--all", "show_all", is_flag=True, help="Show all archived sessions")
@click.pass_context
def history(ctx, show_all):
    """Show session iterations and checkpoints.
    
    By default, shows the current session's history.
    Use --all to show archived sessions.
    """
    project_dir = Path(ctx.obj.get("project") or os.getcwd()).resolve()
    
    console.print()
    
    if show_all:
        # Show archived sessions
        sessions = get_session_history(project_dir)
        
        if not sessions:
            console.print("[dim]No archived sessions found[/dim]")
            return
        
        table = Table(title="Session History")
        table.add_column("Goal", style="bold")
        table.add_column("Status")
        table.add_column("Iterations")
        table.add_column("Checkpoints")
        table.add_column("Duration")
        table.add_column("Completed", style="dim")
        
        for s in sessions[:10]:  # Last 10
            status_style = "green" if s.get("status") == "completed" else "red"
            summary = s.get("summary", {})
            
            completed_at = s.get("completed") or s.get("abandoned") or ""
            
            table.add_row(
                s.get("goal", "?")[:30],
                f"[{status_style}]{s.get('status', '?')}[/{status_style}]",
                str(summary.get("iterations", len(s.get("landings", [])))),
                str(summary.get("checkpoints", len(s.get("checkpoints", [])))),
                format_duration(summary.get("duration_seconds", 0)),
                format_timestamp(completed_at),
            )
        
        console.print(table)
        console.print()
        return
    
    # Show current session history
    session = get_session(project_dir)
    
    if session is None:
        console.print("[dim]No active session[/dim]")
        console.print("\nUse --all to see archived sessions")
        return
    
    # Session info
    console.print(Panel(
        f"[bold]Goal:[/bold] {session['goal']}\n"
        f"[bold]Started:[/bold] {format_timestamp(session['started'])}\n"
        f"[bold]Iteration:[/bold] {session.get('iteration', 0)}",
        title="Current Session",
        border_style="green"
    ))
    
    # Landings
    landings = session.get("landings", [])
    if landings:
        console.print()
        table = Table(title="Landings")
        table.add_column("#", style="dim", width=4)
        table.add_column("Artifact")
        table.add_column("Files", width=8)
        table.add_column("Time", style="dim")
        
        for landing in landings:
            files = landing.get("files", [])
            created = sum(1 for f in files if f.get("action") == "created")
            modified = sum(1 for f in files if f.get("action") == "modified")
            files_str = f"+{created} ~{modified}"
            
            table.add_row(
                str(landing.get("iteration", "?")),
                landing.get("artifact", "?"),
                files_str,
                format_timestamp(landing.get("timestamp", "")),
            )
        
        console.print(table)
    
    # Checkpoints
    checkpoints = session.get("checkpoints", [])
    if checkpoints:
        console.print()
        table = Table(title="Checkpoints")
        table.add_column("#", style="dim", width=4)
        table.add_column("Message")
        table.add_column("Commit", style="cyan", width=10)
        table.add_column("Verified")
        table.add_column("Time", style="dim")
        
        for cp in checkpoints:
            verified = "✓" if cp.get("verified", True) else "⚠"
            verified_style = "green" if cp.get("verified", True) else "yellow"
            
            table.add_row(
                str(cp.get("iteration", "?")),
                cp.get("message", "?")[:40],
                cp.get("commit", "?")[:7],
                f"[{verified_style}]{verified}[/{verified_style}]",
                format_timestamp(cp.get("timestamp", "")),
            )
        
        console.print(table)
    
    if not landings and not checkpoints:
        console.print("\n[dim]No landings or checkpoints yet[/dim]")
    
    console.print()
