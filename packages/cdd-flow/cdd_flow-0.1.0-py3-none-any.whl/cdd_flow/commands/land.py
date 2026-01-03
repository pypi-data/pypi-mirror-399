"""
cdd-flow land command

Detect, integrate, and clean artifacts from the landing zone.
"""

import os
import re
import shutil
import tarfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import NamedTuple

import click
from rich.console import Console
from rich.panel import Panel

from cdd_flow.core.config import get_config
from cdd_flow.core.recovery import prepare_recovery
from cdd_flow.core.session import get_session, update_session_landing

console = Console()


class ArtifactCandidate(NamedTuple):
    """A detected artifact candidate."""
    path: Path
    mtime: datetime
    is_duplicate: bool  # Has (1), (2) etc suffix
    base_name: str  # Name without duplicate suffix


class DetectionResult(NamedTuple):
    """Result of artifact detection."""
    candidate: ArtifactCandidate | None
    confidence: str  # high, medium, low, none
    stale_files: list[Path]
    warnings: list[str]


# Artifact extensions we recognise (defaults, can be overridden by config)
DEFAULT_ARTIFACT_EXTENSIONS = {
    ".tar", ".tar.gz", ".tgz",
    ".py", ".yaml", ".yml", ".json",
    ".md", ".html", ".htm",
    ".jsx", ".tsx", ".ts", ".js",
    ".css", ".scss",
}

# Partial download extensions to exclude
PARTIAL_EXTENSIONS = {".crdownload", ".part", ".download", ".tmp"}


def parse_duplicate_suffix(filename: str) -> tuple[str, bool]:
    """
    Parse Mac-style duplicate suffix from filename.
    
    'artifact (1).tar' -> ('artifact.tar', True)
    'artifact.tar' -> ('artifact.tar', False)
    """
    # Match pattern: name (N).ext or name (N).tar.gz
    match = re.match(r"^(.+?) \((\d+)\)(\.tar\.gz|\.tgz|\.[^.]+)$", filename)
    if match:
        base = match.group(1) + match.group(3)
        return base, True
    return filename, False


def is_file_stable(path: Path, wait_seconds: float = 2.0) -> bool:
    """Check if file size is stable (not still downloading)."""
    import time
    try:
        size1 = path.stat().st_size
        time.sleep(wait_seconds)
        size2 = path.stat().st_size
        return size1 == size2
    except OSError:
        return False


def detect_artifacts(
    landing_zone: Path,
    max_age_minutes: int = 15,
    artifact_extensions: set[str] | None = None
) -> DetectionResult:
    """
    Scan landing zone for artifact candidates.
    
    Returns the best candidate with confidence assessment.
    """
    if artifact_extensions is None:
        artifact_extensions = DEFAULT_ARTIFACT_EXTENSIONS
    
    if not landing_zone.exists():
        return DetectionResult(
            candidate=None,
            confidence="none",
            stale_files=[],
            warnings=[f"Landing zone does not exist: {landing_zone}"]
        )
    
    now = datetime.now()
    cutoff = now - timedelta(minutes=max_age_minutes)
    
    candidates: list[ArtifactCandidate] = []
    old_files: list[ArtifactCandidate] = []  # Old but valid artifacts
    warnings: list[str] = []
    
    for item in landing_zone.iterdir():
        if item.is_dir():
            continue
        
        # Skip hidden files
        if item.name.startswith("."):
            continue
        
        # Skip partial downloads
        name_lower = item.name.lower()
        if any(name_lower.endswith(ext) for ext in PARTIAL_EXTENSIONS):
            continue
        
        # Check extension - handle .tar.gz properly
        is_artifact = any(name_lower.endswith(ext) for ext in artifact_extensions)
        if not is_artifact:
            continue
        
        # Get modification time
        mtime = datetime.fromtimestamp(item.stat().st_mtime)
        base_name, is_duplicate = parse_duplicate_suffix(item.name)
        
        candidate = ArtifactCandidate(
            path=item,
            mtime=mtime,
            is_duplicate=is_duplicate,
            base_name=base_name
        )
        
        if mtime >= cutoff:
            candidates.append(candidate)
        else:
            old_files.append(candidate)
    
    if not candidates:
        return DetectionResult(
            candidate=None,
            confidence="none",
            stale_files=[],  # Don't auto-clean old files if nothing to land
            warnings=["No recent artifacts found"]
        )
    
    # Sort by mtime descending (newest first)
    candidates.sort(key=lambda c: c.mtime, reverse=True)
    best = candidates[0]
    
    # Stale files = duplicates of the SAME base name (the Mac (1) problem)
    stale_files: list[Path] = []
    
    # Mark other versions of same base as stale
    for c in candidates[1:]:
        if c.base_name == best.base_name:
            stale_files.append(c.path)
    
    # Also check old files for same base name
    for c in old_files:
        if c.base_name == best.base_name:
            stale_files.append(c.path)
    
    # Assess confidence
    if len(candidates) == 1 and not best.is_duplicate:
        confidence = "high"
    elif best.is_duplicate or stale_files:
        confidence = "medium"
        warnings.append("Duplicate suffix detected (Mac download collision)")
    elif len(candidates) > 1:
        confidence = "medium"
        warnings.append(f"Multiple recent artifacts found ({len(candidates)})")
    else:
        confidence = "high"
    
    return DetectionResult(
        candidate=best,
        confidence=confidence,
        stale_files=stale_files,
        warnings=warnings
    )


def extract_tar_safe(
    tar_path: Path,
    dest: Path,
    allow_symlinks: bool = False,
    allow_hardlinks: bool = False
) -> list[dict]:
    """
    Safely extract tar archive with security checks.
    
    Returns list of extracted files with action (created/modified).
    
    Rejects:
    - Absolute paths
    - Path traversal (..)
    - Paths resolving outside project
    - Symlinks (unless allow_symlinks)
    - Hardlinks (unless allow_hardlinks)
    - Protected paths (.git/, .cdd-flow/)
    """
    extracted = []
    rejected = []
    
    with tarfile.open(tar_path, "r:*") as tar:
        for member in tar.getmembers():
            # Check for absolute paths
            if member.name.startswith("/"):
                rejected.append((member.name, "absolute path"))
                continue
            
            # Check for path traversal
            if ".." in member.name.split("/"):
                rejected.append((member.name, "path traversal"))
                continue
            
            # Resolve and verify stays in project
            resolved = (dest / member.name).resolve()
            try:
                resolved.relative_to(dest.resolve())
            except ValueError:
                rejected.append((member.name, "escapes project root"))
                continue
            
            # Check for symlinks
            if member.issym():
                if not allow_symlinks:
                    rejected.append((member.name, "symlink not allowed"))
                    continue
            
            # Check for hardlinks
            if member.islnk():
                if not allow_hardlinks:
                    rejected.append((member.name, "hardlink not allowed"))
                    continue
            
            # Protect internal directories
            if member.name.startswith(".git/") or member.name.startswith(".cdd-flow/"):
                rejected.append((member.name, "protected path"))
                continue
            
            # Track whether file existed before
            existed_before = resolved.exists()
            
            # Extract this member
            tar.extract(member, path=dest)
            
            if member.isfile():
                extracted.append({
                    "path": member.name,
                    "action": "modified" if existed_before else "created"
                })
    
    # If any rejected, abort with clear error
    if rejected:
        # Clean up what we extracted
        for file_info in extracted:
            try:
                (dest / file_info["path"]).unlink()
            except OSError:
                pass
        
        error_msg = "Unsafe archive contents:\n"
        for name, reason in rejected:
            error_msg += f"  - {name}: {reason}\n"
        raise click.ClickException(error_msg)
    
    return extracted


def move_to_trash(path: Path, trash_dir: Path) -> Path:
    """Move file to trash with timestamp prefix."""
    trash_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    trash_name = f"{timestamp}-{path.name}"
    trash_path = trash_dir / trash_name
    shutil.move(str(path), str(trash_path))
    return trash_path


@click.command()
@click.option("--verify", is_flag=True, help="Run verification after landing")
@click.option("--checkpoint", "checkpoint_msg", metavar="MSG", help="Land + verify + checkpoint")
@click.option("--clip", is_flag=True, help="Copy changes summary to clipboard")
@click.option("--dest", type=click.Path(), help="Destination for single-file landing")
@click.option("--max-age", default=15, help="Max artifact age in minutes (default: 15)")
@click.option("--no-clean", is_flag=True, help="Don't clean artifact from Downloads")
@click.option("--allow-symlinks", is_flag=True, help="Allow symlinks in tar")
@click.option("--allow-hardlinks", is_flag=True, help="Allow hardlinks in tar")
@click.option("--dry-run", is_flag=True, help="Show what would happen")
@click.pass_context
def land(ctx, verify, checkpoint_msg, clip, dest, max_age, no_clean, allow_symlinks, allow_hardlinks, dry_run):
    """Land an artifact from the Downloads folder.
    
    Detects the most recent artifact, integrates it into the project,
    and cleans up the Downloads folder.
    """
    from cdd_flow.core.recovery import save_landed_manifest
    
    config = get_config(ctx.obj.get("project"))
    project_dir = Path(ctx.obj.get("project") or os.getcwd()).resolve()
    landing_zone = Path(config.get("landing_zone", "~/Downloads")).expanduser()
    trash_dir = Path(config.get("trash_dir", "~/.cdd-flow/trash")).expanduser()
    
    # Get artifact extensions from config
    artifact_extensions = set(config.get("artifact_extensions", DEFAULT_ARTIFACT_EXTENSIONS))
    
    # Step 1: Detect
    console.print("\n[dim]Scanning for artifacts...[/dim]")
    result = detect_artifacts(landing_zone, max_age, artifact_extensions)
    
    if result.confidence == "none":
        console.print(Panel(
            "[red]No recent artifacts found[/red]\n\n"
            "• Did you download the file from Claude?\n"
            f"• Files older than {max_age} minutes are ignored\n"
            "• Use --max-age to override",
            title="✗ Detection Failed",
            border_style="red"
        ))
        raise SystemExit(2)
    
    candidate = result.candidate
    
    # Show warnings
    for warning in result.warnings:
        console.print(f"[yellow]⚠ {warning}[/yellow]")
    
    # Show what we found
    age_mins = (datetime.now() - candidate.mtime).total_seconds() / 60
    console.print(f"\n[green]✓ Found:[/green] {candidate.path.name} ({age_mins:.0f} min ago)")
    
    if result.stale_files:
        console.print(f"[dim]  Will clean {len(result.stale_files)} stale file(s)[/dim]")
    
    if dry_run:
        console.print("\n[yellow]--dry-run: No changes made[/yellow]")
        return
    
    # Step 2: Prepare recovery
    session = get_session(project_dir)
    iteration = (session.get("iteration", 0) if session else 0) + 1
    recovery_dir = project_dir / ".cdd-flow" / "recovery" / str(iteration)
    
    prepare_recovery(project_dir, recovery_dir, candidate.path)
    
    # Step 3: Integrate
    if candidate.path.suffix in {".tar", ".gz", ".tgz"} or candidate.path.name.endswith(".tar.gz"):
        # Extract tar with safe extraction
        console.print(f"[dim]Extracting to {project_dir}...[/dim]")
        landed_files = extract_tar_safe(
            candidate.path,
            project_dir,
            allow_symlinks=allow_symlinks,
            allow_hardlinks=allow_hardlinks
        )
        console.print(f"[green]✓ Extracted {len(landed_files)} file(s)[/green]")
        for f in landed_files[:5]:
            console.print(f"  [dim]{f['path']} ({f['action']})[/dim]")
        if len(landed_files) > 5:
            console.print(f"  [dim]... and {len(landed_files) - 5} more[/dim]")
    else:
        # Single file
        if dest:
            dest_path = project_dir / dest
        else:
            # Convention-based routing
            dest_path = project_dir / candidate.path.name
            console.print(f"[dim]Landing to: {dest_path}[/dim]")
        
        existed_before = dest_path.exists()
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(candidate.path), str(dest_path))
        console.print(f"[green]✓ Copied to {dest_path.relative_to(project_dir)}[/green]")
        landed_files = [{
            "path": str(dest_path.relative_to(project_dir)),
            "action": "modified" if existed_before else "created"
        }]
    
    # Save manifest for recovery
    save_landed_manifest(recovery_dir, landed_files)
    
    # Step 4: Clean
    if not no_clean:
        move_to_trash(candidate.path, trash_dir)
        console.print(f"[green]✓ Moved to trash[/green]")
        
        for stale in result.stale_files:
            move_to_trash(stale, trash_dir)
        if result.stale_files:
            console.print(f"[green]✓ Cleaned {len(result.stale_files)} stale file(s)[/green]")
    else:
        console.print("[dim]⚠ --no-clean: artifact left in Downloads[/dim]")
    
    # Step 5: Report
    console.print("\n[dim]Checking changes...[/dim]")
    # TODO: Integrate with cdd-context for proper change detection
    # For now, just report what we landed
    
    # Step 6: Update session
    update_session_landing(project_dir, {
        "iteration": iteration,
        "artifact": candidate.path.name,
        "files": landed_files,
        "timestamp": datetime.now().isoformat(),
    })
    
    # Verification
    if verify or checkpoint_msg:
        console.print("\n[dim]Running verification...[/dim]")
        # TODO: Run cdd-flow verify
        console.print("[yellow]⚠ Verification not yet implemented[/yellow]")
    
    # Checkpoint
    if checkpoint_msg:
        console.print(f"\n[dim]Creating checkpoint: {checkpoint_msg}[/dim]")
        # TODO: Run cdd-flow checkpoint
        console.print("[yellow]⚠ Checkpoint not yet implemented[/yellow]")
    
    console.print("\n[green]✓ Landing complete[/green]\n")
