# CLAUDE.md

This file provides guidance to Claude Code when working with the aiterm project.

## Project Overview

**aiterm** - AI Terminal Optimizer CLI for Claude Code, OpenCode, and Gemini CLI workflows.

**What it does:**
- Optimizes terminal setup (iTerm2, Ghostty, etc.) for AI coding workflows
- Manages terminal profiles, context detection, and visual customization
- Integrates with Claude Code CLI (hooks, commands, auto-approvals, MCP servers)
- Session-aware workflow automation with chaining support
- Craft plugin management for Claude Code
- OpenCode and Gemini CLI configuration management

**Tech Stack:**
- **Language:** Python 3.10+
- **CLI Framework:** Typer + Rich
- **Testing:** pytest (611 tests)
- **Distribution:** Homebrew, PyPI, curl installer

---

## Current Version: v0.6.0 (Dec 30, 2025)

### v0.6.0 Features - Interactive Tutorial System

**Tutorial System** (`ait learn`):
- `ait learn` - List all tutorials
- `ait learn start <level>` - Begin a tutorial
- `ait learn start <level> -s N` - Resume from step
- `ait learn info <level>` - Show tutorial details

**3 Progressive Levels (31 total steps):**

| Level | Steps | Duration | Topics |
|-------|-------|----------|--------|
| Getting Started | 7 | ~10 min | Install, detect, switch, help |
| Intermediate | 11 | ~20 min | Claude Code, workflows, sessions |
| Advanced | 13 | ~35 min | Release, craft, MCP, IDE |

**Visual Documentation:**
- 9 GIF demos (VHS-generated)
- 6 Mermaid diagrams
- 4 tutorial pages
- REFCARD-TUTORIALS.md

**Statistics:** 75 tutorial tests, 685 total tests

### Previous Releases

| Version | Date | Highlights |
|---------|------|------------|
| v0.5.0 | Dec 30 | Release automation (7 commands) |
| v0.4.0 | Dec 30 | Workflows + Craft integration |
| v0.3.15 | Dec 30 | Ghostty full iTerm2 parity |
| v0.3.9 | Dec 29 | Ghostty terminal support |
| v0.3.6 | Dec 27 | curl installer |

---

## Quick Reference

### Installation

```bash
# Quick Install (auto-detects best method)
curl -fsSL https://raw.githubusercontent.com/Data-Wise/aiterm/main/install.sh | bash

# Homebrew (macOS)
brew install data-wise/tap/aiterm

# PyPI
pip install aiterm-dev
```

### Essential Commands

```bash
# Core
ait doctor                       # Health check
ait detect                       # Show project context
ait switch                       # Apply context to terminal

# Tutorials (v0.6.0)
ait learn                        # List all tutorials
ait learn start getting-started  # Begin tutorial
ait learn info intermediate      # Show tutorial details

# Release Management (v0.5.0)
ait release check                # Validate release readiness
ait release full 0.6.0           # Full release workflow

# Workflows (v0.4.0)
ait workflows status             # Session + workflow status
ait workflows run test           # Run test workflow
ait workflows run lint+test      # Chain workflows
ait workflows custom list        # List custom workflows

# Craft (v0.4.0)
ait craft status                 # Plugin status
ait craft list                   # List commands/skills
ait craft sync                   # Sync with project

# Claude Code
ait claude settings              # View settings
ait claude approvals list        # Show auto-approvals
ait sessions live                # Active sessions

# Terminals
ait terminals detect             # Detect current terminal
ait ghostty theme                # List/set Ghostty themes
ait ghostty status               # Ghostty config status

# Feature Workflow
ait feature status               # Branch pipeline view
ait feature start auth -w        # Start feature with worktree
ait feature cleanup              # Clean merged branches
```

### Key Paths

| Path | Purpose |
|------|---------|
| `~/.config/aiterm/` | Config directory (XDG) |
| `~/.config/aiterm/workflows/` | Custom YAML workflows |
| `~/.claude/plugins/craft` | Craft plugin location |
| `~/.claude/sessions/` | Session tracking data |

---

## Development

### Running Tests

```bash
pytest                           # All tests
pytest tests/test_workflows.py   # Workflow tests only
pytest tests/test_craft.py       # Craft tests only
pytest -x                        # Stop on first failure
```

### Project Structure

```
src/aiterm/
├── cli/                 # CLI commands (Typer)
│   ├── main.py          # Entry point
│   ├── craft.py         # Craft plugin management
│   ├── workflows.py     # Workflow runner
│   ├── ghostty.py       # Ghostty terminal
│   ├── feature.py       # Feature workflow
│   └── sessions.py      # Session coordination
├── terminal/            # Terminal backends
│   ├── iterm2.py
│   └── ghostty.py
├── context/             # Context detection
├── claude/              # Claude Code integration
└── opencode/            # OpenCode integration
```

### Adding a New Command

1. Create file in `src/aiterm/cli/`
2. Define Typer app with commands
3. Register in `main.py`
4. Add tests in `tests/`
5. Update `docs/reference/commands.md`

### Commit Convention

```
type(scope): subject

feat(workflows): add workflow chaining
fix(ghostty): handle missing config
docs: update commands reference
```

---

## Integration Points

### Craft Plugin (v1.8.0+)
- Location: `~/.claude/plugins/craft`
- Source: `~/projects/dev-tools/claude-plugins/craft`
- 60 commands, 16 skills, 8 agents

### Session Coordination
- Hooks: `~/.claude/hooks/session-register.sh`, `session-cleanup.sh`
- Data: `~/.claude/sessions/active/`, `~/.claude/sessions/history/`
- Auto-registers sessions on Claude Code start

### Terminal Support
| Terminal | Features |
|----------|----------|
| iTerm2 | Profiles, badges, status bar |
| Ghostty | Themes, keybinds, sessions |
| Kitty | Tab titles |
| WezTerm | Lua config |

---

## CI/CD

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `docs.yml` | Push to main | Auto-deploy docs |
| `test.yml` | PR/Push | Run pytest |
| `workflow.yml` | Tag push | PyPI publish |

---

## Links

- **Repo:** https://github.com/Data-Wise/aiterm
- **Docs:** https://Data-Wise.github.io/aiterm/
- **PyPI:** https://pypi.org/project/aiterm-dev/
- **Homebrew:** `brew install data-wise/tap/aiterm`
