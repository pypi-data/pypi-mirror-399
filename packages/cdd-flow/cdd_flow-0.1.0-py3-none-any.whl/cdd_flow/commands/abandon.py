"""
cdd-flow abandon command

Abort session and revert to baseline.
"""

import os
import sys
from pathlib import Path

import click
from rich.console import Console

from cdd_flow.core.session import get_session, abandon_session, is_implicit_session

console = Console()


@click.command()
@click.option("--force", is_flag=True, help="Proceed without confirmation")
@click.pass_context
def abandon(ctx, force):
    """Abandon the current session and revert to baseline.
    
    This reverts all changes made since the session started, restoring
    the project to its pre-session state (including any uncommitted 
    changes that were stashed).
    
    Use --force to skip confirmation prompt.
    """
    project_dir = Path(ctx.obj.get("project") or os.getcwd()).resolve()
    
    existing = get_session(project_dir)
    if existing is None:
        console.print("[red]✗ No active session[/red]")
        raise SystemExit(3)
    
    if is_implicit_session(existing):
        console.print("[red]✗ Cannot abandon implicit session (no baseline)[/red]")
        console.print("\nImplicit sessions are created by 'land' without 'start'.")
        console.print("Use 'undo' to revert the last landing instead.")
        raise SystemExit(1)
    
    # Confirmation prompt (unless --force or non-interactive)
    if not force:
        is_interactive = sys.stdin.isatty()
        
        if is_interactive:
            console.print(f"\n[yellow]⚠ About to abandon session: {existing['goal']}[/yellow]")
            console.print("[dim]This will revert all changes since session start.[/dim]\n")
            
            if not click.confirm("Proceed?"):
                console.print("[dim]Cancelled.[/dim]")
                raise SystemExit(4)
        else:
            # Non-interactive mode requires --force
            console.print("[red]✗ Non-interactive mode requires --force[/red]")
            raise SystemExit(1)
    
    console.print(f"\n[dim]Abandoning session...[/dim]")
    
    session, warning = abandon_session(project_dir, force=force)
    
    if session is None:
        console.print(f"[red]✗ {warning}[/red]")
        raise SystemExit(1)
    
    console.print(f"[green]✓ Session abandoned, reverted to baseline[/green]")
    
    if warning:
        console.print(f"\n[yellow]⚠ {warning}[/yellow]")
    
    console.print()
