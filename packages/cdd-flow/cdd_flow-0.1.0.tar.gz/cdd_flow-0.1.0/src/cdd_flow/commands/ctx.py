"""
cdd-flow ctx command

Generate and copy context to clipboard.
"""

import os
import subprocess
from pathlib import Path

import click
from rich.console import Console

from cdd_flow.core.session import get_session

console = Console()


def copy_to_clipboard(text: str) -> bool:
    """Copy text to clipboard using pbcopy (macOS)."""
    try:
        process = subprocess.Popen(
            ["pbcopy"],
            stdin=subprocess.PIPE
        )
        process.communicate(text.encode("utf-8"))
        return process.returncode == 0
    except FileNotFoundError:
        return False


def run_cdd_context(project_dir: Path, mode: str) -> tuple[bool, str]:
    """
    Run cdd-context and return (success, output).
    
    mode: 'full', 'changes', 'changes=list', 'changes=summaries'
    """
    cmd = ["cdd-context", "build"]
    
    if mode == "changes":
        cmd.append("--changes")
    elif mode == "changes=list":
        cmd.append("--changes=list")
    elif mode == "changes=summaries":
        cmd.append("--changes=summaries")
    # 'full' is default (no extra args)
    
    try:
        result = subprocess.run(
            cmd,
            cwd=project_dir,
            capture_output=True,
            text=True
        )
        
        # cdd-context writes to PROJECT_CONTEXT.md
        context_file = project_dir / "PROJECT_CONTEXT.md"
        if context_file.exists():
            return True, context_file.read_text()
        
        return False, result.stderr or "No output generated"
        
    except FileNotFoundError:
        return False, "cdd-context not found. Install with: pip install cdd-context"


@click.command()
@click.option("--full", "mode", flag_value="full", help="Full project context")
@click.option("--changes", "mode", flag_value="changes", help="Changes since last build")
@click.option("--changes-list", "mode", flag_value="changes=list", help="List changed files only")
@click.option("--changes-summaries", "mode", flag_value="changes=summaries", help="Summaries only")
@click.option("--no-clip", is_flag=True, help="Don't copy to clipboard")
@click.pass_context
def ctx(ctx, mode, no_clip):
    """Generate context and copy to clipboard.
    
    Uses cdd-context to generate project context suitable for AI sessions.
    
    By default, generates changes if mid-session (iterations > 0),
    otherwise full context for new sessions.
    """
    project_dir = Path(ctx.obj.get("project") or os.getcwd()).resolve()
    
    # Determine mode based on session state if not explicitly set
    if mode is None:
        session = get_session(project_dir)
        if session and session.get("iteration", 0) > 0:
            mode = "changes"
        else:
            mode = "full"
    
    mode_display = {
        "full": "full context",
        "changes": "changes",
        "changes=list": "changes (list)",
        "changes=summaries": "changes (summaries)",
    }
    
    console.print(f"\n[dim]Generating {mode_display.get(mode, mode)}...[/dim]")
    
    success, output = run_cdd_context(project_dir, mode)
    
    if not success:
        console.print(f"[red]✗ {output}[/red]")
        raise SystemExit(1)
    
    # Copy to clipboard
    if not no_clip:
        if copy_to_clipboard(output):
            size_kb = len(output.encode("utf-8")) / 1024
            console.print(f"[green]✓ Copied to clipboard ({size_kb:.1f}kb)[/green]")
        else:
            console.print("[yellow]⚠ Could not copy to clipboard[/yellow]")
            console.print(f"[dim]Output saved to PROJECT_CONTEXT.md[/dim]")
    else:
        console.print(f"[green]✓ Generated PROJECT_CONTEXT.md[/green]")
    
    console.print()
