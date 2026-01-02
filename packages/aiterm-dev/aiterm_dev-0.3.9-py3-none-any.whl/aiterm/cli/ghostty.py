"""Ghostty terminal management commands."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

app = typer.Typer(
    help="Ghostty terminal management commands.",
    no_args_is_help=True,
)

console = Console()


@app.command(
    "status",
    epilog="""
[bold]Examples:[/]
  ait ghostty status      # Check if running in Ghostty
""",
)
def ghostty_status() -> None:
    """Check Ghostty detection and status."""
    from aiterm.terminal import ghostty, detect_terminal, TerminalType

    terminal = detect_terminal()
    is_ghostty = terminal == TerminalType.GHOSTTY

    table = Table(title="Ghostty Status", show_header=False, border_style="cyan")
    table.add_column("Field", style="bold")
    table.add_column("Value")

    table.add_row("Detected Terminal", terminal.value)
    table.add_row(
        "Running in Ghostty",
        "[green]Yes[/]" if is_ghostty else "[dim]No[/]",
    )

    # Get version if available
    version = ghostty.get_version()
    if version:
        table.add_row("Ghostty Version", version)

    # Check config
    config_path = ghostty.get_config_path()
    if config_path:
        table.add_row("Config File", str(config_path))
    else:
        table.add_row("Config File", "[dim]Not found[/]")

    console.print(table)


@app.command(
    "config",
    epilog="""
[bold]Examples:[/]
  ait ghostty config         # Show current config
  ait ghostty config --edit  # Open config in editor
""",
)
def ghostty_config(
    edit: bool = typer.Option(
        False,
        "--edit",
        "-e",
        help="Open config file in editor.",
    ),
) -> None:
    """Show or edit Ghostty configuration."""
    from aiterm.terminal import ghostty
    import os
    import subprocess

    config_path = ghostty.get_config_path()

    if edit:
        if not config_path:
            # Create default config path
            config_path = ghostty.get_default_config_path()
            if not config_path.exists():
                config_path.touch()
                console.print(f"[green]Created[/] {config_path}")

        editor = os.environ.get("EDITOR", "vim")
        console.print(f"[dim]Opening in {editor}...[/]")
        subprocess.run([editor, str(config_path)])
        return

    if not config_path or not config_path.exists():
        console.print("[yellow]No Ghostty config found.[/]")
        console.print(f"[dim]Create one at: ~/.config/ghostty/config[/]")
        return

    config = ghostty.parse_config(config_path)

    console.print(
        Panel(
            f"[bold]Config:[/] {config_path}",
            title="Ghostty Configuration",
            border_style="cyan",
        )
    )

    table = Table(show_header=True, border_style="dim")
    table.add_column("Setting", style="bold")
    table.add_column("Value")

    table.add_row("Font", f"{config.font_family} @ {config.font_size}pt")
    table.add_row("Theme", config.theme or "[dim](default)[/]")
    table.add_row("Padding", f"x={config.window_padding_x}, y={config.window_padding_y}")
    table.add_row("Opacity", str(config.background_opacity))
    table.add_row("Cursor", config.cursor_style)

    console.print(table)

    # Show raw config if there are extra values
    extra_keys = set(config.raw_config.keys()) - {
        "font-family",
        "font-size",
        "theme",
        "window-padding-x",
        "window-padding-y",
        "background-opacity",
        "cursor-style",
    }
    if extra_keys:
        console.print("\n[bold]Other settings:[/]")
        for key in sorted(extra_keys):
            console.print(f"  {key} = {config.raw_config[key]}")


# Theme sub-commands
theme_app = typer.Typer(help="Theme management for Ghostty.")
app.add_typer(theme_app, name="theme")


@theme_app.command(
    "list",
    epilog="""
[bold]Examples:[/]
  ait ghostty theme list   # Show available themes
""",
)
def theme_list() -> None:
    """List available Ghostty themes."""
    from aiterm.terminal import ghostty

    themes = ghostty.list_themes()
    current_config = ghostty.parse_config()
    current_theme = current_config.theme

    console.print("[bold cyan]Available Ghostty Themes[/]\n")

    table = Table(show_header=True, border_style="dim")
    table.add_column("Theme", style="bold")
    table.add_column("Status")

    for theme in themes:
        if theme == current_theme:
            table.add_row(theme, "[green]● active[/]")
        else:
            table.add_row(theme, "[dim]○[/]")

    console.print(table)
    console.print(f"\n[dim]Total: {len(themes)} built-in themes[/]")
    console.print("[dim]Use 'ait ghostty theme apply <name>' to change theme[/]")


@theme_app.command(
    "apply",
    epilog="""
[bold]Examples:[/]
  ait ghostty theme apply catppuccin-mocha   # Apply theme
  ait ghostty theme apply nord               # Switch to Nord
""",
)
def theme_apply(
    theme_name: str = typer.Argument(..., help="Name of theme to apply."),
) -> None:
    """Apply a theme to Ghostty."""
    from aiterm.terminal import ghostty

    # Validate theme exists (or allow custom)
    builtin_themes = ghostty.list_themes()
    is_builtin = theme_name in builtin_themes

    if ghostty.set_theme(theme_name):
        console.print(f"[green]✓[/] Theme set to: [bold]{theme_name}[/]")
        if not is_builtin:
            console.print("[yellow]Note: This is not a built-in theme.[/]")
        console.print("[dim]Ghostty will auto-reload the config.[/]")
    else:
        console.print("[red]Failed to set theme.[/]")
        raise typer.Exit(1)


@theme_app.command(
    "show",
    epilog="""
[bold]Examples:[/]
  ait ghostty theme show   # Show current theme
""",
)
def theme_show() -> None:
    """Show currently active theme."""
    from aiterm.terminal import ghostty

    config = ghostty.parse_config()

    if config.theme:
        console.print(f"[bold]Current theme:[/] {config.theme}")
    else:
        console.print("[dim]No theme set (using Ghostty defaults)[/]")


# Font sub-commands
font_app = typer.Typer(help="Font settings for Ghostty.")
app.add_typer(font_app, name="font")


@font_app.command(
    "show",
    epilog="""
[bold]Examples:[/]
  ait ghostty font show   # Show current font settings
""",
)
def font_show() -> None:
    """Show current font settings."""
    from aiterm.terminal import ghostty

    config = ghostty.parse_config()
    console.print(f"[bold]Font:[/] {config.font_family} @ {config.font_size}pt")


@font_app.command(
    "set",
    epilog="""
[bold]Examples:[/]
  ait ghostty font set "JetBrains Mono"        # Set font family
  ait ghostty font set "Fira Code" --size 16   # Set font and size
""",
)
def font_set(
    font_family: str = typer.Argument(..., help="Font family name."),
    size: Optional[int] = typer.Option(
        None,
        "--size",
        "-s",
        help="Font size in points.",
    ),
) -> None:
    """Set font family and optionally size."""
    from aiterm.terminal import ghostty

    success = ghostty.set_config_value("font-family", font_family)
    if success:
        console.print(f"[green]✓[/] Font family: {font_family}")
    else:
        console.print("[red]Failed to set font family.[/]")
        raise typer.Exit(1)

    if size:
        success = ghostty.set_config_value("font-size", str(size))
        if success:
            console.print(f"[green]✓[/] Font size: {size}pt")
        else:
            console.print("[red]Failed to set font size.[/]")
            raise typer.Exit(1)

    console.print("[dim]Ghostty will auto-reload the config.[/]")


@app.command(
    "set",
    epilog="""
[bold]Examples:[/]
  ait ghostty set background-opacity 0.9      # Set opacity
  ait ghostty set window-padding-x 10         # Set padding
  ait ghostty set cursor-style bar            # Set cursor
""",
)
def ghostty_set(
    key: str = typer.Argument(..., help="Configuration key."),
    value: str = typer.Argument(..., help="Value to set."),
) -> None:
    """Set a Ghostty configuration value."""
    from aiterm.terminal import ghostty

    if ghostty.set_config_value(key, value):
        console.print(f"[green]✓[/] Set {key} = {value}")
        console.print("[dim]Ghostty will auto-reload the config.[/]")
    else:
        console.print(f"[red]Failed to set {key}.[/]")
        raise typer.Exit(1)
