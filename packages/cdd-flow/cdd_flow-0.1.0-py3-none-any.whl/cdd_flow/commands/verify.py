"""
cdd-flow verify command

Run verification gates.
"""

import os
import subprocess
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from cdd_flow.core.config import get_config

console = Console()


def run_verification_step(step: dict, project_dir: Path) -> dict:
    """Run a single verification step."""
    name = step.get("name", "unnamed")
    command = step.get("command", "")
    required = step.get("required", True)
    
    result = subprocess.run(
        command,
        shell=True,
        cwd=project_dir,
        capture_output=True,
        text=True
    )
    
    return {
        "name": name,
        "command": command,
        "passed": result.returncode == 0,
        "required": required,
        "exit_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def auto_detect_steps(project_dir: Path) -> list[dict]:
    """Auto-detect verification steps based on project structure."""
    steps = []
    
    # Check for CDD contracts
    contracts_dir = project_dir / "contracts"
    if contracts_dir.exists():
        steps.extend([
            {"name": "lint", "command": "cdd lint contracts/", "required": True},
            {"name": "test", "command": "cdd test contracts/", "required": True},
        ])
        return steps
    
    # Check for npm test
    package_json = project_dir / "package.json"
    if package_json.exists():
        import json
        try:
            with open(package_json) as f:
                pkg = json.load(f)
            test_script = pkg.get("scripts", {}).get("test", "")
            if test_script and test_script != 'echo "Error: no test specified" && exit 1':
                steps.append({"name": "npm test", "command": "npm test", "required": True})
        except (json.JSONDecodeError, KeyError):
            pass
    
    # Check for pytest
    if (project_dir / "pytest.ini").exists() or (project_dir / "tests").exists():
        steps.append({"name": "pytest", "command": "pytest", "required": True})
    
    # Check for pyproject.toml with pytest config
    pyproject = project_dir / "pyproject.toml"
    if pyproject.exists() and not any(s["name"] == "pytest" for s in steps):
        content = pyproject.read_text()
        if "[tool.pytest" in content:
            steps.append({"name": "pytest", "command": "pytest", "required": True})
    
    return steps


@click.command()
@click.option("--verbose", "-v", is_flag=True, help="Show command output")
@click.pass_context
def verify(ctx, verbose):
    """Run verification gates.
    
    Runs configured verification steps and reports results.
    Uses auto-detection if no verification config exists.
    
    Exit codes:
        0 - All required steps passed
        1 - At least one required step failed
    """
    project_dir = Path(ctx.obj.get("project") or os.getcwd()).resolve()
    
    config = get_config(project_dir)
    verify_config = config.get("verify", {})
    steps = verify_config.get("steps", [])
    
    # Auto-detect if not configured
    auto_detected = False
    if not steps:
        steps = auto_detect_steps(project_dir)
        auto_detected = True
    
    if not steps:
        console.print("\n[yellow]⚠ No verification steps configured or detected[/yellow]")
        console.print("\nTo configure, create .cdd-flow/config.yaml:")
        console.print("""
  verify:
    steps:
      - name: lint
        command: cdd lint contracts/
        required: true
      - name: test
        command: cdd test contracts/
        required: true
""")
        return
    
    console.print()
    if auto_detected:
        console.print("[dim]Using auto-detected verification:[/dim]")
    else:
        console.print("[dim]Running verification steps:[/dim]")
    
    results = []
    for step in steps:
        console.print(f"  • {step['name']}...", end=" ")
        result = run_verification_step(step, project_dir)
        results.append(result)
        
        if result["passed"]:
            console.print("[green]✓ passed[/green]")
        else:
            status = "[red]✗ failed[/red]"
            if not result["required"]:
                status = "[yellow]⚠ failed (optional)[/yellow]"
            console.print(status)
        
        if verbose and (result["stdout"] or result["stderr"]):
            if result["stdout"]:
                console.print(f"[dim]{result['stdout'][:500]}[/dim]")
            if result["stderr"]:
                console.print(f"[red]{result['stderr'][:500]}[/red]")
    
    # Summary
    console.print()
    passed = sum(1 for r in results if r["passed"])
    failed_required = [r for r in results if not r["passed"] and r["required"]]
    failed_optional = [r for r in results if not r["passed"] and not r["required"]]
    
    if not failed_required:
        console.print(f"[green]✓ Verification passed ({passed}/{len(results)} steps)[/green]")
        if failed_optional:
            console.print(f"[dim]  ({len(failed_optional)} optional steps failed)[/dim]")
    else:
        console.print(f"[red]✗ Verification failed[/red]")
        for r in failed_required:
            console.print(f"  • {r['name']}: {r['command']}")
            if r["stderr"]:
                # Show first line of error
                first_line = r["stderr"].strip().split("\n")[0][:80]
                console.print(f"    [dim]{first_line}[/dim]")
        raise SystemExit(1)
    
    console.print()
