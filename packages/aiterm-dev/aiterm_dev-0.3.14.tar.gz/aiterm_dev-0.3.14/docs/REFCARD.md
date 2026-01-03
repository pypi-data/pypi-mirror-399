# aiterm Quick Reference

```
┌─────────────────────────────────────────────────────────────┐
│ AITERM v0.3.11 - Terminal Optimizer for AI Development     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ ESSENTIAL                                                   │
│ ──────────                                                  │
│ ait doctor              Check installation                  │
│ ait detect              Show project context                │
│ ait switch              Apply context to terminal           │
│ ait hello               Diagnostic greeting                 │
│ ait info                System diagnostics (--json)         │
│                                                             │
│ CONFIGURATION (NEW in v0.3.11)                              │
│ ──────────────────────────────                              │
│ ait config path         Show config directory               │
│ ait config path --all   Show all paths with status          │
│ ait config show         Display current configuration       │
│ ait config init         Create default config.toml          │
│ ait config edit         Open config in $EDITOR              │
│                                                             │
│ CLAUDE CODE                                                 │
│ ──────────                                                  │
│ ait claude settings     View current settings               │
│ ait claude backup       Backup settings file                │
│ ait claude approvals    Manage auto-approvals               │
│   approvals list        Show current approvals              │
│   approvals add <cmd>   Add approval rule                   │
│   approvals preset      Apply preset (safe/moderate/full)   │
│                                                             │
│ CONTEXT DETECTION                                           │
│ ─────────────────                                           │
│ ait context detect      Detect project type                 │
│ ait context show        Alias for detect                    │
│ ait context apply       Apply profile to terminal           │
│                                                             │
│ PROFILES                                                    │
│ ─────────                                                   │
│ ait profile list        List available profiles             │
│ ait profile show        Show current profile                │
│                                                             │
│ MCP SERVERS                                                 │
│ ───────────                                                 │
│ ait mcp list            List configured servers             │
│ ait mcp status          Check server health                 │
│ ait mcp test <name>     Test specific server                │
│                                                             │
│ HOOKS & COMMANDS                                            │
│ ────────────────                                            │
│ ait hooks list          List installed hooks                │
│ ait commands list       List command templates              │
│                                                             │
│ DOCUMENTATION                                               │
│ ─────────────                                               │
│ ait docs check          Validate documentation              │
│ ait docs serve          Preview docs locally                │
│                                                             │
│ TERMINALS                                                   │
│ ─────────                                                   │
│ ait terminals list      List supported terminals            │
│ ait terminals detect    Detect current terminal             │
│ ait terminals features  Show terminal features              │
│ ait terminals compare   Compare terminal capabilities       │
│                                                             │
│ GHOSTTY (v0.3.9+)                                           │
│ ─────────────────                                           │
│ ait ghostty status      Show Ghostty configuration          │
│ ait ghostty config      Display config file location        │
│ ait ghostty theme       List or set themes (14 built-in)    │
│ ait ghostty font        Get or set font configuration       │
│ ait ghostty set         Set any config value                │
│                                                             │
│ FLOW-CLI INTEGRATION (v0.3.10+)                             │
│ ───────────────────────────────                             │
│ tm title <text>         Set tab title (instant)             │
│ tm profile <name>       Switch iTerm2 profile               │
│ tm which                Show detected terminal              │
│ tm detect               Detect project context              │
│ tm switch               Apply context to terminal           │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ COMMON WORKFLOWS                                            │
│ ────────────────                                            │
│                                                             │
│ Quick install:                                              │
│   curl -fsSL .../install.sh | bash                          │
│                                                             │
│ First-time setup:                                           │
│   ait doctor && ait config init                             │
│                                                             │
│ Switch context when entering project:                       │
│   cd ~/my-project && ait switch                             │
│                                                             │
│ Backup before changes:                                      │
│   ait claude backup && ait claude approvals preset safe     │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ SHELL ALIASES                                               │
│ ─────────────                                               │
│ ait          aiterm (main CLI)                              │
│ oc           opencode (OpenCode CLI)                        │
│ tm           terminal manager (flow-cli dispatcher)         │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ CONFIG LOCATIONS                                            │
│ ────────────────                                            │
│ ~/.config/aiterm/config.toml    aiterm config (v0.3.11+)    │
│ ~/.claude/settings.json         Claude Code settings        │
│ ~/.config/opencode/config.json  OpenCode settings           │
│ ~/.config/ghostty/config        Ghostty terminal config     │
│                                                             │
│ Environment: AITERM_CONFIG_HOME overrides config path       │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ Docs: https://data-wise.github.io/aiterm/                   │
│ Repo: https://github.com/Data-Wise/aiterm                   │
└─────────────────────────────────────────────────────────────┘
```

## Domain-Specific Reference Cards

| Topic | File |
|-------|------|
| Claude Code | [REFCARD-CLAUDE.md](reference/REFCARD-CLAUDE.md) |
| MCP Servers | [REFCARD-MCP.md](reference/REFCARD-MCP.md) |
| Hooks | [REFCARD-HOOKS.md](reference/REFCARD-HOOKS.md) |
| Context Detection | [REFCARD-CONTEXT.md](reference/REFCARD-CONTEXT.md) |
| OpenCode | [REFCARD-OPENCODE.md](reference/REFCARD-OPENCODE.md) |

## Print Version

For a printer-friendly version without markdown formatting:

```bash
# Print to terminal
ait --help

# Save to file
ait --help > aiterm-help.txt
```
