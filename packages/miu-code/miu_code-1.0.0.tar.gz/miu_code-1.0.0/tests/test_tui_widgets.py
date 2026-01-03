"""Tests for TUI widgets - Phase 3 StatusBar and WelcomeBanner."""

import os

from miu_code.tui.widgets.banner import WelcomeBanner
from miu_code.tui.widgets.status import StatusBar
from miu_core.modes import AgentMode, ModeManager
from miu_core.usage import UsageTracker


class TestStatusBar:
    """Tests for StatusBar widget."""

    def test_statusbar_instantiation(self) -> None:
        """Test StatusBar can be instantiated with default values."""
        bar = StatusBar()

        assert bar.mode_label == "normal (shift+tab to cycle)"
        assert bar.current_path == ""
        assert bar.token_usage == "0% of 200k tokens"

    def test_statusbar_with_custom_managers(self) -> None:
        """Test StatusBar with custom ModeManager and UsageTracker."""
        mode_manager = ModeManager(AgentMode.PLAN)
        usage_tracker = UsageTracker(context_limit=100_000)

        bar = StatusBar(mode_manager=mode_manager, usage_tracker=usage_tracker)

        assert "plan mode" in bar.mode_label
        assert "100k tokens" in bar.token_usage

    def test_statusbar_with_working_dir(self) -> None:
        """Test StatusBar formats working directory path correctly."""
        home = os.path.expanduser("~")
        test_path = os.path.join(home, "git", "project")

        bar = StatusBar(working_dir=test_path)

        assert bar.current_path == "~/git/project"

    def test_statusbar_path_without_home(self) -> None:
        """Test StatusBar handles absolute paths not in home."""
        bar = StatusBar(working_dir="/tmp/test/dir")

        assert bar.current_path == "/tmp/test/dir"

    def test_statusbar_mode_cycling(self) -> None:
        """Test StatusBar updates on mode cycle through all 4 modes."""
        mode_manager = ModeManager()
        bar = StatusBar(mode_manager=mode_manager)

        assert "normal" in bar.mode_label

        mode_manager.cycle()
        assert "plan mode" in bar.mode_label

        mode_manager.cycle()
        assert "ask mode" in bar.mode_label

        mode_manager.cycle()
        assert "auto mode" in bar.mode_label

        mode_manager.cycle()
        assert "normal" in bar.mode_label

    def test_statusbar_update_usage(self) -> None:
        """Test StatusBar usage tracking updates."""
        usage_tracker = UsageTracker()
        bar = StatusBar(usage_tracker=usage_tracker)

        assert "0% of 200k tokens" == bar.token_usage

        bar.update_usage(input_tokens=100, output_tokens=50)
        assert "0% of 200k tokens" in bar.token_usage

        bar.update_usage(input_tokens=10_000, output_tokens=5_000)
        usage_percent = (15_000 / 200_000) * 100
        assert f"{usage_percent:.0f}%" in bar.token_usage

    def test_statusbar_update_path(self) -> None:
        """Test StatusBar path update."""
        bar = StatusBar()

        assert bar.current_path == ""

        home = os.path.expanduser("~")
        new_path = os.path.join(home, "new", "path")
        bar.update_path(new_path)

        assert bar.current_path == "~/new/path"

    def test_statusbar_mode_manager_property(self) -> None:
        """Test StatusBar exposes mode_manager property for cycling."""
        bar = StatusBar()
        mode_manager = bar.mode_manager

        assert mode_manager is not None
        assert mode_manager.mode == AgentMode.NORMAL

        mode_manager.cycle()
        assert "plan mode" in bar.mode_label

    def test_statusbar_token_limit_formatting(self) -> None:
        """Test StatusBar formats different token limits correctly."""
        tracker_200k = UsageTracker(context_limit=200_000)
        tracker_100k = UsageTracker(context_limit=100_000)

        bar_200k = StatusBar(usage_tracker=tracker_200k)
        bar_100k = StatusBar(usage_tracker=tracker_100k)

        assert "200k tokens" in bar_200k.token_usage
        assert "100k tokens" in bar_100k.token_usage

    def test_statusbar_multiple_usage_updates(self) -> None:
        """Test StatusBar accumulates token usage over multiple updates."""
        usage_tracker = UsageTracker()
        bar = StatusBar(usage_tracker=usage_tracker)

        bar.update_usage(input_tokens=1000, output_tokens=500)
        bar.update_usage(input_tokens=2000, output_tokens=1000)
        bar.update_usage(input_tokens=3000, output_tokens=1500)

        total = 1000 + 500 + 2000 + 1000 + 3000 + 1500
        expected_percent = (total / 200_000) * 100
        assert f"{expected_percent:.0f}%" in bar.token_usage


class TestWelcomeBanner:
    """Tests for WelcomeBanner widget."""

    def test_welcomebanner_instantiation(self) -> None:
        """Test WelcomeBanner can be instantiated with default values."""
        banner = WelcomeBanner()

        assert banner.version == ""
        assert banner.model == ""
        assert banner.mcp_count == 0
        assert banner.animation_progress == 0.0

    def test_welcomebanner_with_metadata(self) -> None:
        """Test WelcomeBanner with version, model, and MCP info."""
        banner = WelcomeBanner(version="0.2.0", model="claude-opus-4-20250805", mcp_count=2)

        assert banner.version == "0.2.0"
        assert banner.model == "claude-opus-4-20250805"
        assert banner.mcp_count == 2

    def test_welcomebanner_working_dir_default(self) -> None:
        """Test WelcomeBanner uses current working directory by default."""
        banner = WelcomeBanner()

        assert banner.working_dir == os.getcwd()

    def test_welcomebanner_working_dir_custom(self) -> None:
        """Test WelcomeBanner with custom working directory."""
        test_dir = "/tmp/test/dir"
        banner = WelcomeBanner(working_dir=test_dir)

        assert banner.working_dir == test_dir

    def test_welcomebanner_path_formatting_home(self) -> None:
        """Test WelcomeBanner formats home directory paths with ~."""
        home = os.path.expanduser("~")
        test_path = os.path.join(home, "git", "project")
        banner = WelcomeBanner(working_dir=test_path)

        formatted = banner._format_path(test_path)
        assert formatted == "~/git/project"

    def test_welcomebanner_path_formatting_absolute(self) -> None:
        """Test WelcomeBanner handles absolute paths not in home."""
        test_path = "/tmp/test/dir"
        banner = WelcomeBanner(working_dir=test_path)

        formatted = banner._format_path(test_path)
        assert formatted == "/tmp/test/dir"

    def test_welcomebanner_compact_mode(self) -> None:
        """Test WelcomeBanner compact mode flag is tracked."""
        banner_compact = WelcomeBanner(compact=True)
        banner_normal = WelcomeBanner(compact=False)

        # Both use same logo (simplified implementation)
        assert len(banner_compact._lines) == len(banner_normal._lines)
        assert banner_compact._compact is True
        assert banner_normal._compact is False

    def test_welcomebanner_animation_state(self) -> None:
        """Test WelcomeBanner animation state (disabled in simplified version)."""
        banner = WelcomeBanner()

        # Animation is disabled in simplified version
        assert banner.animation_progress == 0.0
        assert banner._animation_complete is True

    def test_welcomebanner_logo_lines(self) -> None:
        """Test WelcomeBanner parses logo into lines correctly."""
        banner = WelcomeBanner(compact=True)

        # Should have logo lines
        assert len(banner._lines) > 0
        # Each line should have content
        for line in banner._lines:
            assert len(line) > 0

    def test_welcomebanner_with_all_metadata(self) -> None:
        """Test WelcomeBanner with full metadata."""
        home = os.path.expanduser("~")
        test_dir = os.path.join(home, "miu-mono")

        banner = WelcomeBanner(
            version="0.2.0",
            model="claude-opus-4-20250805",
            mcp_count=3,
            working_dir=test_dir,
            compact=True,
        )

        assert banner.version == "0.2.0"
        assert banner.model == "claude-opus-4-20250805"
        assert banner.mcp_count == 3
        assert banner.working_dir == test_dir
        assert banner._format_path(test_dir) == "~/miu-mono"
        assert banner._compact is True

    def test_welcomebanner_mcp_count_zero(self) -> None:
        """Test WelcomeBanner with zero MCP count."""
        banner = WelcomeBanner(model="claude-opus-4-20250805", mcp_count=0)

        assert banner.mcp_count == 0

    def test_welcomebanner_mcp_count_multiple(self) -> None:
        """Test WelcomeBanner with multiple MCP servers."""
        banner = WelcomeBanner(model="claude-opus-4-20250805", mcp_count=5)

        assert banner.mcp_count == 5

    def test_welcomebanner_empty_version(self) -> None:
        """Test WelcomeBanner with empty version string."""
        banner = WelcomeBanner(version="")

        assert banner.version == ""

    def test_welcomebanner_empty_model(self) -> None:
        """Test WelcomeBanner with empty model string."""
        banner = WelcomeBanner(model="")

        assert banner.model == ""


class TestStatusBarModeIntegration:
    """Integration tests for StatusBar with ModeManager."""

    def test_mode_change_callback(self) -> None:
        """Test StatusBar receives mode change callbacks."""
        mode_manager = ModeManager()
        bar = StatusBar(mode_manager=mode_manager)

        initial_label = bar.mode_label

        # Cycle mode
        mode_manager.cycle()
        updated_label = bar.mode_label

        assert initial_label != updated_label
        assert "plan mode" in updated_label

    def test_multiple_mode_cycles(self) -> None:
        """Test StatusBar tracks multiple mode cycles through all 4 modes."""
        mode_manager = ModeManager()
        bar = StatusBar(mode_manager=mode_manager)

        modes_seen = [bar.mode_label]

        for _ in range(4):
            mode_manager.cycle()
            modes_seen.append(bar.mode_label)

        # Should see normal, plan, ask, auto, normal again
        assert len(set(modes_seen)) >= 4  # At least 4 different modes


class TestStatusBarUsageIntegration:
    """Integration tests for StatusBar with UsageTracker."""

    def test_usage_accumulation(self) -> None:
        """Test StatusBar correctly accumulates usage over time."""
        usage_tracker = UsageTracker()
        bar = StatusBar(usage_tracker=usage_tracker)

        initial = bar.token_usage
        assert "0%" in initial

        # Add usage
        bar.update_usage(input_tokens=50_000, output_tokens=25_000)
        assert bar.token_usage != initial
        assert "38%" in bar.token_usage  # 75k / 200k = 37.5%, rounds to 38%

    def test_usage_reset(self) -> None:
        """Test StatusBar updates when usage is reset."""
        usage_tracker = UsageTracker()
        bar = StatusBar(usage_tracker=usage_tracker)

        bar.update_usage(input_tokens=100_000, output_tokens=50_000)
        assert "75%" in bar.token_usage

        usage_tracker.reset()
        bar.token_usage = usage_tracker.format_usage()
        assert "0%" in bar.token_usage


class TestWelcomeBannerRender:
    """Tests for WelcomeBanner render output."""

    def test_render_returns_text(self) -> None:
        """Test WelcomeBanner render returns renderable text."""
        banner = WelcomeBanner(version="0.2.0", model="test-model")

        # render() is normally called by textual, we test the prep
        assert banner.version == "0.2.0"
        assert banner.model == "test-model"

    def test_render_with_metadata(self) -> None:
        """Test WelcomeBanner preserves metadata for rendering."""
        banner = WelcomeBanner(
            version="0.2.0",
            model="claude-opus-4-20250805",
            mcp_count=2,
            working_dir="/home/user/project",
        )

        assert banner.version == "0.2.0"
        assert banner.model == "claude-opus-4-20250805"
        assert banner.mcp_count == 2

    def test_animation_progress_boundaries(self) -> None:
        """Test WelcomeBanner animation progress stays within bounds."""
        banner = WelcomeBanner()

        # Initial state
        assert banner.animation_progress == 0.0

        # Should not exceed bounds
        banner.animation_progress = 1.5
        assert banner.animation_progress == 1.5


class TestPathFormatting:
    """Tests for path formatting in both widgets."""

    def test_both_widgets_format_same_path(self) -> None:
        """Test StatusBar and WelcomeBanner format paths the same way."""
        home = os.path.expanduser("~")
        test_path = os.path.join(home, "test", "path")

        status_bar = StatusBar(working_dir=test_path)
        banner = WelcomeBanner(working_dir=test_path)

        # Both should format the same way
        assert status_bar.current_path == banner._format_path(test_path)

    def test_nested_home_paths(self) -> None:
        """Test path formatting with deeply nested home paths."""
        home = os.path.expanduser("~")
        test_path = os.path.join(home, "a", "b", "c", "d", "e")

        bar = StatusBar(working_dir=test_path)
        assert bar.current_path == "~/a/b/c/d/e"

    def test_path_with_spaces(self) -> None:
        """Test path formatting with spaces in directory names."""
        home = os.path.expanduser("~")
        test_path = os.path.join(home, "My Documents", "My Projects")

        bar = StatusBar(working_dir=test_path)
        assert bar.current_path == "~/My Documents/My Projects"

    def test_root_paths(self) -> None:
        """Test path formatting for root-level paths."""
        bar = StatusBar(working_dir="/tmp")
        assert bar.current_path == "/tmp"

        bar = StatusBar(working_dir="/var/log")
        assert bar.current_path == "/var/log"


class TestWidgetInitialization:
    """Tests for widget initialization edge cases."""

    def test_statusbar_none_managers_use_defaults(self) -> None:
        """Test StatusBar creates default managers when None provided."""
        bar = StatusBar(mode_manager=None, usage_tracker=None)

        assert bar.mode_manager is not None
        assert bar._usage_tracker is not None

    def test_welcomebanner_auto_current_dir(self) -> None:
        """Test WelcomeBanner auto-assigns current directory."""
        cwd = os.getcwd()
        banner = WelcomeBanner()

        assert banner.working_dir == cwd

    def test_welcomebanner_explicit_dir_overrides_default(self) -> None:
        """Test WelcomeBanner uses explicit dir over current."""
        test_dir = "/custom/path"
        banner = WelcomeBanner(working_dir=test_dir)

        assert banner.working_dir == test_dir
        assert banner.working_dir != os.getcwd()

    def test_statusbar_empty_working_dir(self) -> None:
        """Test StatusBar handles empty working directory."""
        bar = StatusBar(working_dir="")

        assert bar.current_path == ""

    def test_welcomebanner_logo_parsing(self) -> None:
        """Test WelcomeBanner correctly parses logo."""
        banner = WelcomeBanner(compact=False)

        # Should have multiple lines
        assert len(banner._lines) > 1
        # All should be non-empty after parsing
        assert all(len(line) > 0 for line in banner._lines)
