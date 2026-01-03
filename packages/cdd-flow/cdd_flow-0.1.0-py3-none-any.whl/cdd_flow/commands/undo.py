"""
cdd-flow undo command

Revert the last landing.
"""

import os
from pathlib import Path

import click
from rich.console import Console

from cdd_flow.core.recovery import get_recovery_info, perform_undo
from cdd_flow.core.session import get_session, save_session

console = Console()


@click.command()
@click.option("--force", is_flag=True, help="Proceed even if files were modified since landing")
@click.option("--restore", is_flag=True, help="Restore artifact to Downloads")
@click.pass_context
def undo(ctx, force, restore):
    """Revert the last landing.
    
    Restores the project to its state before the most recent landing.
    """
    project_dir = Path(ctx.obj.get("project") or os.getcwd()).resolve()
    
    # Get current session/state
    session = get_session(project_dir)
    if session is None:
        console.print("[red]✗ No active session or landings to undo[/red]")
        raise SystemExit(1)
    
    iteration = session.get("iteration", 0)
    if iteration == 0:
        console.print("[red]✗ No landings to undo[/red]")
        raise SystemExit(1)
    
    # Check recovery info exists
    recovery = get_recovery_info(project_dir, iteration)
    if recovery is None:
        console.print(f"[red]✗ No recovery data for iteration {iteration}[/red]")
        raise SystemExit(1)
    
    console.print(f"\n[dim]Undoing landing (iteration {iteration})...[/dim]")
    
    # Show what will be undone
    manifest = recovery.get("manifest", {})
    files = manifest.get("files", [])
    if files:
        console.print("[dim]Files affected:[/dim]")
        for f in files[:5]:
            action = f.get("action", "?")
            path = f.get("path", "?")
            console.print(f"  [dim]{path} ({action})[/dim]")
        if len(files) > 5:
            console.print(f"  [dim]... and {len(files) - 5} more[/dim]")
    
    # Perform undo
    success, message = perform_undo(project_dir, iteration, force=force)
    
    if not success:
        console.print(f"[red]✗ {message}[/red]")
        raise SystemExit(1)
    
    # Update session
    session["iteration"] = iteration - 1
    if session["landings"]:
        session["landings"].pop()
    save_session(project_dir, session)
    
    console.print(f"[green]✓ {message}[/green]")
    
    # Optionally restore artifact
    if restore and recovery.get("artifact"):
        landing_zone = Path("~/Downloads").expanduser()
        artifact = recovery["artifact"]
        restored_path = landing_zone / artifact.name
        
        import shutil
        shutil.copy2(str(artifact), str(restored_path))
        console.print(f"[green]✓ Restored {artifact.name} to Downloads[/green]")
    
    console.print()
