"""
Session management for cdd-flow.

Sessions track a focused unit of work with AI.
"""

import subprocess
from datetime import datetime
from pathlib import Path

import yaml


def get_session_path(project_dir: Path) -> Path:
    """Get the session file path for a project."""
    return project_dir / ".cdd-flow" / "session.yaml"


def get_session(project_dir: Path) -> dict | None:
    """Load current session for a project, if any."""
    session_path = get_session_path(project_dir)
    if session_path.exists():
        with open(session_path) as f:
            data = yaml.safe_load(f)
            if data and data.get("session", {}).get("status") == "active":
                return data.get("session")
    return None


def save_session(project_dir: Path, session: dict) -> None:
    """Save session to disk."""
    session_path = get_session_path(project_dir)
    session_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(session_path, "w") as f:
        yaml.dump({"version": "1", "session": session}, f, default_flow_style=False)


def is_implicit_session(session: dict | None) -> bool:
    """Check if session is implicit (created by land without explicit start)."""
    if session is None:
        return True
    return session.get("goal") == "(implicit session)"


def capture_baseline(project_dir: Path) -> dict:
    """
    Capture baseline state for session recovery.
    
    If working tree is dirty, stash changes and record stash ref.
    Returns baseline info dict.
    """
    baseline = {
        "commit": None,
        "had_dirty_tree": False,
        "stash_ref": None,
    }
    
    # Get HEAD commit
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=project_dir,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            baseline["commit"] = result.stdout.strip()
    except FileNotFoundError:
        return baseline
    
    # Check if dirty
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=project_dir,
        capture_output=True,
        text=True
    )
    
    if result.stdout.strip():
        baseline["had_dirty_tree"] = True
        
        # Stash changes
        session_id = datetime.now().strftime("%Y%m%d-%H%M%S")
        stash_msg = f"cdd-flow-baseline-{session_id}"
        
        result = subprocess.run(
            ["git", "stash", "push", "-m", stash_msg],
            cwd=project_dir,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            # Get the stash ref
            result = subprocess.run(
                ["git", "rev-parse", "stash@{0}"],
                cwd=project_dir,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                baseline["stash_ref"] = result.stdout.strip()
    
    return baseline


def start_session(project_dir: Path, goal: str) -> tuple[dict | None, str | None]:
    """
    Start a new explicit session.
    
    Returns (session, error_message).
    """
    # Check no active session exists
    existing = get_session(project_dir)
    if existing is not None and not is_implicit_session(existing):
        return None, f"Session already active: {existing.get('goal')}"
    
    now = datetime.now()
    session_id = now.strftime("%Y-%m-%dT%H-%M-%S") + "-" + goal.lower().replace(" ", "-")[:20]
    
    # Capture baseline for abandon recovery
    baseline = capture_baseline(project_dir)
    
    session = {
        "id": session_id,
        "goal": goal,
        "started": now.isoformat(),
        "status": "active",
        "baseline": baseline,
        "iteration": 0,
        "landings": [],
        "checkpoints": [],
    }
    
    save_session(project_dir, session)
    return session, None


def update_session_landing(project_dir: Path, landing: dict) -> None:
    """Record a landing in the session."""
    session = get_session(project_dir)
    
    if session is None:
        # No active session, create implicit state tracking
        now = datetime.now()
        session = {
            "id": now.strftime("%Y-%m-%dT%H-%M-%S") + "-implicit",
            "goal": "(implicit session)",
            "started": now.isoformat(),
            "status": "active",
            "iteration": 0,
            "landings": [],
            "checkpoints": [],
        }
    
    session["iteration"] = landing["iteration"]
    session["landings"].append(landing)
    
    save_session(project_dir, session)


def add_checkpoint(project_dir: Path, commit_sha: str, message: str, verified: bool = True) -> None:
    """Record a checkpoint in the session."""
    session = get_session(project_dir)
    if session is None:
        return
    
    checkpoint = {
        "iteration": session["iteration"],
        "commit": commit_sha,
        "message": message,
        "timestamp": datetime.now().isoformat(),
        "verified": verified,
    }
    
    session["checkpoints"].append(checkpoint)
    save_session(project_dir, session)


def archive_session(project_dir: Path, session: dict) -> Path:
    """Archive a completed/abandoned session."""
    sessions_dir = project_dir / ".cdd-flow" / "sessions"
    sessions_dir.mkdir(parents=True, exist_ok=True)
    
    archive_path = sessions_dir / f"{session['id']}.yaml"
    with open(archive_path, "w") as f:
        yaml.dump({"version": "1", "session": session}, f, default_flow_style=False)
    
    # Remove active session file
    session_path = get_session_path(project_dir)
    if session_path.exists():
        session_path.unlink()
    
    return archive_path


def complete_session(project_dir: Path) -> tuple[dict | None, str | None]:
    """
    Mark session as completed and archive.
    
    Returns (session, error_message).
    """
    session = get_session(project_dir)
    if session is None:
        return None, "No active session"
    
    session["status"] = "completed"
    session["completed"] = datetime.now().isoformat()
    
    # Calculate summary
    started = datetime.fromisoformat(session["started"])
    ended = datetime.now()
    duration = ended - started
    
    session["summary"] = {
        "iterations": session.get("iteration", 0),
        "checkpoints": len(session.get("checkpoints", [])),
        "duration_seconds": int(duration.total_seconds()),
    }
    
    archive_session(project_dir, session)
    
    # Clear recovery directory
    from cdd_flow.core.recovery import clear_recovery
    clear_recovery(project_dir)
    
    return session, None


def abandon_session(project_dir: Path, force: bool = False) -> tuple[dict | None, str | None]:
    """
    Abandon session and revert to baseline.
    
    Returns (session, error_message).
    """
    session = get_session(project_dir)
    if session is None:
        return None, "No active session"
    
    # Check if this is an implicit session (can't abandon, no baseline)
    if is_implicit_session(session):
        return None, "Cannot abandon implicit session (no baseline). Use 'undo' instead."
    
    baseline = session.get("baseline", {})
    if not baseline.get("commit"):
        return None, "Session has no baseline commit recorded"
    
    # Check for uncommitted changes
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=project_dir,
        capture_output=True,
        text=True
    )
    
    if result.stdout.strip() and not force:
        return None, "Uncommitted changes exist. Use --force to proceed or commit/stash first."
    
    # Revert to baseline
    result = subprocess.run(
        ["git", "reset", "--hard", baseline["commit"]],
        cwd=project_dir,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        return None, f"git reset failed: {result.stderr}"
    
    # Restore stashed changes if any
    stash_warning = None
    if baseline.get("stash_ref"):
        result = subprocess.run(
            ["git", "stash", "apply", baseline["stash_ref"]],
            cwd=project_dir,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            # Drop the stash on success
            subprocess.run(
                ["git", "stash", "drop", baseline["stash_ref"]],
                cwd=project_dir,
                capture_output=True
            )
        else:
            stash_warning = (
                "Stash could not be applied automatically.\n"
                "Your pre-session changes are preserved in the stash.\n"
                "  To see: git stash show -p\n"
                "  To apply: git stash apply\n"
                "  To discard: git stash drop"
            )
    
    # Clear recovery directory
    from cdd_flow.core.recovery import clear_recovery
    clear_recovery(project_dir)
    
    # Mark and archive
    session["status"] = "abandoned"
    session["abandoned"] = datetime.now().isoformat()
    if stash_warning:
        session["stash_warning"] = stash_warning
    
    archive_session(project_dir, session)
    
    return session, stash_warning


def get_session_history(project_dir: Path) -> list[dict]:
    """Get history of archived sessions."""
    sessions_dir = project_dir / ".cdd-flow" / "sessions"
    if not sessions_dir.exists():
        return []
    
    history = []
    for f in sorted(sessions_dir.iterdir(), reverse=True):
        if f.suffix == ".yaml":
            with open(f) as fh:
                data = yaml.safe_load(fh)
                if data and data.get("session"):
                    history.append(data["session"])
    
    return history
