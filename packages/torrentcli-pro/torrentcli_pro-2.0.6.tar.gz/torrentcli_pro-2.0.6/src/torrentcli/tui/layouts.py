"""
Responsive layout system for TUI.

Provides adaptive layouts that adjust to terminal width:
- 80 columns: Compact single-column layout
- 120+ columns: Wide multi-column layout with graphs
- Auto-detection and dynamic resizing
"""

import shutil
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from rich.console import Console, RenderableType
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from torrentcli.aria2c.wrapper import Aria2cStats
from torrentcli.engine import TorrentHealth
from torrentcli.tui.theme import Theme


class LayoutMode(Enum):
    """Layout mode based on terminal width."""

    MINIMAL = "minimal"  # <80 columns
    COMPACT = "compact"  # 80-119 columns
    WIDE = "wide"  # 120+ columns


@dataclass
class LayoutConfig:
    """Configuration for a layout mode."""

    mode: LayoutMode
    terminal_width: int
    show_graphs: bool
    show_tracker_details: bool
    progress_bar_width: int
    max_tracker_rows: int


class ResponsiveLayout:
    """
    Responsive layout that adapts to terminal width.

    Automatically detects terminal size and selects appropriate layout.
    """

    def __init__(self, theme: Theme, force_mode: Optional[LayoutMode] = None) -> None:
        """
        Initialize responsive layout.

        Args:
            theme: Theme to use for styling
            force_mode: Optional forced layout mode (overrides auto-detection)
        """
        self.theme = theme
        self.force_mode = force_mode
        self.console = Console()

    def detect_layout_mode(self) -> LayoutConfig:
        """
        Detect optimal layout mode based on terminal width.

        Returns:
            LayoutConfig for current terminal
        """
        # Get terminal width
        try:
            width = shutil.get_terminal_size().columns
        except Exception:
            width = 80  # Fallback

        # Use forced mode if specified
        if self.force_mode:
            mode = self.force_mode
        elif width < 80:
            mode = LayoutMode.MINIMAL
        elif width < 120:
            mode = LayoutMode.COMPACT
        else:
            mode = LayoutMode.WIDE

        # Configure based on mode
        if mode == LayoutMode.MINIMAL:
            return LayoutConfig(
                mode=mode,
                terminal_width=width,
                show_graphs=False,
                show_tracker_details=False,
                progress_bar_width=30,
                max_tracker_rows=3,
            )
        elif mode == LayoutMode.COMPACT:
            return LayoutConfig(
                mode=mode,
                terminal_width=width,
                show_graphs=True,
                show_tracker_details=False,
                progress_bar_width=50,
                max_tracker_rows=5,
            )
        else:  # WIDE
            return LayoutConfig(
                mode=mode,
                terminal_width=width,
                show_graphs=True,
                show_tracker_details=True,
                progress_bar_width=70,
                max_tracker_rows=10,
            )

    def render(
        self,
        stats: Aria2cStats,
        health: Optional[TorrentHealth] = None,
        tracker_list: Optional[list] = None,
    ) -> RenderableType:
        """
        Render layout based on current terminal size.

        Args:
            stats: Download statistics
            health: Torrent health classification
            tracker_list: List of tracker info dicts

        Returns:
            Renderable layout
        """
        config = self.detect_layout_mode()

        if config.mode == LayoutMode.MINIMAL:
            return self._render_minimal(stats, config)
        elif config.mode == LayoutMode.COMPACT:
            return self._render_compact(stats, health, config)
        else:
            return self._render_wide(stats, health, tracker_list, config)

    def _render_minimal(self, stats: Aria2cStats, config: LayoutConfig) -> RenderableType:
        """
        Render minimal single-line layout.

        Args:
            stats: Download statistics
            config: Layout configuration

        Returns:
            Minimal renderable
        """
        # Just show essential info in one line
        progress_bar = self.theme.render_progress_bar(stats.progress_percent, width=config.progress_bar_width)

        speed = self._format_speed(stats.download_speed)
        eta = self._format_eta(stats.eta_seconds)

        line = Text()
        line.append(f"{stats.progress_percent:5.1f}% ", style=self.theme.colors.text_primary)
        line.append(progress_bar)
        line.append(f" {speed} ", style=self.theme.colors.download_color)
        line.append(f"ETA:{eta}", style=self.theme.colors.text_dim)

        return line

    def _render_compact(
        self, stats: Aria2cStats, health: Optional[TorrentHealth], config: LayoutConfig
    ) -> RenderableType:
        """
        Render compact single-column layout.

        Args:
            stats: Download statistics
            health: Torrent health
            config: Layout configuration

        Returns:
            Compact layout
        """
        layout = Layout()
        layout.split_column(
            Layout(name="progress", size=5),
            Layout(name="stats", size=4),
        )

        # Progress section
        progress_bar = self.theme.render_progress_bar(stats.progress_percent, width=config.progress_bar_width)
        downloaded = self._format_bytes(stats.downloaded)
        total = self._format_bytes(stats.total_size)

        progress_text = Text()
        progress_text.append(f"{stats.progress_percent:5.1f}% ", style=self.theme.colors.text_primary)
        progress_text.append(f"[{downloaded} / {total}]\n", style=self.theme.colors.text_secondary)

        progress_content = Text.assemble(
            progress_text,
            "\n",
            progress_bar,
        )

        layout["progress"].update(
            Panel(progress_content, title="Progress", border_style=self.theme.colors.border)
        )

        # Stats section
        stats_table = Table(show_header=False, box=None, padding=(0, 1))
        stats_table.add_column("Label", style=self.theme.colors.text_dim)
        stats_table.add_column("Value", style=self.theme.colors.text_primary)

        stats_table.add_row("Speed:", self._format_speed(stats.download_speed))
        stats_table.add_row("ETA:", self._format_eta(stats.eta_seconds))
        stats_table.add_row("Peers:", f"{stats.seeders}S / {stats.connections}P")

        layout["stats"].update(
            Panel(stats_table, title="Info", border_style=self.theme.colors.border)
        )

        return layout

    def _render_wide(
        self,
        stats: Aria2cStats,
        health: Optional[TorrentHealth],
        tracker_list: Optional[list],
        config: LayoutConfig,
    ) -> RenderableType:
        """
        Render wide multi-column layout.

        Args:
            stats: Download statistics
            health: Torrent health
            tracker_list: List of tracker dicts
            config: Layout configuration

        Returns:
            Wide layout
        """
        # Main layout with side-by-side columns
        layout = Layout()
        layout.split_row(
            Layout(name="left", ratio=2),
            Layout(name="right", ratio=1),
        )

        # Left column: Progress and stats
        layout["left"].split_column(
            Layout(name="progress", size=7),
            Layout(name="stats", size=6),
        )

        # Right column: Network and trackers
        layout["right"].split_column(
            Layout(name="network", size=6),
            Layout(name="trackers", size=7),
        )

        # Progress section
        progress_bar = self.theme.render_progress_bar(stats.progress_percent, width=config.progress_bar_width)
        downloaded = self._format_bytes(stats.downloaded)
        total = self._format_bytes(stats.total_size)
        remaining = self._format_bytes(stats.total_size - stats.downloaded)

        progress_content = Text.assemble(
            (f"{stats.progress_percent:6.2f}%\n\n", self.theme.colors.text_primary),
            progress_bar,
            "\n\n",
            (f"{downloaded} / {total} ", self.theme.colors.text_secondary),
            (f"({remaining} remaining)", self.theme.colors.text_dim),
        )

        layout["left"]["progress"].update(
            Panel(progress_content, title="Progress", border_style=self.theme.colors.border)
        )

        # Stats section
        stats_table = Table(show_header=False, box=None, padding=(0, 2))
        stats_table.add_column("Label", style=self.theme.colors.text_dim, width=20)
        stats_table.add_column("Value", style=self.theme.colors.text_primary)

        stats_table.add_row("Download Speed:", self._format_speed(stats.download_speed))
        stats_table.add_row("Upload Speed:", self._format_speed(stats.upload_speed))
        stats_table.add_row("ETA:", self._format_eta(stats.eta_seconds))

        layout["left"]["stats"].update(
            Panel(stats_table, title="Statistics", border_style=self.theme.colors.border)
        )

        # Network section
        network_table = Table(show_header=False, box=None, padding=(0, 2))
        network_table.add_column("Label", style=self.theme.colors.text_dim)
        network_table.add_column("Value", style=self.theme.colors.text_primary)

        network_table.add_row("Connections:", f"{stats.connections}")
        network_table.add_row("Seeders:", f"{stats.seeders}")

        if health:
            health_color = self._get_health_color(health)
            network_table.add_row("Health:", Text(health.value.upper(), style=health_color))

        layout["right"]["network"].update(
            Panel(network_table, title="Network", border_style=self.theme.colors.border)
        )

        # Trackers section
        if tracker_list and config.show_tracker_details:
            trackers_content = self._render_tracker_table(tracker_list, config.max_tracker_rows)
        else:
            trackers_content = Text("No tracker data", style=self.theme.colors.text_dim)

        layout["right"]["trackers"].update(
            Panel(trackers_content, title="Trackers", border_style=self.theme.colors.border)
        )

        return layout

    def _render_tracker_table(self, tracker_list: list, max_rows: int) -> Table:
        """
        Render tracker statistics table.

        Args:
            tracker_list: List of tracker info dicts
            max_rows: Maximum rows to show

        Returns:
            Table with tracker info
        """
        table = Table(show_header=True, box=None, padding=(0, 1))
        table.add_column("Tracker", style=self.theme.colors.tracker_color, no_wrap=True)
        table.add_column("Seeders", style=self.theme.colors.text_primary, justify="right")
        table.add_column("Time", style=self.theme.colors.text_dim, justify="right")

        # Sort by seeder count and take top N
        sorted_trackers = sorted(
            tracker_list, key=lambda t: t.get("seeders", 0), reverse=True
        )[:max_rows]

        for tracker in sorted_trackers:
            # Truncate tracker URL
            url = tracker.get("url", "Unknown")
            if len(url) > 30:
                url = "..." + url[-27:]

            seeders = tracker.get("seeders", 0)
            response_time = tracker.get("response_time_ms", 0)

            table.add_row(url, str(seeders), f"{response_time:.0f}ms")

        return table

    def _get_health_color(self, health: TorrentHealth) -> str:
        """Get color for health status."""
        mapping = {
            TorrentHealth.HEALTHY: self.theme.colors.accent_success,
            TorrentHealth.MODERATE: self.theme.colors.accent_info,
            TorrentHealth.RARE: self.theme.colors.accent_warning,
            TorrentHealth.DEAD: self.theme.colors.accent_error,
        }
        return mapping.get(health, self.theme.colors.text_primary)

    @staticmethod
    def _format_speed(bps: float) -> str:
        """Format bytes per second to human-readable speed."""
        units = ["B/s", "KB/s", "MB/s", "GB/s"]
        value = bps
        unit_idx = 0

        while value >= 1024 and unit_idx < len(units) - 1:
            value /= 1024
            unit_idx += 1

        return f"{value:6.2f} {units[unit_idx]}"

    @staticmethod
    def _format_bytes(bytes_val: int) -> str:
        """Format bytes to human-readable size."""
        units = ["B", "KB", "MB", "GB", "TB"]
        value = float(bytes_val)
        unit_idx = 0

        while value >= 1024 and unit_idx < len(units) - 1:
            value /= 1024
            unit_idx += 1

        return f"{value:.2f} {units[unit_idx]}"

    @staticmethod
    def _format_eta(seconds: int) -> str:
        """Format ETA seconds to human-readable time."""
        if seconds <= 0:
            return "Unknown"

        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60

        if hours > 0:
            return f"{hours}h{minutes}m"
        elif minutes > 0:
            return f"{minutes}m{secs}s"
        else:
            return f"{secs}s"


def get_terminal_width() -> int:
    """
    Get current terminal width.

    Returns:
        Terminal width in columns
    """
    try:
        return shutil.get_terminal_size().columns
    except Exception:
        return 80  # Fallback
