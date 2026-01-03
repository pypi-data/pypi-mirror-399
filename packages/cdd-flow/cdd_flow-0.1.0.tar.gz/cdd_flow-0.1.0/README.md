# cdd-flow

AI-Assisted Development Delivery System

**Status:** v0.1.0 (draft) | Part of the [CDD](https://github.com/thegdyne/cdd) ecosystem

## The Problem

AI-assisted development is fast. The handoff is slow.

```
You:     "Here's my context"          ← cdd-context handles this
AI:      "Here's your artifact"       
You:     *click download*
         *clear downloads folder*     ← friction
         *cd to project*              ← friction
         *extract tar*                ← friction
         *check what changed*         ← friction
         *run tests*                  ← friction
         *oops wrong project*         ← recovery?
         *download again*             ← repeat friction
```

The bottleneck moved. It's not writing code anymore. It's the artifact handoff.

## The Solution

```bash
cdd-flow land
```

That's it. Artifact detected, integrated, Downloads cleaned, changes reported.

## Quick Start

```bash
# Install
pip install cdd-flow

# In your project
cd ~/repos/my-project

# Land an artifact from AI
cdd-flow land

# Land and verify
cdd-flow land --verify

# Land, verify, and checkpoint
cdd-flow land --checkpoint "feature working"

# Oops, undo that
cdd-flow undo
```

## The Core Loop

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   cdd-flow ctx          Push context to AI (clipboard)          │
│        │                                                        │
│        ▼                                                        │
│   [Work with AI]        AI produces artifact                    │
│        │                                                        │
│        ▼                                                        │
│   cdd-flow land         Detect → Integrate → Clean → Report     │
│        │                                                        │
│        ▼                                                        │
│   cdd-flow verify       Run CDD gates (optional)                │
│        │                                                        │
│        ▼                                                        │
│   cdd-flow checkpoint   Commit verified state                   │
│        │                                                        │
│        └────────────────► Iterate or complete                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Commands

### Core Loop

```bash
cdd-flow ctx                    # Generate context → clipboard
cdd-flow land                   # Integrate artifact from Downloads
cdd-flow verify                 # Run verification gates
cdd-flow checkpoint "message"   # Commit verified state
```

### Session Management

```bash
cdd-flow start "implement feature"   # Begin tracked session
cdd-flow status                      # Show current state
cdd-flow complete                    # End session
cdd-flow abandon                     # Abort and revert
```

### Recovery

```bash
cdd-flow undo                   # Revert last landing
cdd-flow rollback               # Revert to last checkpoint
cdd-flow history                # Show iterations
```

## Landing Intelligence

cdd-flow handles the mess:

```bash
$ cdd-flow land

# Clean state
✓ Found: artifact.tar (1 minute ago)
✓ Extracted 3 files
✓ Cleaned Downloads

# Mac duplicate nightmare
⚠ Multiple versions detected:
    artifact (2).tar  (30 sec ago) ← using
    artifact (1).tar  (5 min ago)  ← cleaning
    artifact.tar      (2 hours)    ← cleaning
✓ Landed and cleaned 3 files from Downloads

# Nothing there
✗ No recent artifacts in ~/Downloads
  Did you download from Claude?
```

## Recovery

Every landing is reversible until checkpoint:

```bash
$ cdd-flow land           # Landed, but wrong
$ cdd-flow undo           # Reverted
$ cdd-flow land           # Try again
$ cdd-flow checkpoint     # Lock it in
```

## Verification

Auto-detects or configure:

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
```

## Aliases

For muscle memory:

```bash
alias fl='cdd-flow land'
alias flv='cdd-flow land --verify'
alias fu='cdd-flow undo'
alias fc='cdd-flow ctx'
alias fcp='cdd-flow checkpoint'
alias fs='cdd-flow status'
```

Typical rhythm:

```bash
$ fc              # Context → clipboard → paste to AI
$ fl              # Land artifact
$ flv             # Land + verify  
$ fcp "done"      # Checkpoint
```

## Requirements

- Python 3.10+
- git (for checkpoints and recovery)

Dependencies installed automatically:
- cdd-context (context generation)
- cdd-tooling (verification)

## Ecosystem

```
┌─────────────────────────────────────────────────────────────────┐
│                         CDD ECOSYSTEM                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   cdd-flow         Orchestration (this repo)       ← YOU ARE   │
│      │             land, ctx, verify, checkpoint       HERE     │
│      │                                                          │
│      ├─────────► cdd-context     Context generation             │
│      │                           build, status, clear-cache     │
│      │                                                          │
│      └─────────► cdd-tooling     Verification                   │
│                                  analyze, lint, test, compare   │
│                                                                 │
│   cdd              Methodology (spec only)                      │
│                    SPEC.md, README.md                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Installation

```bash
# Full workstation setup (installs cdd-context and cdd-tooling)
pip install cdd-flow

# Or install individually
pip install cdd-context   # Just context generation
pip install cdd-tooling   # Just verification
```

## Documentation

- [SPEC.md](SPEC.md) — Full specification
- [CHANGELOG.md](CHANGELOG.md) — Version history

## License

MIT
