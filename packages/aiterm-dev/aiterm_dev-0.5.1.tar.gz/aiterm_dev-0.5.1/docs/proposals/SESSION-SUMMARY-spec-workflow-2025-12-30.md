# Session Summary: Spec Capture & Review Workflow

**Date:** 2025-12-30
**Project:** claude-plugins (workflow + craft)

---

## Commands Added/Modified

| Command | Version | Location | What It Does |
|---------|---------|----------|--------------|
| `/workflow:brainstorm` | v2.2.0 | `workflow/commands/brainstorm.md` | **Extended** - Now captures specs with `--save-spec` flag |
| `/spec:review` | v1.0.0 | `workflow/commands/spec-review.md` | **NEW** - Review, approve, archive specs |
| `/craft:do` | v1.1.0 | `craft/commands/do.md` | **Extended** - Checks for matching spec before routing |
| `/workflow:done` | - | `workflow/commands/done.md` | **Extended** - Offers to archive completed specs |

---

## New Files Created

| File | Purpose |
|------|---------|
| `workflow/templates/SPEC-TEMPLATE.md` | Comprehensive spec template |
| `workflow/commands/spec-review.md` | New review command |

---

## Workflow Chain

```
/brainstorm --save-spec "feature"
        ↓
   Q: Capture as spec? → Yes
   Q: User type? → Developer/End User/Admin
        ↓
   docs/specs/SPEC-feature-2025-12-30.md
        ↓
/spec:review feature
        ↓
   Validation checks (acceptance, technical, questions)
   Q: Action? → Approve/Update/Add Questions/Keep Draft
        ↓
   Status: draft → approved
        ↓
/craft:do "implement feature"
        ↓
   Detects spec → "Found spec. Review/Implement/Skip?"
        ↓
/workflow:done
        ↓
   Q: Archive spec? → Yes (moves to _archive/)
```

---

## Spec Template Sections

- **Overview** - 1-2 sentence summary
- **User Stories** - Primary + secondary with acceptance criteria
- **Technical Requirements** - Architecture, API, data models, dependencies
- **UI/UX Specifications** - Wireframes, flows, accessibility
- **Open Questions** - Track decisions
- **Review Checklist** - Validation before approval

---

## Test Results (This Session)

| Test | Result |
|------|--------|
| Brainstorm with `--save-spec` | ✅ Created spec |
| Spec directory creation | ✅ `docs/specs/` + `_archive/` |
| User type question flow | ✅ Developer selected |
| Spec review validation | ✅ 5 checks run |
| Add questions flow | ✅ 2 questions added |
| Resolve questions Q&A | ✅ 3 questions resolved |
| Approve spec | ✅ Status updated |

---

## Commits

| Repo | Commit | Description |
|------|--------|-------------|
| claude-plugins | `59e790c` | `feat(workflow): add spec capture and review workflow` |

---

## Files Changed in aiterm (Test)

```
docs/specs/
├── _archive/                              # For completed specs
└── SPEC-dark-mode-toggle-2025-12-30.md   # Test spec (approved)

BRAINSTORM-dark-mode-toggle-2025-12-30.md  # Test brainstorm
```

---

## Next Steps

1. Register `/spec:review` in plugin command registry
2. Consider simplifying `--save-spec` syntax
3. Add command shortcuts/aliases
