"""
TUI renderer using Rich Live display.

Provides real-time download progress visualization with:
- 10 FPS updates using Rich Live
- Theme-aware styling
- Responsive layouts (compact/detailed)
- Real-time speed graphs
- Tracker statistics
"""

import time
from typing import Any, Dict, List, Optional

from rich.align import Align
from rich.console import Console, Group, RenderableType
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TaskID, TextColumn, TimeRemainingColumn
from rich.table import Table
from rich.text import Text

from torrentcli.aria2c.wrapper import Aria2cStats
from torrentcli.engine import TorrentHealth
from torrentcli.tui.theme import Theme


class TUIRenderer:
    """
    Real-time TUI renderer for download progress.

    Uses Rich Live display to render download statistics at 10 FPS.
    """

    def __init__(self, theme: Theme, compact: bool = False, quiet: bool = False) -> None:
        """
        Initialize TUI renderer.

        Args:
            theme: Theme to use for styling
            compact: Use compact layout
            quiet: Minimal output mode
        """
        self.theme = theme
        self.compact = compact
        self.quiet = quiet
        self.console = Console()

        # Progress tracking
        self.start_time = time.time()
        self.peak_speed = 0.0
        self.peak_speed_time = 0.0
        self.speed_history: List[float] = []
        self.max_history_size = 50

        # Live display
        self.live: Optional[Live] = None

    def start(self) -> None:
        """Start the live display."""
        if not self.quiet:
            self.live = Live(
                self._render_placeholder(),
                console=self.console,
                refresh_per_second=10,  # 10 FPS
                transient=False,
            )
            self.live.start()

    def stop(self) -> None:
        """Stop the live display."""
        if self.live:
            self.live.stop()
            self.live = None

    def update(
        self,
        stats: Aria2cStats,
        health: Optional[TorrentHealth] = None,
        tracker_stats: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Update display with new statistics.

        Args:
            stats: Current download statistics
            health: Torrent health classification
            tracker_stats: Tracker statistics dict
        """
        # Update tracking
        if stats.download_speed > self.peak_speed:
            self.peak_speed = stats.download_speed
            self.peak_speed_time = time.time() - self.start_time

        # Update speed history for sparkline
        self.speed_history.append(stats.download_speed)
        if len(self.speed_history) > self.max_history_size:
            self.speed_history.pop(0)

        # Render updated display
        if self.live:
            if self.compact:
                renderable = self._render_compact(stats, health)
            else:
                renderable = self._render_detailed(stats, health, tracker_stats)

            self.live.update(renderable)
        elif not self.quiet:
            # Fallback to simple console print
            self._print_simple(stats)

    def _render_placeholder(self) -> RenderableType:
        """Render placeholder while waiting for first stats."""
        text = Text("Initializing download...", style=self.theme.colors.text_dim)
        return Align.center(text, vertical="middle")

    def _render_compact(
        self, stats: Aria2cStats, health: Optional[TorrentHealth]
    ) -> RenderableType:
        """
        Render compact one-line progress.

        Args:
            stats: Download statistics
            health: Torrent health

        Returns:
            Renderable object
        """
        # Progress bar
        progress_bar = self.theme.render_progress_bar(stats.progress_percent, width=30)

        # Speed and ETA
        speed_text = self._format_speed(stats.download_speed)
        eta_text = self._format_eta(stats.eta_seconds)

        # Build compact line
        line = Text()
        line.append(f"{stats.progress_percent:5.1f}% ", style=self.theme.colors.text_primary)
        line.append(progress_bar)
        line.append(f" {speed_text}", style=self.theme.colors.download_color)
        line.append(f" ETA: {eta_text}", style=self.theme.colors.text_secondary)
        line.append(
            f" [{stats.seeders}S/{stats.connections}P]", style=self.theme.colors.peer_color
        )

        return line

    def _render_detailed(
        self,
        stats: Aria2cStats,
        health: Optional[TorrentHealth],
        tracker_stats: Optional[Dict[str, Any]],
    ) -> RenderableType:
        """
        Render detailed multi-panel display.

        Args:
            stats: Download statistics
            health: Torrent health
            tracker_stats: Tracker statistics

        Returns:
            Renderable layout
        """
        # Create layout with sections
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="progress", size=8),
            Layout(name="stats", size=6),
            Layout(name="network", size=6),
        )

        # Header with status
        layout["header"].update(self._render_header(stats, health))

        # Progress section
        layout["progress"].update(self._render_progress_section(stats))

        # Stats section
        layout["stats"].update(self._render_stats_section(stats))

        # Network section
        layout["network"].update(self._render_network_section(stats, tracker_stats))

        return Panel(layout, border_style=self.theme.colors.border, title="TorrentCLI Pro")

    def _render_header(self, stats: Aria2cStats, health: Optional[TorrentHealth]) -> RenderableType:
        """Render header with status."""
        status_text = Text()
        status_text.append("Status: ", style=self.theme.colors.text_dim)

        if stats.status == "complete":
            status_text.append("COMPLETE", style=self.theme.colors.accent_success)
        elif stats.status == "downloading":
            status_text.append("DOWNLOADING", style=self.theme.colors.accent_info)
        elif stats.status == "stalled":
            status_text.append("STALLED", style=self.theme.colors.accent_warning)
        elif stats.status == "error":
            status_text.append("ERROR", style=self.theme.colors.accent_error)
        else:
            status_text.append(stats.status.upper(), style=self.theme.colors.text_primary)

        if health:
            status_text.append(" | Health: ", style=self.theme.colors.text_dim)
            status_text.append(health.value.upper(), style=self._get_health_color(health))

        return Align.center(status_text)

    def _render_progress_section(self, stats: Aria2cStats) -> RenderableType:
        """Render progress bar and percentage."""
        # Large progress bar
        progress_bar = self.theme.render_progress_bar(stats.progress_percent, width=60)

        # Percentage and sizes
        progress_text = Text()
        progress_text.append(f"{stats.progress_percent:5.1f}%\n", style=self.theme.colors.text_primary, justify="center")

        # Downloaded / Total
        downloaded_str = self._format_bytes(stats.downloaded)
        total_str = self._format_bytes(stats.total_size)
        remaining_str = self._format_bytes(stats.total_size - stats.downloaded)

        size_text = Text()
        size_text.append(f"{downloaded_str} / {total_str}", style=self.theme.colors.text_secondary)
        size_text.append(f" ({remaining_str} remaining)", style=self.theme.colors.text_dim)

        group = Group(
            Align.center(progress_text),
            Align.center(progress_bar),
            Text(""),  # Spacing
            Align.center(size_text),
        )

        return Panel(group, title="Progress", border_style=self.theme.colors.border)

    def _render_stats_section(self, stats: Aria2cStats) -> RenderableType:
        """Render download statistics table."""
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Label", style=self.theme.colors.text_dim)
        table.add_column("Value", style=self.theme.colors.text_primary)

        # Speed stats
        current_speed = self._format_speed(stats.download_speed)
        peak_speed = self._format_speed(self.peak_speed)
        peak_time = self._format_duration(self.peak_speed_time)

        table.add_row("Download Speed:", current_speed)
        table.add_row("Peak Speed:", f"{peak_speed} @ {peak_time}")

        # Upload speed (if available)
        if stats.upload_speed > 0:
            upload_speed = self._format_speed(stats.upload_speed)
            table.add_row("Upload Speed:", upload_speed)

        # ETA
        eta = self._format_eta(stats.eta_seconds)
        table.add_row("ETA:", eta)

        # Elapsed time
        elapsed = self._format_duration(time.time() - self.start_time)
        table.add_row("Elapsed:", elapsed)

        return Panel(table, title="Statistics", border_style=self.theme.colors.border)

    def _render_network_section(
        self, stats: Aria2cStats, tracker_stats: Optional[Dict[str, Any]]
    ) -> RenderableType:
        """Render network and tracker statistics."""
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Label", style=self.theme.colors.text_dim)
        table.add_column("Value", style=self.theme.colors.text_primary)

        # Peers and seeders
        table.add_row("Connections:", f"{stats.connections}")
        table.add_row("Seeders:", f"{stats.seeders}")

        # Tracker stats if available
        if tracker_stats:
            responding = tracker_stats.get("responding", 0)
            total = tracker_stats.get("total", 0)
            table.add_row("Trackers:", f"{responding}/{total} responding")

        # Speed graph (sparkline)
        if self.speed_history:
            sparkline = self._render_sparkline(self.speed_history)
            table.add_row("Speed Graph:", sparkline)

        return Panel(table, title="Network", border_style=self.theme.colors.border)

    def _render_sparkline(self, values: List[float]) -> Text:
        """
        Render sparkline graph from speed history.

        Args:
            values: List of speed values

        Returns:
            Text with sparkline characters
        """
        if not values:
            return Text("No data", style=self.theme.colors.text_dim)

        # Normalize values to sparkline levels
        max_val = max(values) if max(values) > 0 else 1
        levels = self.theme.chars.sparkline_levels

        sparkline = Text()
        for value in values:
            normalized = value / max_val
            level_idx = int(normalized * (len(levels) - 1))
            char = levels[level_idx]
            sparkline.append(char, style=self.theme.colors.download_color)

        return sparkline

    def _print_simple(self, stats: Aria2cStats) -> None:
        """Simple console print fallback."""
        speed = self._format_speed(stats.download_speed)
        eta = self._format_eta(stats.eta_seconds)
        self.console.print(
            f"[{stats.progress_percent:5.1f}%] {speed} | ETA: {eta} | "
            f"{stats.seeders}S/{stats.connections}P"
        )

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
            return f"{hours}h {minutes}m"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"

    @staticmethod
    def _format_duration(seconds: float) -> str:
        """Format duration to human-readable time."""
        total_secs = int(seconds)
        hours = total_secs // 3600
        minutes = (total_secs % 3600) // 60
        secs = total_secs % 60

        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"


def render_completion_message(
    theme: Theme, name: str, size_bytes: int, duration_sec: float, avg_speed_bps: float
) -> None:
    """
    Render download completion message.

    Args:
        theme: Theme to use
        name: Download name
        size_bytes: Total size in bytes
        duration_sec: Download duration
        avg_speed_bps: Average download speed
    """
    console = Console()

    # Create completion panel
    completion_text = Text()
    completion_text.append("Download Complete!\n\n", style=theme.colors.accent_success, justify="center")

    completion_text.append("File: ", style=theme.colors.text_dim)
    completion_text.append(f"{name}\n", style=theme.colors.text_primary)

    size_str = TUIRenderer._format_bytes(size_bytes)
    completion_text.append("Size: ", style=theme.colors.text_dim)
    completion_text.append(f"{size_str}\n", style=theme.colors.text_primary)

    duration_str = TUIRenderer._format_duration(duration_sec)
    completion_text.append("Duration: ", style=theme.colors.text_dim)
    completion_text.append(f"{duration_str}\n", style=theme.colors.text_primary)

    avg_speed_str = TUIRenderer._format_speed(avg_speed_bps)
    completion_text.append("Average Speed: ", style=theme.colors.text_dim)
    completion_text.append(f"{avg_speed_str}", style=theme.colors.text_primary)

    panel = Panel(
        Align.center(completion_text),
        border_style=theme.colors.accent_success,
        title="Success",
    )

    console.print(panel)


def render_error_message(theme: Theme, error: str) -> None:
    """
    Render error message.

    Args:
        theme: Theme to use
        error: Error message
    """
    console = Console()

    error_text = Text()
    error_text.append("Download Failed\n\n", style=theme.colors.accent_error, justify="center")
    error_text.append(error, style=theme.colors.text_primary)

    panel = Panel(
        Align.center(error_text),
        border_style=theme.colors.accent_error,
        title="Error",
    )

    console.print(panel)
