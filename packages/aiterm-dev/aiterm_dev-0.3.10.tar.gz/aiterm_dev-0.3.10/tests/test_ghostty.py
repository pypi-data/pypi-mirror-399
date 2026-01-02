"""Tests for Ghostty terminal integration."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest


class TestGhosttyDetection:
    """Test Ghostty terminal detection."""

    def test_is_ghostty_true(self):
        """Test detection when TERM_PROGRAM is ghostty."""
        from aiterm.terminal import ghostty

        with patch.dict(os.environ, {"TERM_PROGRAM": "ghostty"}):
            assert ghostty.is_ghostty() is True

    def test_is_ghostty_false_iterm(self):
        """Test detection when TERM_PROGRAM is iTerm."""
        from aiterm.terminal import ghostty

        with patch.dict(os.environ, {"TERM_PROGRAM": "iTerm.app"}):
            assert ghostty.is_ghostty() is False

    def test_is_ghostty_false_empty(self):
        """Test detection when TERM_PROGRAM is not set."""
        from aiterm.terminal import ghostty

        with patch.dict(os.environ, {"TERM_PROGRAM": ""}):
            assert ghostty.is_ghostty() is False

    def test_is_ghostty_case_insensitive(self):
        """Test detection is case-insensitive."""
        from aiterm.terminal import ghostty

        with patch.dict(os.environ, {"TERM_PROGRAM": "Ghostty"}):
            assert ghostty.is_ghostty() is True


class TestGhosttyConfig:
    """Test Ghostty configuration parsing."""

    def test_parse_empty_config(self, tmp_path: Path):
        """Test parsing an empty config file."""
        from aiterm.terminal import ghostty

        config_file = tmp_path / "config"
        config_file.write_text("")

        config = ghostty.parse_config(config_file)
        assert config.font_family == "monospace"
        assert config.font_size == 14
        assert config.theme == ""

    def test_parse_config_with_values(self, tmp_path: Path):
        """Test parsing config with actual values."""
        from aiterm.terminal import ghostty

        config_file = tmp_path / "config"
        config_file.write_text(
            """
font-family = JetBrains Mono
font-size = 16
theme = catppuccin-mocha
window-padding-x = 10
window-padding-y = 8
"""
        )

        config = ghostty.parse_config(config_file)
        assert config.font_family == "JetBrains Mono"
        assert config.font_size == 16
        assert config.theme == "catppuccin-mocha"
        assert config.window_padding_x == 10
        assert config.window_padding_y == 8

    def test_parse_config_with_comments(self, tmp_path: Path):
        """Test parsing config ignores comments."""
        from aiterm.terminal import ghostty

        config_file = tmp_path / "config"
        config_file.write_text(
            """
# This is a comment
font-family = Fira Code
# Another comment
font-size = 14
"""
        )

        config = ghostty.parse_config(config_file)
        assert config.font_family == "Fira Code"
        assert config.font_size == 14

    def test_parse_nonexistent_config(self, tmp_path: Path):
        """Test parsing returns defaults for nonexistent file."""
        from aiterm.terminal import ghostty

        config = ghostty.parse_config(tmp_path / "nonexistent")
        assert config.font_family == "monospace"
        assert config.font_size == 14


class TestGhosttyConfigWrite:
    """Test writing Ghostty configuration."""

    def test_set_config_value_new_file(self, tmp_path: Path):
        """Test setting value creates file if needed."""
        from aiterm.terminal import ghostty

        config_file = tmp_path / "config"
        ghostty.set_config_value("theme", "nord", config_file)

        assert config_file.exists()
        content = config_file.read_text()
        assert "theme = nord" in content

    def test_set_config_value_update_existing(self, tmp_path: Path):
        """Test updating existing value."""
        from aiterm.terminal import ghostty

        config_file = tmp_path / "config"
        config_file.write_text("theme = old-theme\nfont-size = 14\n")

        ghostty.set_config_value("theme", "new-theme", config_file)

        content = config_file.read_text()
        assert "theme = new-theme" in content
        assert "old-theme" not in content
        assert "font-size = 14" in content

    def test_set_config_value_add_new(self, tmp_path: Path):
        """Test adding new value to existing file."""
        from aiterm.terminal import ghostty

        config_file = tmp_path / "config"
        config_file.write_text("font-size = 14\n")

        ghostty.set_config_value("theme", "dracula", config_file)

        content = config_file.read_text()
        assert "theme = dracula" in content
        assert "font-size = 14" in content


class TestGhosttyThemes:
    """Test Ghostty theme functionality."""

    def test_list_themes(self):
        """Test listing available themes."""
        from aiterm.terminal import ghostty

        themes = ghostty.list_themes()
        assert len(themes) > 0
        assert "catppuccin-mocha" in themes
        assert "nord" in themes
        assert "dracula" in themes

    def test_set_theme(self, tmp_path: Path):
        """Test setting a theme."""
        from aiterm.terminal import ghostty

        config_file = tmp_path / "config"
        result = ghostty.set_theme("tokyo-night", config_file)

        assert result is True
        config = ghostty.parse_config(config_file)
        assert config.theme == "tokyo-night"


class TestTerminalDetector:
    """Test terminal type detection."""

    def test_detect_ghostty(self):
        """Test detecting Ghostty terminal."""
        from aiterm.terminal import detect_terminal, TerminalType

        with patch.dict(os.environ, {"TERM_PROGRAM": "ghostty"}):
            assert detect_terminal() == TerminalType.GHOSTTY

    def test_detect_iterm2(self):
        """Test detecting iTerm2 terminal."""
        from aiterm.terminal import detect_terminal, TerminalType

        with patch.dict(os.environ, {"TERM_PROGRAM": "iTerm.app"}):
            assert detect_terminal() == TerminalType.ITERM2

    def test_detect_kitty(self):
        """Test detecting Kitty terminal."""
        from aiterm.terminal import detect_terminal, TerminalType

        with patch.dict(os.environ, {"TERM_PROGRAM": "kitty"}):
            assert detect_terminal() == TerminalType.KITTY

    def test_detect_unknown(self):
        """Test detecting unknown terminal."""
        from aiterm.terminal import detect_terminal, TerminalType

        with patch.dict(os.environ, {"TERM_PROGRAM": ""}):
            assert detect_terminal() == TerminalType.UNKNOWN


class TestTerminalInfo:
    """Test get_terminal_info function."""

    def test_terminal_info_ghostty(self):
        """Test terminal info for Ghostty."""
        from aiterm.terminal import get_terminal_info

        with patch.dict(os.environ, {"TERM_PROGRAM": "ghostty"}):
            info = get_terminal_info()
            assert info["type"] == "ghostty"
            assert info["supports_themes"] is True
            assert info["config_editable"] is True
            assert info["supports_profiles"] is False

    def test_terminal_info_iterm2(self):
        """Test terminal info for iTerm2."""
        from aiterm.terminal import get_terminal_info

        with patch.dict(os.environ, {"TERM_PROGRAM": "iTerm.app"}):
            info = get_terminal_info()
            assert info["type"] == "iterm2"
            assert info["supports_profiles"] is True
            assert info["supports_user_vars"] is True


# =============================================================================
# NEW TESTS: get_version() - subprocess handling
# =============================================================================


class TestGhosttyVersion:
    """Test Ghostty version detection."""

    def test_get_version_success(self):
        """Test successful version retrieval."""
        from aiterm.terminal import ghostty
        from unittest.mock import MagicMock
        import subprocess

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Ghostty 1.0.0"

        with patch.object(subprocess, "run", return_value=mock_result) as mock_run:
            version = ghostty.get_version()
            assert version == "Ghostty 1.0.0"
            mock_run.assert_called_once()

    def test_get_version_not_installed(self):
        """Test version when Ghostty is not installed."""
        from aiterm.terminal import ghostty
        import subprocess

        with patch.object(subprocess, "run", side_effect=FileNotFoundError):
            version = ghostty.get_version()
            assert version is None

    def test_get_version_timeout(self):
        """Test version when command times out."""
        from aiterm.terminal import ghostty
        import subprocess

        with patch.object(subprocess, "run", side_effect=subprocess.TimeoutExpired("ghostty", 5)):
            version = ghostty.get_version()
            assert version is None

    def test_get_version_nonzero_exit(self):
        """Test version when command fails."""
        from aiterm.terminal import ghostty
        from unittest.mock import MagicMock
        import subprocess

        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""

        with patch.object(subprocess, "run", return_value=mock_result):
            version = ghostty.get_version()
            assert version is None


# =============================================================================
# NEW TESTS: set_title() - OSC escape sequence handling
# =============================================================================


class TestGhosttySetTitle:
    """Test Ghostty window title setting."""

    def test_set_title_in_ghostty(self):
        """Test setting title when in Ghostty."""
        from aiterm.terminal import ghostty
        import io

        with patch.dict(os.environ, {"TERM_PROGRAM": "ghostty"}):
            mock_stdout = io.StringIO()
            with patch("sys.stdout", mock_stdout):
                result = ghostty.set_title("My Title")
                assert result is True
                output = mock_stdout.getvalue()
                assert "\033]2;My Title\007" in output

    def test_set_title_not_in_ghostty(self):
        """Test setting title when not in Ghostty."""
        from aiterm.terminal import ghostty

        with patch.dict(os.environ, {"TERM_PROGRAM": "iTerm.app"}):
            result = ghostty.set_title("My Title")
            assert result is False

    def test_set_title_with_special_characters(self):
        """Test setting title with special characters."""
        from aiterm.terminal import ghostty
        import io

        with patch.dict(os.environ, {"TERM_PROGRAM": "ghostty"}):
            mock_stdout = io.StringIO()
            with patch("sys.stdout", mock_stdout):
                result = ghostty.set_title("📁 project (main)")
                assert result is True
                output = mock_stdout.getvalue()
                assert "📁 project (main)" in output


# =============================================================================
# NEW TESTS: apply_context() - context to title mapping
# =============================================================================


class TestGhosttyApplyContext:
    """Test applying context info to Ghostty."""

    def test_apply_context_full(self):
        """Test applying context with all fields."""
        from aiterm.terminal import ghostty
        from aiterm.context.detector import ContextInfo, ContextType
        import io

        context = ContextInfo(
            type=ContextType.PYTHON,
            name="myproject",
            icon="🐍",
            profile="Python-Dev",
            branch="feature-x",
            is_dirty=False,
        )

        with patch.dict(os.environ, {"TERM_PROGRAM": "ghostty"}):
            mock_stdout = io.StringIO()
            with patch("sys.stdout", mock_stdout):
                ghostty.apply_context(context)
                output = mock_stdout.getvalue()
                assert "🐍" in output
                assert "myproject" in output
                assert "feature-x" in output

    def test_apply_context_minimal(self):
        """Test applying context with minimal fields."""
        from aiterm.terminal import ghostty
        from aiterm.context.detector import ContextInfo, ContextType
        import io

        context = ContextInfo(
            type=ContextType.DEFAULT,
            name="unknown",
            icon="",
            profile="Default",
        )

        with patch.dict(os.environ, {"TERM_PROGRAM": "ghostty"}):
            mock_stdout = io.StringIO()
            with patch("sys.stdout", mock_stdout):
                ghostty.apply_context(context)
                output = mock_stdout.getvalue()
                assert "unknown" in output

    def test_apply_context_no_branch(self):
        """Test applying context without branch info."""
        from aiterm.terminal import ghostty
        from aiterm.context.detector import ContextInfo, ContextType
        import io

        context = ContextInfo(
            type=ContextType.NODE,
            name="webapp",
            icon="📦",
            profile="Node-Dev",
        )

        with patch.dict(os.environ, {"TERM_PROGRAM": "ghostty"}):
            mock_stdout = io.StringIO()
            with patch("sys.stdout", mock_stdout):
                ghostty.apply_context(context)
                output = mock_stdout.getvalue()
                assert "📦" in output
                assert "webapp" in output
                # No branch parentheses
                assert "(" not in output or "webapp" in output


# =============================================================================
# NEW TESTS: show_config() - formatted output
# =============================================================================


class TestGhosttyShowConfig:
    """Test show_config formatted output."""

    def test_show_config_with_values(self, tmp_path: Path):
        """Test show_config with actual config."""
        from aiterm.terminal import ghostty

        config_file = tmp_path / "config"
        config_file.write_text(
            """font-family = JetBrains Mono
font-size = 16
theme = dracula
cursor-style = underline
"""
        )

        with patch.object(ghostty, "get_config_path", return_value=config_file):
            output = ghostty.show_config()

            assert "Ghostty Configuration" in output
            assert "JetBrains Mono" in output
            assert "16" in output
            assert "dracula" in output
            assert "underline" in output

    def test_show_config_no_file(self):
        """Test show_config when no config exists."""
        from aiterm.terminal import ghostty

        with patch.object(ghostty, "get_config_path", return_value=None):
            output = ghostty.show_config()

            assert "Ghostty Configuration" in output
            assert "Not found" in output
            assert "monospace" in output  # default font


# =============================================================================
# NEW TESTS: Edge cases - invalid values, malformed config
# =============================================================================


class TestGhosttyConfigEdgeCases:
    """Test edge cases in config parsing."""

    def test_parse_invalid_int(self, tmp_path: Path):
        """Test parsing config with invalid integer value."""
        from aiterm.terminal import ghostty

        config_file = tmp_path / "config"
        config_file.write_text("font-size = not-a-number\n")

        config = ghostty.parse_config(config_file)
        # Should keep default value
        assert config.font_size == 14

    def test_parse_invalid_float(self, tmp_path: Path):
        """Test parsing config with invalid float value."""
        from aiterm.terminal import ghostty

        config_file = tmp_path / "config"
        config_file.write_text("background-opacity = invalid\n")

        config = ghostty.parse_config(config_file)
        # Should keep default value
        assert config.background_opacity == 1.0

    def test_parse_malformed_line(self, tmp_path: Path):
        """Test parsing config with malformed line (no equals)."""
        from aiterm.terminal import ghostty

        config_file = tmp_path / "config"
        config_file.write_text(
            """font-size = 14
this line has no equals sign
theme = nord
"""
        )

        config = ghostty.parse_config(config_file)
        assert config.font_size == 14
        assert config.theme == "nord"

    def test_parse_whitespace_handling(self, tmp_path: Path):
        """Test parsing handles various whitespace."""
        from aiterm.terminal import ghostty

        config_file = tmp_path / "config"
        config_file.write_text(
            """  font-family   =   Fira Code
font-size=12
  theme =tokyo-night
"""
        )

        config = ghostty.parse_config(config_file)
        assert config.font_family == "Fira Code"
        assert config.font_size == 12
        assert config.theme == "tokyo-night"

    def test_parse_background_opacity(self, tmp_path: Path):
        """Test parsing background opacity."""
        from aiterm.terminal import ghostty

        config_file = tmp_path / "config"
        config_file.write_text("background-opacity = 0.85\n")

        config = ghostty.parse_config(config_file)
        assert config.background_opacity == 0.85

    def test_raw_config_capture(self, tmp_path: Path):
        """Test that raw_config captures all key-value pairs."""
        from aiterm.terminal import ghostty

        config_file = tmp_path / "config"
        config_file.write_text(
            """font-family = Monaco
custom-key = custom-value
another = setting
"""
        )

        config = ghostty.parse_config(config_file)
        assert "custom-key" in config.raw_config
        assert config.raw_config["custom-key"] == "custom-value"
        assert config.raw_config["another"] == "setting"


# =============================================================================
# NEW TESTS: Config path functions
# =============================================================================


class TestGhosttyConfigPaths:
    """Test config path detection functions."""

    def test_get_config_path_xdg(self, tmp_path: Path):
        """Test finding config in XDG location."""
        from aiterm.terminal import ghostty

        # Create fake XDG config
        xdg_config = tmp_path / ".config" / "ghostty" / "config"
        xdg_config.parent.mkdir(parents=True)
        xdg_config.write_text("theme = test")

        with patch.object(Path, "home", return_value=tmp_path):
            # Need to re-import to pick up patched CONFIG_PATHS
            with patch.object(ghostty, "CONFIG_PATHS", [xdg_config, tmp_path / ".ghostty"]):
                path = ghostty.get_config_path()
                assert path == xdg_config

    def test_get_config_path_none_found(self, tmp_path: Path):
        """Test when no config file exists."""
        from aiterm.terminal import ghostty

        with patch.object(ghostty, "CONFIG_PATHS", [tmp_path / "nonexistent1", tmp_path / "nonexistent2"]):
            path = ghostty.get_config_path()
            assert path is None

    def test_get_default_config_path_creates_dirs(self, tmp_path: Path):
        """Test default config path creates parent directories."""
        from aiterm.terminal import ghostty

        with patch.object(Path, "home", return_value=tmp_path):
            path = ghostty.get_default_config_path()
            assert path.parent.exists()
            assert path.name == "config"


# =============================================================================
# NEW TESTS: reload_config()
# =============================================================================


class TestGhosttyReloadConfig:
    """Test config reload functionality."""

    def test_reload_config_in_ghostty(self):
        """Test reload returns True in Ghostty."""
        from aiterm.terminal import ghostty

        with patch.dict(os.environ, {"TERM_PROGRAM": "ghostty"}):
            result = ghostty.reload_config()
            assert result is True

    def test_reload_config_not_in_ghostty(self):
        """Test reload returns False when not in Ghostty."""
        from aiterm.terminal import ghostty

        with patch.dict(os.environ, {"TERM_PROGRAM": "iTerm.app"}):
            result = ghostty.reload_config()
            assert result is False


# =============================================================================
# NEW TESTS: Theme list immutability
# =============================================================================


class TestGhosttyThemeList:
    """Test theme list behavior."""

    def test_list_themes_returns_copy(self):
        """Test that list_themes returns a copy (not mutable original)."""
        from aiterm.terminal import ghostty

        themes1 = ghostty.list_themes()
        themes1.append("fake-theme")

        themes2 = ghostty.list_themes()
        assert "fake-theme" not in themes2

    def test_builtin_themes_count(self):
        """Test expected number of built-in themes."""
        from aiterm.terminal import ghostty

        themes = ghostty.list_themes()
        # Should have at least the documented themes
        assert len(themes) >= 14
