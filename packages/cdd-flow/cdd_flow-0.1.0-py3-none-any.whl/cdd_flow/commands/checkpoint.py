"""
cdd-flow checkpoint command

Commit verified state.
"""

import os
import subprocess
from pathlib import Path

import click
from rich.console import Console

from cdd_flow.core.recovery import clear_recovery
from cdd_flow.core.session import get_session, add_checkpoint, save_session

console = Console()


def run_verification(project_dir: Path) -> tuple[bool, list[dict]]:
    """
    Run verification steps.
    
    Returns (all_passed, results).
    """
    from cdd_flow.core.config import get_config
    
    config = get_config(project_dir)
    verify_config = config.get("verify", {})
    steps = verify_config.get("steps", [])
    
    # Auto-detect if no config
    if not steps:
        contracts_dir = project_dir / "contracts"
        if contracts_dir.exists():
            steps = [
                {"name": "lint", "command": "cdd lint contracts/", "required": True},
                {"name": "test", "command": "cdd test contracts/", "required": True},
            ]
        else:
            # Check for npm test
            package_json = project_dir / "package.json"
            if package_json.exists():
                import json
                try:
                    with open(package_json) as f:
                        pkg = json.load(f)
                    if pkg.get("scripts", {}).get("test"):
                        steps = [{"name": "npm test", "command": "npm test", "required": True}]
                except (json.JSONDecodeError, KeyError):
                    pass
            
            # Check for pytest
            if not steps:
                if (project_dir / "pytest.ini").exists() or (project_dir / "tests").exists():
                    steps = [{"name": "pytest", "command": "pytest", "required": True}]
    
    if not steps:
        return True, []  # No verification configured
    
    results = []
    all_passed = True
    
    for step in steps:
        name = step.get("name", "unnamed")
        command = step.get("command", "")
        required = step.get("required", True)
        
        console.print(f"  [dim]Running {name}...[/dim]", end="")
        
        result = subprocess.run(
            command,
            shell=True,
            cwd=project_dir,
            capture_output=True,
            text=True
        )
        
        passed = result.returncode == 0
        
        step_result = {
            "name": name,
            "passed": passed,
            "required": required,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
        results.append(step_result)
        
        if passed:
            console.print(" [green]✓[/green]")
        else:
            console.print(" [red]✗[/red]")
            if required:
                all_passed = False
    
    return all_passed, results


@click.command()
@click.argument("message", required=False)
@click.option("--no-verify", is_flag=True, help="Skip verification")
@click.option("--force", is_flag=True, help="Bypass failed verification")
@click.pass_context
def checkpoint(ctx, message, no_verify, force):
    """Commit verified state as a checkpoint.
    
    Creates a git commit after running verification. If verification
    fails, the checkpoint is blocked unless --force is used.
    
    If no message is provided, generates one from the session goal.
    
    Examples:
        cdd-flow checkpoint "basic structure working"
        cdd-flow checkpoint --no-verify
        cdd-flow checkpoint --force  # bypass failed verification
    """
    project_dir = Path(ctx.obj.get("project") or os.getcwd()).resolve()
    
    session = get_session(project_dir)
    
    # Generate message if not provided
    if not message:
        if session and session.get("goal") != "(implicit session)":
            iteration = session.get("iteration", 0)
            message = f"{session['goal']} - iteration {iteration}"
        else:
            message = "checkpoint"
    
    # Run verification
    verified = True
    if not no_verify and not force:
        console.print("\n[dim]Running verification...[/dim]")
        verified, results = run_verification(project_dir)
        
        if not verified:
            console.print("\n[red]✗ Verification failed[/red]")
            console.print("\nCheckpoint blocked. Options:")
            console.print("  • Fix issues and retry")
            console.print("  • Use --force to bypass (not recommended)")
            console.print("  • Use --no-verify to skip verification")
            raise SystemExit(1)
        
        if results:
            console.print("[green]✓ Verification passed[/green]")
    elif no_verify:
        console.print("[dim]⚠ Verification skipped[/dim]")
        verified = False
    elif force:
        console.print("[yellow]⚠ Verification bypassed with --force[/yellow]")
        verified = False
    
    # Stage all changes
    console.print("\n[dim]Staging changes...[/dim]")
    result = subprocess.run(
        ["git", "add", "-A"],
        cwd=project_dir,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        console.print(f"[red]✗ git add failed: {result.stderr}[/red]")
        raise SystemExit(1)
    
    # Check if anything to commit
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=project_dir,
        capture_output=True,
        text=True
    )
    
    if not result.stdout.strip():
        console.print("[yellow]⚠ Nothing to commit (working tree clean)[/yellow]")
        return
    
    # Commit
    console.print(f"[dim]Committing: {message}[/dim]")
    result = subprocess.run(
        ["git", "commit", "-m", message],
        cwd=project_dir,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        console.print(f"[red]✗ git commit failed: {result.stderr}[/red]")
        raise SystemExit(1)
    
    # Get commit SHA
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=project_dir,
        capture_output=True,
        text=True
    )
    commit_sha = result.stdout.strip()[:7]
    
    # Record in session
    if session:
        add_checkpoint(project_dir, commit_sha, message, verified=verified)
    
    # Clear recovery (checkpoint is now authoritative)
    clear_recovery(project_dir)
    
    console.print(f"[green]✓ Committed: {message} ({commit_sha})[/green]\n")
