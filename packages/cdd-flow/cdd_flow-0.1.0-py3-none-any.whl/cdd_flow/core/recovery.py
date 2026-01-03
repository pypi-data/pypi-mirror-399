"""
Recovery mechanisms for cdd-flow.

Handles preparing recovery state and performing undo/rollback operations.
"""

import shutil
import subprocess
from datetime import datetime
from pathlib import Path

import yaml


def prepare_recovery(
    project_dir: Path,
    recovery_dir: Path,
    artifact_path: Path,
    landed_files: list[dict] | None = None
) -> None:
    """
    Prepare full recovery state before landing.
    
    Creates:
    - metadata.yaml (baseline commit, timestamp)
    - before.patch (uncommitted changes, binary)
    - staged.patch (staged changes, binary)
    - status_before.txt (git status snapshot)
    - artifact copy
    """
    recovery_dir.mkdir(parents=True, exist_ok=True)
    
    # Collect metadata
    metadata = {
        "timestamp": datetime.now().isoformat(),
        "artifact_name": artifact_path.name,
        "baseline": {}
    }
    
    # Record baseline commit
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=project_dir,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            metadata["baseline"]["commit"] = result.stdout.strip()
    except FileNotFoundError:
        pass  # git not available
    
    # Save metadata
    with open(recovery_dir / "metadata.yaml", "w") as f:
        yaml.dump(metadata, f, default_flow_style=False)
    
    # Capture unstaged changes (working tree vs index, binary-safe)
    try:
        result = subprocess.run(
            ["git", "diff", "--binary"],
            cwd=project_dir,
            capture_output=True
        )
        if result.returncode == 0 and result.stdout:
            (recovery_dir / "before.patch").write_bytes(result.stdout)
    except FileNotFoundError:
        pass
    
    # Capture staged changes (binary-safe)
    try:
        result = subprocess.run(
            ["git", "diff", "--binary", "--cached"],
            cwd=project_dir,
            capture_output=True
        )
        if result.returncode == 0 and result.stdout:
            (recovery_dir / "staged.patch").write_bytes(result.stdout)
    except FileNotFoundError:
        pass
    
    # Capture git status snapshot
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain=v1"],
            cwd=project_dir,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            (recovery_dir / "status_before.txt").write_text(result.stdout)
    except FileNotFoundError:
        pass
    
    # Copy artifact for reference
    artifact_copy = recovery_dir / artifact_path.name
    shutil.copy2(str(artifact_path), str(artifact_copy))


def save_landed_manifest(recovery_dir: Path, landed_files: list[dict]) -> None:
    """Save the manifest of landed files after successful extraction."""
    manifest = {
        "files": landed_files,
        "dirs_created": []  # TODO: track created directories
    }
    manifest_path = recovery_dir / "landed_manifest.yaml"
    with open(manifest_path, "w") as f:
        yaml.dump(manifest, f, default_flow_style=False)


def get_recovery_info(project_dir: Path, iteration: int) -> dict | None:
    """Get recovery information for an iteration."""
    recovery_dir = project_dir / ".cdd-flow" / "recovery" / str(iteration)
    if not recovery_dir.exists():
        return None
    
    info = {
        "iteration": iteration,
        "recovery_dir": recovery_dir,
        "has_before_patch": (recovery_dir / "before.patch").exists(),
        "has_staged_patch": (recovery_dir / "staged.patch").exists(),
        "has_manifest": (recovery_dir / "landed_manifest.yaml").exists(),
    }
    
    # Load metadata
    metadata_file = recovery_dir / "metadata.yaml"
    if metadata_file.exists():
        with open(metadata_file) as f:
            metadata = yaml.safe_load(f)
            info["baseline"] = metadata.get("baseline", {})
            info["timestamp"] = metadata.get("timestamp")
            info["artifact_name"] = metadata.get("artifact_name")
    
    # Load manifest
    manifest_file = recovery_dir / "landed_manifest.yaml"
    if manifest_file.exists():
        with open(manifest_file) as f:
            info["manifest"] = yaml.safe_load(f)
    
    # Find the artifact
    for f in recovery_dir.iterdir():
        if f.suffix in {".tar", ".py", ".yaml", ".json"} or f.name.endswith(".tar.gz"):
            if f.name not in {"metadata.yaml", "landed_manifest.yaml"}:
                info["artifact"] = f
                break
    
    return info


def perform_undo(project_dir: Path, iteration: int, force: bool = False) -> tuple[bool, str]:
    """
    Undo a landing by reverting to pre-landing state.
    
    Algorithm (scoped to manifest files only):
    1. Load manifest of landed files
    2. Check if user modified landed files (warn unless force)
    3. For each file in manifest:
       - If action=created: delete the file
       - If action=modified: git checkout -- <path>
    4. Apply before.patch (restore pre-landing uncommitted work)
    5. Apply staged.patch (restore staged changes)
    
    Returns (success, message).
    """
    recovery = get_recovery_info(project_dir, iteration)
    if not recovery:
        return False, f"No recovery data for iteration {iteration}"
    
    manifest = recovery.get("manifest", {})
    files = manifest.get("files", [])
    
    if not files:
        return False, "No files in manifest to undo"
    
    # Process each file in manifest (scoped undo)
    for file_info in files:
        file_path = project_dir / file_info["path"]
        action = file_info.get("action", "modified")
        
        if action == "created":
            # Delete files that were created by the landing
            if file_path.exists():
                file_path.unlink()
        elif action == "modified":
            # Restore modified files to HEAD state
            subprocess.run(
                ["git", "checkout", "--", str(file_info["path"])],
                cwd=project_dir,
                capture_output=True
            )
    
    # Re-apply pre-landing uncommitted work
    if recovery["has_before_patch"]:
        patch_path = recovery["recovery_dir"] / "before.patch"
        result = subprocess.run(
            ["git", "apply", str(patch_path)],
            cwd=project_dir,
            capture_output=True
        )
        if result.returncode != 0:
            return True, "Reverted files but patch apply failed - at clean HEAD state"
    
    # Re-apply staged changes
    if recovery["has_staged_patch"]:
        patch_path = recovery["recovery_dir"] / "staged.patch"
        subprocess.run(
            ["git", "apply", "--cached", str(patch_path)],
            cwd=project_dir,
            capture_output=True
        )
    
    return True, "Reverted to pre-landing state"


def clear_recovery(project_dir: Path, up_to_iteration: int | None = None) -> None:
    """
    Clear recovery directories.
    
    If up_to_iteration is specified, clear only up to that iteration.
    Otherwise, clear all.
    """
    recovery_base = project_dir / ".cdd-flow" / "recovery"
    if not recovery_base.exists():
        return
    
    for item in recovery_base.iterdir():
        if item.is_dir():
            try:
                iteration_num = int(item.name)
                if up_to_iteration is None or iteration_num <= up_to_iteration:
                    shutil.rmtree(item)
            except ValueError:
                pass  # Not a numbered directory
