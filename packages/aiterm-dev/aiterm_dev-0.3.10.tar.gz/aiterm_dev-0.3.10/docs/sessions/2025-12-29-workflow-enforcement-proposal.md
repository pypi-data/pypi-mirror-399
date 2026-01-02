# Session: Workflow Enforcement Proposal

**Date:** 2025-12-29
**Project:** aiterm + flow-cli
**Focus:** Smart branch workflow enforcement

---

## Summary

Designed and documented a 4-layer smart workflow enforcement system:

```
feature/* ──► dev ──► main
hotfix/*  ────┴───────┘
bugfix/*  ────┘
release/* ────────────┘
```

## Work Split

| Tool | Layer | Commands |
|------|-------|----------|
| **flow-cli** | Shell (instant) | `g feature`, `g promote`, `g release` |
| **aiterm** | Rich CLI | `ait workflows enforce/branch-status/violations` |
| **Shared** | Git hooks | pre-push (block main/dev, log violations) |

## Documentation Updated

1. `flow-cli/TODO.md` - Added Priority 0: Workflow Enforcement
2. `flow-cli/IDEAS.md` - Added HIGH PRIORITY section with examples
3. `aiterm/V0.4.0-PLAN.md` - Added Phase 1d (depends on flow-cli)

## Proposal Location

`~/.claude/plans/refactored-growing-riddle.md`

## Next Steps

1. **flow-cli session:** Implement g dispatcher commands
2. **aiterm Phase 1d:** Add `ait workflows` CLI commands

---

*Session duration: ~45 minutes*
