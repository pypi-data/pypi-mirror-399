# Feature Workflow Quick Reference

Fast reference for `ait feature` commands.

---

## Commands

```bash
ait feature status              # Pipeline visualization
ait feature list                # List features (active only)
ait feature list --all          # List all (including merged)
ait feature start <name>        # Create feature/<name> from dev
ait feature start <name> -w     # Create with worktree
ait feature cleanup             # Remove merged branches
ait feature cleanup -n          # Dry run (preview)
```

---

## Quick Start

```bash
# Start new feature with worktree
ait feature start auth-v2 --worktree
cd ~/.git-worktrees/myproject/auth-v2

# Check what's active
ait feature status

# After PR merged, cleanup
ait feature cleanup
```

---

## Options

### `ait feature start`

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--worktree` | `-w` | off | Create in worktree |
| `--no-install` | | off | Skip dep install |
| `--base` | `-b` | `dev` | Base branch |

### `ait feature cleanup`

| Option | Short | Description |
|--------|-------|-------------|
| `--dry-run` | `-n` | Preview only |
| `--force` | `-f` | No confirmation |

---

## Worktree Paths

```
~/.git-worktrees/
└── <project>/
    └── <feature-name>/
```

---

## flow-cli Comparison

| Task | flow-cli | aiterm |
|------|----------|--------|
| Quick branch | `gfs name` | - |
| Quick PR | `gfp` | - |
| Pipeline | - | `ait feature status` |
| Full setup | - | `ait feature start -w` |
| Cleanup | - | `ait feature cleanup` |

---

## See Also

- [Full Guide](../guide/feature-workflow.md)
- [Git Worktrees](../guides/GIT-WORKTREES-GUIDE.md)
- [Sessions](REFCARD-SESSIONS.md)
