# Changelog

All notable changes to cdd-flow.

## [0.1.0] - 2025-12-30

### Initial Release

**Core Loop (Phase 1):**
- `land` command: Detect, integrate, and clean artifacts from Downloads
- `undo` command: Revert last landing (scoped to manifest files)
- `ctx` command: Generate context via cdd-context
- `status` command: Show session state

**Session Management (Phase 2):**
- `start` command: Begin a tracked session with baseline capture
- `complete` command: End session successfully with summary
- `abandon` command: Abort session and revert to baseline
- `checkpoint` command: Commit verified state
- `verify` command: Run verification gates (auto-detection + config)
- `history` command: Show iterations and checkpoints

**Architecture:**
- Session management: explicit sessions with baseline capture for abandon
- Implicit sessions: lightweight state tracking for quick `land` workflows
- Recovery mechanics: full state capture (unstaged, staged, manifest)
- Safe tar extraction: rejects path traversal, symlinks, protected paths
- Trash management: time-limited quarantine
- Verification: configurable steps or auto-detection (CDD, npm, pytest)

**Platform:**
- macOS only (uses `pbcopy` for clipboard)
- Python 3.10+

**Dependencies:**
- cdd-context >= 0.3.0
- cdd-tooling >= 0.1.1

---

## Roadmap

### Phase 1: Core Loop ✓
- [x] `land` command with detection, integration, cleaning
- [x] `undo` command for last landing
- [x] `ctx` command delegating to cdd-context
- [x] `status` command for basic state

### Phase 2: Sessions ✓
- [x] `start` / `complete` / `abandon` session lifecycle
- [x] `checkpoint` with verification gate
- [x] `verify` standalone command
- [x] `history` command

### Phase 3: Polish
- [ ] File routing rules for single-file landings
- [ ] Auto-detection of verification commands (enhanced)
- [ ] `rollback` to checkpoints
- [ ] `clean` command for trash purge
- [ ] Trash auto-purge on landing
