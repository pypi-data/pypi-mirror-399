"""Ghostty terminal integration.

Provides configuration management and theme switching for Ghostty terminal.
Ghostty is a GPU-accelerated terminal emulator by Mitchell Hashimoto.

Key differences from iTerm2:
- Config file: ~/.config/ghostty/config (plain text, not JSON)
- No runtime profile switching via escape sequences
- Changes require config reload (Cmd+Shift+,) or restart
- Themes are applied by modifying config file
"""

import os
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from aiterm.context.detector import ContextInfo


@dataclass
class GhosttyConfig:
    """Parsed Ghostty configuration."""

    font_family: str = "monospace"
    font_size: int = 14
    theme: str = ""
    window_padding_x: int = 0
    window_padding_y: int = 0
    background_opacity: float = 1.0
    cursor_style: str = "block"
    raw_config: dict = field(default_factory=dict)


# Standard config locations
CONFIG_PATHS = [
    Path.home() / ".config" / "ghostty" / "config",
    Path.home() / ".ghostty",
]

# Built-in themes (Ghostty ships with these)
BUILTIN_THEMES = [
    "catppuccin-mocha",
    "catppuccin-latte",
    "catppuccin-frappe",
    "catppuccin-macchiato",
    "dracula",
    "gruvbox-dark",
    "gruvbox-light",
    "nord",
    "solarized-dark",
    "solarized-light",
    "tokyo-night",
    "tokyo-night-storm",
    "one-dark",
    "one-light",
]


def is_ghostty() -> bool:
    """Check if running in Ghostty terminal."""
    return os.environ.get("TERM_PROGRAM", "").lower() == "ghostty"


def get_config_path() -> Optional[Path]:
    """Find the Ghostty config file path.

    Returns:
        Path to config file if found, None otherwise.
    """
    for path in CONFIG_PATHS:
        if path.exists():
            return path
    return None


def get_default_config_path() -> Path:
    """Get the default config path (creates parent dirs if needed)."""
    config_dir = Path.home() / ".config" / "ghostty"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "config"


def parse_config(config_path: Optional[Path] = None) -> GhosttyConfig:
    """Parse Ghostty configuration file.

    Args:
        config_path: Path to config file. Auto-detected if None.

    Returns:
        GhosttyConfig with parsed values.
    """
    config = GhosttyConfig()

    path = config_path or get_config_path()
    if not path or not path.exists():
        return config

    with open(path) as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith("#"):
                continue

            # Parse key = value
            if "=" in line:
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip()

                config.raw_config[key] = value

                # Map known keys
                if key == "font-family":
                    config.font_family = value
                elif key == "font-size":
                    try:
                        config.font_size = int(value)
                    except ValueError:
                        pass
                elif key == "theme":
                    config.theme = value
                elif key == "window-padding-x":
                    try:
                        config.window_padding_x = int(value)
                    except ValueError:
                        pass
                elif key == "window-padding-y":
                    try:
                        config.window_padding_y = int(value)
                    except ValueError:
                        pass
                elif key == "background-opacity":
                    try:
                        config.background_opacity = float(value)
                    except ValueError:
                        pass
                elif key == "cursor-style":
                    config.cursor_style = value

    return config


def set_config_value(key: str, value: str, config_path: Optional[Path] = None) -> bool:
    """Set a configuration value in the Ghostty config file.

    Args:
        key: Configuration key (e.g., "theme", "font-size").
        value: Value to set.
        config_path: Path to config file. Auto-detected if None.

    Returns:
        True if config was updated, False on error.
    """
    path = config_path or get_config_path() or get_default_config_path()

    # Read existing config
    lines = []
    key_found = False

    if path.exists():
        with open(path) as f:
            for line in f:
                stripped = line.strip()
                if stripped.startswith(f"{key} ") or stripped.startswith(f"{key}="):
                    lines.append(f"{key} = {value}\n")
                    key_found = True
                else:
                    lines.append(line)

    # Add new key if not found
    if not key_found:
        if lines and not lines[-1].endswith("\n"):
            lines.append("\n")
        lines.append(f"{key} = {value}\n")

    # Write back
    with open(path, "w") as f:
        f.writelines(lines)

    return True


def set_theme(theme: str, config_path: Optional[Path] = None) -> bool:
    """Set the Ghostty theme.

    Args:
        theme: Theme name (e.g., "catppuccin-mocha").
        config_path: Path to config file. Auto-detected if None.

    Returns:
        True if theme was set, False on error.
    """
    return set_config_value("theme", theme, config_path)


def list_themes() -> list[str]:
    """List available Ghostty themes.

    Returns:
        List of built-in theme names.
    """
    return BUILTIN_THEMES.copy()


def set_title(title: str) -> bool:
    """Set the terminal window title.

    Uses standard OSC 2 escape sequence (works in most terminals).

    Args:
        title: The title to set.

    Returns:
        True if title was set.
    """
    if not is_ghostty():
        return False

    sys.stdout.write(f"\033]2;{title}\007")
    sys.stdout.flush()
    return True


def reload_config() -> bool:
    """Trigger Ghostty config reload.

    Note: Ghostty auto-reloads on config file save, so this is usually
    not needed. This function sends Cmd+Shift+, via AppleScript as fallback.

    Returns:
        True if reload was triggered, False on error.
    """
    if not is_ghostty():
        return False

    # Ghostty auto-reloads on config save, so just return True
    # If we need manual reload, we could use AppleScript:
    # osascript -e 'tell application "Ghostty" to activate'
    # osascript -e 'tell application "System Events" to keystroke "," using {command down, shift down}'
    return True


def apply_context(context: ContextInfo) -> None:
    """Apply a context to Ghostty (title only, no profile switching).

    Ghostty doesn't support runtime profile switching like iTerm2.
    We can only set the window title.

    Args:
        context: The context info to apply.
    """
    # Build title with context info
    title_parts = []
    if context.icon:
        title_parts.append(context.icon)
    if context.name:
        title_parts.append(context.name)
    if context.branch:
        title_parts.append(f"({context.branch})")

    title = " ".join(title_parts) if title_parts else context.title
    set_title(title)


def show_config() -> str:
    """Get a formatted display of current Ghostty config.

    Returns:
        Formatted string showing current configuration.
    """
    config = parse_config()
    path = get_config_path()

    lines = [
        "Ghostty Configuration",
        "=" * 40,
        f"Config file: {path or 'Not found'}",
        "",
        f"Font:       {config.font_family} @ {config.font_size}pt",
        f"Theme:      {config.theme or '(default)'}",
        f"Padding:    x={config.window_padding_x}, y={config.window_padding_y}",
        f"Opacity:    {config.background_opacity}",
        f"Cursor:     {config.cursor_style}",
    ]

    return "\n".join(lines)


def get_version() -> Optional[str]:
    """Get Ghostty version.

    Returns:
        Version string or None if not available.
    """
    try:
        result = subprocess.run(
            ["ghostty", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return None
