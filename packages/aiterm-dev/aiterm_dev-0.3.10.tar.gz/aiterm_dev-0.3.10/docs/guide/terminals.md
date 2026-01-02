# Terminal Emulators Guide

**aiterm** supports multiple terminal emulators for AI-assisted development workflows.

---

## Supported Terminals

| Terminal | macOS | Linux | Windows | aiterm Support |
|----------|-------|-------|---------|----------------|
| **iTerm2** | ✅ | - | - | Full (profiles, badge, status) |
| **Ghostty** | ✅ | ✅ | - | Full (v0.3.9+) |
| **Kitty** | ✅ | ✅ | - | Basic |
| **Alacritty** | ✅ | ✅ | ✅ | Basic |
| **WezTerm** | ✅ | ✅ | ✅ | Good |

---

## Quick Start

```bash
# Check which terminals are installed
ait terminals list

# Detect your current terminal
ait terminals detect

# See features for a specific terminal
ait terminals features ghostty
```

---

## Ghostty Support (v0.3.9+)

[Ghostty](https://ghostty.org/) is a fast, native terminal emulator built with Zig. aiterm provides full support for Ghostty.

### Detection

aiterm detects Ghostty via:
- `GHOSTTY_RESOURCES_DIR` environment variable
- `ghostty --version` command output

```bash
$ ait terminals detect
Terminal Detection

✓ Detected: ghostty
  Version: Ghostty 1.2.3
  Channel: stable
  Features: tab_title, themes, native_ui
```

### Features

| Feature | Support | Notes |
|---------|---------|-------|
| Tab Title | ✅ | Via escape sequences |
| Themes | ✅ | Built-in theme support |
| Native UI | ✅ | macOS native look |
| Profiles | ❌ | Not supported by Ghostty |
| Badge | ❌ | Not supported by Ghostty |

### Configuration

Ghostty configuration lives at:

```
~/.config/ghostty/config
```

**Example aiterm-friendly config:**

```ini
# ~/.config/ghostty/config

# Enable title changes from applications
window-title-format = "%t"

# Theme (optional)
theme = dracula

# Font
font-family = "JetBrains Mono"
font-size = 14

# Window
window-padding-x = 10
window-padding-y = 10
```

### Setting Tab Title

```bash
# Set tab title (works in Ghostty)
ait terminals title "Working on aiterm"
```

---

## iTerm2 Support

[iTerm2](https://iterm2.com/) is the most feature-rich terminal for macOS. aiterm provides full integration.

### Features

| Feature | Support | Notes |
|---------|---------|-------|
| Profiles | ✅ | Full profile switching |
| Tab Title | ✅ | Via escape sequences |
| Badge | ✅ | Status badges |
| Status Bar | ✅ | User-defined variables |
| Themes | ✅ | Color presets |

### Profile Switching

```bash
# Switch to a named profile
ait terminals profile "Python-Dev"

# Or use context-based switching
ait switch  # Automatically selects profile based on directory
```

### Recommended Profiles

Create these profiles in iTerm2 Preferences for automatic context switching:

| Profile | Color | Use Case |
|---------|-------|----------|
| `Default` | Blue | General development |
| `Python-Dev` | Green | Python projects |
| `R-Dev` | Purple | R package development |
| `Node-Dev` | Yellow | Node.js projects |
| `Production` | **Red** | Production environments |
| `AI-Session` | Cyan | Claude/Gemini sessions |

---

## WezTerm Support

[WezTerm](https://wezfurlong.org/wezterm/) is a GPU-accelerated terminal with Lua configuration.

### Features

| Feature | Support | Notes |
|---------|---------|-------|
| Tab Title | ✅ | Via escape sequences |
| Themes | ✅ | Color schemes |
| Lua Config | ✅ | Full scripting |
| Multiplexing | ✅ | Built-in tmux-like |

### Configuration

WezTerm config lives at `~/.wezterm.lua`:

```lua
-- ~/.wezterm.lua
local wezterm = require 'wezterm'
local config = {}

-- Allow aiterm to set tab title
config.window_title = 'WezTerm'

-- Theme
config.color_scheme = 'Dracula'

-- Font
config.font = wezterm.font 'JetBrains Mono'
config.font_size = 14.0

return config
```

---

## Kitty Support

[Kitty](https://sw.kovidgoyal.net/kitty/) is a fast, GPU-accelerated terminal.

### Features

| Feature | Support | Notes |
|---------|---------|-------|
| Tab Title | ✅ | Via escape sequences |
| Themes | ✅ | Via kitty-themes |
| Kittens | ✅ | Plugin system |

### Configuration

```ini
# ~/.config/kitty/kitty.conf

# Allow aiterm to set window title
allow_remote_control yes

# Theme
include ~/.config/kitty/themes/dracula.conf

# Font
font_family JetBrains Mono
font_size 14.0
```

---

## Alacritty Support

[Alacritty](https://alacritty.org/) is a minimalist, cross-platform terminal.

### Features

| Feature | Support | Notes |
|---------|---------|-------|
| Tab Title | ✅ | Via escape sequences |
| Themes | ✅ | TOML config |
| Profiles | ❌ | Single config only |

### Configuration

```toml
# ~/.config/alacritty/alacritty.toml

[window]
title = "Alacritty"
dynamic_title = true

[font]
size = 14.0

[font.normal]
family = "JetBrains Mono"
```

---

## Feature Comparison

Run `ait terminals compare` for a live comparison:

```
                    Terminal Feature Comparison
┏━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━┓
┃ Terminal  ┃ Profiles ┃ Tab Title ┃ Badge ┃ Themes ┃ Native UI ┃
┡━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━┩
│ iTerm2    │    ✓     │     ✓     │   ✓   │   ✓    │     ✓     │
│ Kitty     │    ✓     │     ✓     │   ✗   │   ✓    │     ✗     │
│ Alacritty │    ✗     │     ✓     │   ✗   │   ✓    │     ✗     │
│ WezTerm   │    ✓     │     ✓     │   ✗   │   ✓    │     ✓     │
│ Ghostty   │    ✗     │     ✓     │   ✗   │   ✓    │     ✓     │
└───────────┴──────────┴───────────┴───────┴────────┴───────────┘
```

---

## Choosing a Terminal

### For AI-Assisted Development

**Recommended: iTerm2 or Ghostty**

- **iTerm2** - Best for profile-based context switching, status bar integration
- **Ghostty** - Best for performance, native macOS feel, simplicity

### For Cross-Platform

**Recommended: WezTerm**

- Works on macOS, Linux, Windows
- Lua scripting for customization
- Good performance

### For Minimalism

**Recommended: Alacritty or Ghostty**

- Simple configuration
- Fast startup
- Low resource usage

---

## Troubleshooting

### Terminal Not Detected

```bash
# Check what aiterm sees
ait terminals detect

# If wrong terminal detected, check environment
echo $TERM_PROGRAM
echo $GHOSTTY_RESOURCES_DIR
```

### Tab Title Not Changing

Some terminals require configuration to allow title changes:

**Ghostty:** Should work by default

**iTerm2:** Preferences → Profiles → Terminal → "Applications in terminal may change the title"

**Kitty:** Add `allow_remote_control yes` to config

**WezTerm:** Should work by default

### Profile Not Switching (iTerm2)

1. Ensure the profile exists in iTerm2 Preferences
2. Check profile name matches exactly (case-sensitive)
3. Try running manually: `ait terminals profile "ProfileName"`

---

## Next Steps

- **Context Detection:** [How aiterm detects project types](context-detection.md)
- **Profile Configuration:** [Setting up profiles](profiles.md)
- **Workflows:** [Development workflows](workflows.md)
