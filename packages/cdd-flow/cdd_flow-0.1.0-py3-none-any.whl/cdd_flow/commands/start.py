"""
cdd-flow start command

Begin a new tracked session.
"""

import os
from pathlib import Path

import click
from rich.console import Console

from cdd_flow.core.session import get_session, start_session, is_implicit_session

console = Console()


@click.command()
@click.argument("goal", required=False)
@click.pass_context
def start(ctx, goal):
    """Start a new tracked session.
    
    A session tracks a focused unit of work with AI. It captures a baseline
    so you can safely abandon and revert if needed.
    
    Example:
        cdd-flow start "implement PDF export"
    """
    project_dir = Path(ctx.obj.get("project") or os.getcwd()).resolve()
    
    # Check for goal
    if not goal:
        console.print("[red]✗ Goal is required[/red]")
        console.print("\nUsage: cdd-flow start \"your goal description\"")
        raise SystemExit(1)
    
    # Check for existing session
    existing = get_session(project_dir)
    if existing is not None and not is_implicit_session(existing):
        console.print(f"[red]✗ Session already active: {existing.get('goal')}[/red]")
        console.print("\nComplete or abandon the current session first:")
        console.print("  cdd-flow complete")
        console.print("  cdd-flow abandon")
        raise SystemExit(1)
    
    console.print(f"\n[dim]Starting session...[/dim]")
    
    session, error = start_session(project_dir, goal)
    
    if error:
        console.print(f"[red]✗ {error}[/red]")
        raise SystemExit(1)
    
    console.print(f"[green]✓ Session started: {goal}[/green]")
    
    baseline = session.get("baseline", {})
    if baseline.get("had_dirty_tree"):
        console.print("[dim]  (uncommitted changes stashed for recovery)[/dim]")
    
    console.print("\n[dim]Next steps:[/dim]")
    console.print("  cdd-flow ctx        # Generate context for AI")
    console.print("  cdd-flow land       # Land an artifact")
    console.print("  cdd-flow checkpoint # Commit verified state")
    console.print()
