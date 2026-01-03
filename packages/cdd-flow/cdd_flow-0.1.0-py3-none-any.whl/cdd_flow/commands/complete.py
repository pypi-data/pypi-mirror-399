"""
cdd-flow complete command

End a session successfully.
"""

import os
from datetime import datetime
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel

from cdd_flow.core.session import get_session, complete_session

console = Console()


def format_duration(seconds: int) -> str:
    """Format seconds to human readable duration."""
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    return f"{secs}s"


@click.command()
@click.pass_context
def complete(ctx):
    """End the current session successfully.
    
    Marks the session as completed and archives it. The recovery directory
    is cleared since the session work is now committed.
    """
    project_dir = Path(ctx.obj.get("project") or os.getcwd()).resolve()
    
    existing = get_session(project_dir)
    if existing is None:
        console.print("[red]✗ No active session[/red]")
        console.print("\nStart one with: cdd-flow start \"your goal\"")
        raise SystemExit(3)
    
    console.print(f"\n[dim]Completing session...[/dim]")
    
    session, error = complete_session(project_dir)
    
    if error:
        console.print(f"[red]✗ {error}[/red]")
        raise SystemExit(1)
    
    # Show summary
    summary = session.get("summary", {})
    duration = format_duration(summary.get("duration_seconds", 0))
    
    summary_text = (
        f"[bold]Goal:[/bold] {session['goal']}\n"
        f"[bold]Iterations:[/bold] {summary.get('iterations', 0)}\n"
        f"[bold]Checkpoints:[/bold] {summary.get('checkpoints', 0)}\n"
        f"[bold]Duration:[/bold] {duration}"
    )
    
    console.print(Panel(
        summary_text,
        title="[green]✓ Session Completed[/green]",
        border_style="green"
    ))
    console.print()
