---
doc_status: draft
doc_version: 0.1.0
date: 2025-12-30
---

# cdd-flow Specification

AI-Assisted Development Delivery System

## What

A command-line tool that orchestrates the AI development loop:

1. **Context out** — Push project state to AI
2. **Artifact in** — Receive and integrate AI-produced artifacts
3. **Verify** — Run appropriate gates
4. **Iterate** — Rapid cycles until done
5. **Checkpoint** — Lock in verified progress

This is not a git wrapper. It's a delivery system optimised for AI-assisted development cadence.

---

## Glossary

| Term | Definition |
|------|------------|
| **Session** | A focused unit of work with AI; has goal, iterations, outcome |
| **Iteration** | One round-trip: context out → artifact in → verify |
| **Landing** | Artifact arrives, integrates into project |
| **Checkpoint** | Verified state committed to git |
| **Landing Zone** | `~/Downloads` — where artifacts arrive from AI |
| **Staging** | Temporary area for extraction before integration |
| **Recovery** | Ability to undo a landing before checkpoint |

---

## Design Principles

### 1. Speed Over Ceremony

AI iterations are fast. The tooling must not be the bottleneck.

```
BAD:  land → configure → confirm → extract → confirm → verify → confirm
GOOD: land → done (with smart defaults)
```

### 2. Recoverable by Default

Every landing is reversible until checkpoint. Mistakes are cheap.

### 3. Clean State Maintenance

Downloads folder is always clean after landing. No `(1)` suffix disasters.

**Exception:** `--no-clean` explicitly disables cleanup for debugging. When used, the "always clean" guarantee does not apply and `status` reflects this.

### 4. Context is Currency

The thing you paste to AI matters. Make it effortless to generate and update.

### 5. CDD-Native

Verification means contracts and gates, not just "it compiles".

---

## Platform Support

**[NORMATIVE]**

cdd-flow targets **macOS only**. Behavior on non-macOS platforms is undefined and out of scope for v0.1.x.

**Requirements:**
- macOS 12+ (Monterey or later recommended)
- Python >= 3.10
- Git (for recovery mechanics)

**Clipboard:** Uses `pbcopy` exclusively.

**Downloads:** Handles macOS duplicate suffix pattern `(n)` only. Other OS patterns (e.g., Windows " - Copy") are not detected.

---

## State Model

### Global State

```
~/.cdd-flow/
  config.yaml           # Global configuration
  trash/                # Landed artifacts (time-limited quarantine)
    {timestamp}-{filename}
```

### Project State

```
{project}/
  .cdd-flow/
    session.yaml        # Current session (if active)
    config.yaml         # Project-specific settings
    sessions/           # Archived sessions (completed/abandoned)
      {session-id}.yaml
    recovery/
      {iteration}/
        metadata.yaml   # Baseline commit, timestamp
        before.patch    # Unstaged changes
        staged.patch    # Staged changes
        status_before.txt  # git status --porcelain=v1
        landed_manifest.yaml
        {artifact}      # Copy of landed artifact
```

---

## Session Lifecycle

```
                    ┌─────────────┐
                    │   (none)    │
                    └──────┬──────┘
                           │ start
                           ▼
                    ┌─────────────┐
         ┌─────────│   active    │◄────────┐
         │         └──────┬──────┘         │
         │                │                │
         │ abandon        │ complete       │ land/verify/checkpoint
         │                │                │ (iterations)
         ▼                ▼                │
  ┌─────────────┐  ┌─────────────┐         │
  │  abandoned  │  │  completed  │         │
  └─────────────┘  └─────────────┘         │
                                           │
         └─────────────────────────────────┘
```

### Session States

| State | Description | Transitions |
|-------|-------------|-------------|
| `(none)` | No active session | → `active` via `start` |
| `active` | Work in progress | → `completed` via `complete` |
| | | → `abandoned` via `abandon` |
| `completed` | Session finished successfully | → `(none)` (archived) |
| `abandoned` | Session scrapped, reverted | → `(none)` (archived) |

### Session Start

**[NORMATIVE]**

```
cdd-flow start "goal description"

1. Check no active session exists (error if one does)
2. Record baseline:
   - baseline_commit = git rev-parse HEAD
   - baseline_dirty = (git status --porcelain not empty)
   - If dirty: 
     - git stash push -m "cdd-flow-baseline-{session-id}"
     - stash_ref = git rev-parse stash@{0}  # Capture stable ref
3. Create session.yaml with baseline info (including stash_ref if applicable)
4. Report: "Session started: {goal}"
```

### Session Abandon

**[NORMATIVE]**

```
cdd-flow abandon [--force]

1. Check active session exists
2. Preflight:
   - If uncommitted changes and no --force: 
     - In interactive mode: prompt for confirmation
     - In non-interactive mode (piped/no TTY): exit 1 with error
3. Revert to baseline:
   - git reset --hard {baseline.commit}
   - If baseline had stash: git stash apply {stash_ref}
     - If apply succeeds: git stash drop {stash_ref}
     - If apply conflicts: leave stash, print recovery instructions
4. Clear .cdd-flow/recovery/ directory
5. Mark session status: abandoned
6. Archive session.yaml to .cdd-flow/sessions/{session-id}.yaml
7. Report: "Session abandoned, reverted to baseline"
```

**Note:** `--force` bypasses confirmation and is required for scripts/automation.

**Stash conflict recovery:**

If `git stash apply` fails due to conflicts:
```
⚠ Stash could not be applied automatically.
  Your pre-session changes are preserved in the stash.
  
  To see stashed changes: git stash show -p
  To apply manually:      git stash apply
  To discard:             git stash drop
```

### Session Complete

**[NORMATIVE]**

```
cdd-flow complete

1. Check active session exists
2. Mark session status: completed
3. Archive session.yaml to .cdd-flow/sessions/{session-id}.yaml
4. Clear .cdd-flow/recovery/ directory
5. Report session summary (iterations, checkpoints, duration)
```

### Implicit Sessions

**[NORMATIVE]**

When `land` is called without an explicit `start`:

1. Create implicit session with timestamped ID
2. `undo` works normally (uses recovery/ state)
3. No baseline is captured (cannot `abandon`)
4. `status` shows "(implicit session)"
5. `complete` archives minimal session (no summary, just clears state)

This enables quick iteration without ceremony while preserving single-landing recovery.

---

## Landing Mechanics

### Artifact Detection

**[NORMATIVE]**

Landing zone: `~/Downloads` (configurable via `landing_zone`)

Detection algorithm:

```
1. Scan landing zone for candidate files
2. Filter by extension: use `artifact_extensions` from config (see Configuration)
3. Exclude partial downloads: .crdownload, .part, .download, .tmp
4. Exclude hidden files (starting with .)
5. Filter by recency: modified within threshold (default: 15 minutes)
6. Filter by stability: file size unchanged for 2+ seconds (avoid in-progress downloads)
7. Sort by mtime descending (newest first)
8. Handle OS duplicates: file.tar, file (1).tar, file (2).tar
   - Duplicates = same base name + OS suffix pattern + same extension
   - Select newest mtime among duplicates
   - Mark OTHER duplicates of SAME base name as stale (for cleanup)
   - Do NOT mark unrelated old files as stale
9. Return: (candidate, confidence, stale_files, warnings)
```

**Duplicate detection pattern:**

```regex
^(.+?) \((\d+)\)(\.tar\.gz|\.tgz|\.[^.]+)$
```

Matches: `artifact (1).tar`, `report (2).pdf`, `file (12).tar.gz`

Does NOT match: `my report.tar`, `file-v2.tar` (these are different files, not OS duplicates)

Confidence levels:

| Level | Condition |
|-------|-----------|
| `high` | Single recent file, no duplicates |
| `medium` | Recent file exists, but duplicates present |
| `low` | Only old files, or multiple recent ambiguous |
| `none` | No candidates found |

### Landing Flow

**[NORMATIVE]**

```
┌─────────────────────────────────────────────────────────────────┐
│  cdd-flow land                                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. DETECT                                                      │
│     - Scan landing zone                                         │
│     - Assess confidence                                         │
│     - If none: exit with guidance                               │
│     - If low: prompt for confirmation                           │
│                                                                 │
│  2. PREPARE RECOVERY                                            │
│     - Record baseline_commit = git rev-parse HEAD               │
│     - git diff --binary > before.patch (unstaged)               │
│     - git diff --binary --cached > staged.patch                 │
│     - git status --porcelain=v1 > status_before.txt             │
│     - Copy artifact to .cdd-flow/recovery/{iteration}/          │
│                                                                 │
│  3. INTEGRATE (with safe extraction)                            │
│     - tar: extract with safety checks (see Safe Extraction)     │
│     - single file: use --dest, routing rules, or prompt         │
│     - Record landed files in manifest                           │
│                                                                 │
│  4. CLEAN (unless --no-clean)                                   │
│     - mv artifact → ~/.cdd-flow/trash/{timestamp}-{name}        │
│     - mv stale duplicates → trash                               │
│                                                                 │
│  5. REPORT                                                      │
│     - Run cdd-flow ctx --changes --no-clip (unless --clip)       │
│     - Display summary                                           │
│     - If --verify: run verification                             │
│     - If --clip: copy changes to clipboard                      │
│                                                                 │
│  6. UPDATE SESSION                                              │
│     - Increment iteration                                       │
│     - Record landing metadata + manifest                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Safe Extraction Rules

**[NORMATIVE]**

Tar extraction MUST enforce these safety checks:

| Check | Behavior |
|-------|----------|
| Absolute paths | **Reject** — refuse to extract member |
| Path contains `..` | **Reject** — refuse to extract member |
| Resolved path outside project | **Reject** — refuse to extract member |
| Symlinks | **Reject** — refuse unless `--allow-symlinks` |
| Hardlinks | **Reject** — refuse unless `--allow-hardlinks` |
| Target is `.git/` | **Reject** — never overwrite git internals |
| Target is `.cdd-flow/` | **Reject** — never overwrite flow state |

**Algorithm:**

```python
for member in tar:
    # Reject absolute paths
    if member.name.startswith('/'):
        reject(member, "absolute path")
    
    # Reject path traversal
    if '..' in member.name.split('/'):
        reject(member, "path traversal")
    
    # Resolve and verify stays in project
    resolved = (project_root / member.name).resolve()
    if not resolved.is_relative_to(project_root):
        reject(member, "escapes project root")
    
    # Reject symlinks/hardlinks unless explicitly allowed
    if member.issym() and not allow_symlinks:
        reject(member, "symlink not allowed (use --allow-symlinks)")
    if member.islnk() and not allow_hardlinks:
        reject(member, "hardlink not allowed (use --allow-hardlinks)")
    
    # Protect internal directories
    if member.name.startswith('.git/') or member.name.startswith('.cdd-flow/'):
        reject(member, "protected path")
    
    extract(member)
```

On any rejection, the entire landing aborts with a clear error message listing rejected members.

### Single-File Landing

**[NORMATIVE]**

When landing a single file (not a tar archive):

**Destination resolution order:**
1. `--dest PATH` option (explicit)
2. Project routing rules in `.cdd-flow/config.yaml`
3. Interactive prompt (if TTY available)
4. Error with guidance (if non-interactive)

**Non-interactive behavior:**

If stdin is not a TTY and no destination can be determined:
```
✗ Cannot determine destination for: myfile.py
  Use --dest to specify, or add routing rules to .cdd-flow/config.yaml
```
Exit code: 1

### Trash Management

**[NORMATIVE]**

Trash location: `~/.cdd-flow/trash/`

Naming: `{ISO-timestamp}-{original-filename}`

Retention: 7 days (configurable)

Auto-purge: On `land`, `clean`, and `status` commands, purge items older than retention.

Note: Trash is a **time-limited quarantine**, not permanent storage. For true recovery, use `.cdd-flow/recovery/`.

---

## Recovery Mechanics

### Recovery State

**[NORMATIVE]**

On each landing, capture full recovery state in `.cdd-flow/recovery/{iteration}/`:

```
recovery/{iteration}/
├── metadata.yaml           # Recovery metadata
├── before.patch            # git diff --binary (unstaged changes)
├── staged.patch            # git diff --binary --cached (staged changes)  
├── status_before.txt       # git status --porcelain=v1
├── landed_manifest.yaml    # What the landing added/modified
└── artifact.tar            # Copy of original artifact
```

**metadata.yaml:**
```yaml
baseline:
  commit: "abc123"          # HEAD before landing
timestamp: "2025-12-30T10:35:00Z"
artifact_name: "artifact.tar"
```

**landed_manifest.yaml:**
```yaml
files:
  - path: src/new_file.py
    action: created
  - path: src/modified.py
    action: modified
dirs_created:
  - src/new_dir/
```

**Capture algorithm:**

```
1. Record baseline.commit = git rev-parse HEAD
2. Capture unstaged changes: git diff --binary > before.patch
3. Capture staged changes: git diff --binary --cached > staged.patch
4. Record status: git status --porcelain=v1 > status_before.txt
5. Perform landing (extract/copy)
6. Record landed files in landed_manifest.yaml (track created vs modified)
7. Copy artifact for reference (retained regardless of --no-clean)
```

**Note:** `before.patch` captures working tree vs index (unstaged only). `staged.patch` captures index vs HEAD. Together they represent all uncommitted work.

### Undo (Last Landing)

**[NORMATIVE]**

```
cdd-flow undo [--force] [--restore]

1. Check .cdd-flow/recovery/{current-iteration}/ exists
2. Load landed_manifest.yaml
3. Preflight: if user modified landed files since landing, warn and require --force
4. For each file in manifest:
   - If action=created: delete the file
   - If action=modified: git checkout -- <path> (restore to HEAD)
5. If before.patch exists and non-empty:
   - git apply before.patch (restore pre-landing uncommitted work)
6. If staged.patch exists and non-empty:
   - git apply --cached staged.patch (restore staged changes)
7. Decrement iteration counter
8. If --restore: copy artifact from recovery/ back to Downloads
```

**Important:** Undo is scoped to files in the manifest. Unrelated uncommitted changes are preserved.

**Failure modes:**

| Condition | Behavior |
|-----------|----------|
| User edited landed files | Warn, require `--force` to proceed |
| Patch apply fails | Warn, do not attempt further restoration. Working tree matches HEAD for manifest files; run `git status` to inspect. Unrelated files are not touched. |
| No recovery data | Error, exit 1 |

### Rollback (To Checkpoint)

**[NORMATIVE]**

```
cdd-flow rollback [checkpoint-id] [--force] [--dry-run]

1. If no checkpoint-id: use last checkpoint
2. Preflight checks:
   - Refuse if uncommitted changes exist (unless --force)
   - Print: "Rolling back to: {checkpoint.commit} ({checkpoint.message})"
3. If --dry-run: exit 0 after showing what would happen
4. git reset --hard {checkpoint.commit}
5. Clear recovery/ directory (checkpoint is now authoritative)
6. Reset iteration to checkpoint.iteration
```

**Guardrails:**

- Refuses on dirty working tree without `--force`
- Always prints target commit info before executing
- `--dry-run` shows plan without executing

---

## Verification

### Verify Command

**[NORMATIVE]**

```
cdd-flow verify

1. Load verification config (project or inferred)
2. Run each verification step in order
3. Report results
4. Exit 0 if all required steps pass
5. Exit 1 if any required step fails
```

### Verification Configuration

```yaml
# .cdd-flow/config.yaml
verify:
  steps:
    - name: lint
      command: cdd lint contracts/
      required: true
      
    - name: test
      command: cdd test contracts/
      required: true
      
    - name: build
      command: npm run build
      required: false  # Warn only
```

### Auto-Detection (No Config)

If no verify config exists, attempt to infer:

| Condition | Verification |
|-----------|--------------|
| `contracts/` exists | `cdd lint contracts/ && cdd test contracts/` |
| `package.json` exists | `npm test` (if `scripts.test` exists and is non-empty) |
| `pytest.ini` or `tests/` exists | `pytest` |
| None of above | Skip verification with warning |

**npm test detection:** Parse `package.json`, check if `scripts.test` key exists and value is not empty/undefined.

---

## Checkpoint Mechanics

**[NORMATIVE]**

```
cdd-flow checkpoint [message] [--no-verify] [--force]

1. If no message: generate from session goal + iteration
2. Run verification (unless --no-verify or --force)
   - If verification fails and no --force: exit 1
3. git add -A
4. git commit -m "{message}"
5. Record checkpoint in session:
   - iteration number
   - commit SHA
   - message
   - timestamp
   - verified: true/false
6. Clear recovery/ directory (no longer needed)
7. Report success
```

### Checkpoint Naming Convention

If message not provided, generate from session:

```
{session-goal} - iteration {n}
```

Example: `"implement PDF export - iteration 3"`

---

## Context Commands

### ctx (Push Context)

**[NORMATIVE]**

```
cdd-flow ctx [--full | --changes[=MODE]] [--no-clip]

  --full              Full project context
  --changes[=MODE]    Changes since last build
                      MODE: full (default), list, summaries
  --no-clip           Don't copy to clipboard

Default: --changes if session has iterations > 0, else --full

1. Run appropriate cdd-context command
2. Copy output to clipboard (unless --no-clip)
3. Display summary (not full content)
```

### Integration with cdd-context

| cdd-flow command | cdd-context equivalent |
|------------------|------------------------|
| `cdd-flow ctx` | Auto-selects based on session state |
| `cdd-flow ctx --full` | `cdd-context build --clip` |
| `cdd-flow ctx --changes` | `cdd-context build --changes --clip` |
| `cdd-flow ctx --changes=list` | `cdd-context build --changes=list --clip` |
| `cdd-flow ctx --changes=summaries` | `cdd-context build --changes=summaries --clip` |

---

## Command Reference

### Session Commands

| Command | Description |
|---------|-------------|
| `cdd-flow start [goal]` | Begin a new session |
| `cdd-flow status` | Show session state, iteration, recent landings |
| `cdd-flow complete` | End session successfully |
| `cdd-flow abandon` | Abort session, revert to pre-session state |

### Core Loop Commands

| Command | Description |
|---------|-------------|
| `cdd-flow ctx` | Generate and copy context to clipboard |
| `cdd-flow land` | Detect, integrate, and clean artifact |
| `cdd-flow verify` | Run verification gates |
| `cdd-flow checkpoint [msg]` | Commit verified state |

### Recovery Commands

| Command | Description |
|---------|-------------|
| `cdd-flow undo` | Revert last landing |
| `cdd-flow rollback [id]` | Revert to checkpoint |
| `cdd-flow history` | Show session iterations and checkpoints |

### Utility Commands

| Command | Description |
|---------|-------------|
| `cdd-flow config` | Show/edit configuration |
| `cdd-flow clean` | Purge old trash, clean landing zone |

---

## Command Options

### Global Options

| Option | Description |
|--------|-------------|
| `--project PATH` | Specify project directory (default: CWD) |
| `--verbose` | Detailed output |
| `--quiet` | Minimal output |
| `--dry-run` | Show what would happen, don't do it |

### land Options

| Option | Description |
|--------|-------------|
| `--verify` | Run verification after landing |
| `--checkpoint [MSG]` | Land + verify + checkpoint. MSG optional (auto-generates if omitted) |
| `--clip` | Copy changes summary to clipboard |
| `--dest PATH` | Destination for single-file landing |
| `--max-age MINS` | Override recency threshold (default: 15) |
| `--no-clean` | Don't remove artifact from Downloads (disables clean guarantee) |
| `--allow-symlinks` | Allow symlinks in tar (default: reject) |
| `--allow-hardlinks` | Allow hardlinks in tar (default: reject) |

**`--checkpoint` behavior:**

`--checkpoint` implies `--verify`. The checkpoint is only created if verification passes:

```
land --checkpoint "msg"  →  land + verify + (if pass) checkpoint "msg"
```

If verification fails, landing still succeeds but checkpoint is not created. Exit code reflects verification failure (exit 1).

### undo Options

| Option | Description |
|--------|-------------|
| `--force` | Proceed even if user modified landed files |
| `--restore` | Restore artifact to Downloads after undo |

### rollback Options

| Option | Description |
|--------|-------------|
| `--force` | Proceed even with uncommitted changes |
| `--dry-run` | Show what would happen, don't execute |

### checkpoint Options

| Option | Description |
|--------|-------------|
| `--force` | Bypass verification (not recommended) |
| `--no-verify` | Skip verification step |

### start Options

| Option | Description |
|--------|-------------|
| (none beyond global) | Goal is positional argument |

### abandon Options

| Option | Description |
|--------|-------------|
| `--force` | Proceed without confirmation prompt |

### ctx Options

| Option | Description |
|--------|-------------|
| `--full` | Full project context |
| `--changes[=MODE]` | Changes since last build. MODE: `full` (default), `list`, `summaries` |
| `--no-clip` | Don't copy to clipboard |

Default behavior: `--changes` if session has iterations > 0, else `--full`.

---

## Configuration

### Global Config

Location: `~/.cdd-flow/config.yaml`

**[NORMATIVE]**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `landing_zone` | path | `~/Downloads` | Where artifacts arrive |
| `trash_dir` | path | `~/.cdd-flow/trash` | Where cleaned artifacts go |
| `trash_retention_days` | int | `7` | Days before auto-purge |
| `default_recency_minutes` | int | `15` | Max age for artifact detection |
| `artifact_extensions` | list | (see below) | File extensions to recognise |
| `clipboard_copy` | string | `pbcopy` | Command to copy to clipboard |

**Note:** This tool is designed for macOS. Clipboard uses `pbcopy` by default.

Default artifact extensions:
```yaml
artifact_extensions:
  - .tar
  - .tar.gz
  - .tgz
  - .py
  - .yaml
  - .yml
  - .json
  - .md
  - .html
  - .htm
  - .jsx
  - .tsx
  - .ts
  - .js
  - .css
  - .scss
```

### Project Config

Location: `{project}/.cdd-flow/config.yaml`

**[NORMATIVE]**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `verify` | object | (auto-detect) | Verification configuration |
| `verify.steps` | list | `[]` | Verification steps to run |
| `verify.steps[].name` | string | required | Step name |
| `verify.steps[].command` | string | required | Command to execute |
| `verify.steps[].required` | bool | `true` | Whether failure blocks checkpoint |
| `routing` | object | `{}` | File routing rules for single-file landings |
| `landing_zone` | path | (global) | Override global landing zone |

Example:

```yaml
# .cdd-flow/config.yaml

verify:
  steps:
    - name: lint
      command: cdd lint contracts/
      required: true
    - name: test
      command: cdd test contracts/
      required: true
    - name: build
      command: npm run build
      required: false  # Warn only

routing:
  "*.py": src/
  "*.yaml": contracts/
  "*.md": docs/
```

---

## Session Schema

**[NORMATIVE]**

```yaml
# .cdd-flow/session.yaml

version: "1"
session:
  id: "2025-12-30T10-30-00-pdf-export"
  goal: "implement PDF export"
  started: "2025-12-30T10:30:00Z"
  status: active  # active | completed | abandoned
  
  # Baseline for abandon recovery (explicit sessions only)
  baseline:
    commit: "abc123def"           # HEAD at session start
    had_dirty_tree: false         # Was there uncommitted work?
    stash_ref: null               # If dirty, the stash reference
  
  iteration: 3
  
  landings:
    - iteration: 1
      timestamp: "2025-12-30T10:35:00Z"
      artifact: "artifact.tar"
      files:
        - path: src/pdf.py
          action: created
        - path: contracts/pdf.yaml
          action: created
      
    - iteration: 2
      timestamp: "2025-12-30T10:42:00Z"
      artifact: "pdf.py"
      files:
        - path: src/pdf.py
          action: modified
        
    - iteration: 3
      timestamp: "2025-12-30T10:48:00Z"
      artifact: "artifact.tar"
      files:
        - path: src/pdf.py
          action: modified
        - path: src/export.py
          action: created
  
  checkpoints:
    - iteration: 2
      commit: "a1b2c3d4"
      message: "pdf rendering working"
      timestamp: "2025-12-30T10:45:00Z"
```

**Landing entry fields:**

| Field | Type | Description |
|-------|------|-------------|
| `iteration` | int | Iteration number |
| `timestamp` | ISO8601 | When landing occurred |
| `artifact` | string | Original artifact filename |
| `files` | list | Files affected |
| `files[].path` | string | File path relative to project |
| `files[].action` | enum | `created` or `modified` |

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Failure (verification failed, operation failed) |
| 2 | No artifact found |
| 3 | No active session (for commands requiring session) |
| 4 | User abort (cancelled prompt) |

**Note:** Verification failures also return exit code 1. To distinguish verification failure from other failures, parse command output or check for verification-specific messages.

---

## Error Handling

### No Artifact Found

```
$ cdd-flow land

✗ No recent artifacts in ~/Downloads

  Possible causes:
  - Forgot to download from Claude
  - File older than 15 minutes (use --max-age to override)
  
  Recent files (not matching artifact patterns):
    - vacation.jpg (2 minutes ago)
```

### Duplicate Detection

```
$ cdd-flow land

⚠ Multiple versions detected (Mac duplicate issue):
    artifact (2).tar  (1 minute ago) ← using this
    artifact (1).tar  (10 minutes ago) ← will clean
    artifact.tar      (2 hours ago) ← will clean

  Landing: artifact (2).tar
  
  Proceed? [Y/n]
```

### No Session Active

```
$ cdd-flow checkpoint "done"

✗ No active session

  Start one with: cdd-flow start "your goal"
  
  Or use git directly: git commit -m "done"
```

### Verification Failed

```
$ cdd-flow checkpoint "pdf export complete"

Running verification...
  ✓ lint passed
  ✗ test failed
  
  T003: test_pdf_output
    Expected: $.result.pages = 3
    Actual: $.result.pages = 2
    
Checkpoint blocked. Fix and retry, or use --force to bypass.
```

---

## Interaction Patterns

### Pattern 1: Quick Iteration (No Explicit Session)

For fast, informal work:

```bash
$ cd ~/repos/my-project
$ cdd-flow land
✓ Landed artifact.tar (3 files)
✓ Cleaned Downloads

$ cdd-flow land --verify
✓ Landed fix.py
✓ Verification passed

$ git add -A && git commit -m "done"
```

Session is implicit. Recovery still works for last landing.

### Pattern 2: Formal Session

For tracked, recoverable work:

```bash
$ cdd-flow start "implement PDF export"
✓ Session started: implement PDF export

$ cdd-flow ctx
✓ Context copied (4.2kb)

# ... work with AI ...

$ cdd-flow land --verify
✓ Landed (iteration 1)
✓ Verification passed

$ cdd-flow checkpoint "basic structure"
✓ Committed: basic structure (a1b2c3d)

# ... more iterations ...

$ cdd-flow complete
✓ Session completed: implement PDF export
  - 5 iterations
  - 3 checkpoints
  - Duration: 45 minutes
```

### Pattern 3: Recovery Flow

```bash
$ cdd-flow land
✓ Landed artifact.tar

# Oops, wrong files
$ cdd-flow undo
✓ Reverted landing
✓ Restored artifact.tar to Downloads

# Try again after AI fixes
$ cdd-flow land
✓ Landed artifact.tar (take 2)
```

---

## Integration Points

### Dependency Model

```
cdd-flow
  └── depends on: cdd-context (context generation)
  └── depends on: cdd-tooling (verification)
  └── depends on: git (checkpoints, recovery)
```

All four CDD repos (cdd, cdd-context, cdd-tooling, cdd-flow) remain independent. cdd-flow is thin orchestration.

### cdd-context

**Required dependency.** Used for context generation.

```bash
# cdd-flow ctx delegates to:
cdd-context build --clip
cdd-context build --changes --clip
```

Minimum version: `>=0.3.0`

### cdd-tooling

**Required dependency.** Used for verification.

```bash
# cdd-flow verify delegates to:
cdd lint contracts/
cdd test contracts/
```

Minimum version: `>=0.1.1`

### git

**Required.** Used for checkpoints, recovery, state detection.

```bash
# cdd-flow uses:
git diff
git add
git commit
git reset
git apply
```

### Version Compatibility

cdd-flow pins minimum versions of dependencies. When breaking changes occur in cdd-context or cdd-tooling, cdd-flow CHANGELOG documents the required upgrade path.

---

## MVP Scope

### Phase 1: Core Loop

Commands:
- `land` (with detection, integration, cleaning)
- `undo` (last landing only)
- `ctx` (delegates to cdd-context)
- `status` (basic state display)

### Phase 2: Sessions

Commands:
- `start`
- `complete`
- `abandon`
- `checkpoint`
- `verify`
- `history`

### Phase 3: Polish

- Configuration system
- Routing rules for single files
- Auto-detection of verification
- `rollback` to checkpoints
- Trash auto-purge

---

## Success Criteria

- [ ] `land` handles all Downloads states (clean, duplicates, stale, empty)
- [ ] Recovery works: `undo` restores pre-landing state
- [ ] Downloads is always clean after `land`
- [ ] Context flows smoothly via `ctx`
- [ ] Sessions track iterations and checkpoints
- [ ] Verification integrates with CDD tooling
- [ ] Sub-second response for common operations

---

## Appendix: Aliases

Suggested shell aliases for muscle memory:

```bash
# ~/.zshrc or ~/.bashrc

alias fl='cdd-flow land'
alias flv='cdd-flow land --verify'
alias flc='cdd-flow land --checkpoint'
alias fu='cdd-flow undo'
alias fc='cdd-flow ctx'
alias fcp='cdd-flow checkpoint'
alias fs='cdd-flow status'
```

Typical session:

```bash
$ fc                    # Context to clipboard, paste to AI
$ fl                    # Land artifact
$ flv                   # Land + verify
$ fcp "feature done"    # Checkpoint
```

---

*Version 0.1.0 — Draft*
