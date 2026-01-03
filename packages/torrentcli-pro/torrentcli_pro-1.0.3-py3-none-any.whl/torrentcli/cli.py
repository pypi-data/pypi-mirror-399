"""
CLI interface using Click framework.

Provides commands for download management, configuration, and stats viewing.
"""

import sys
from pathlib import Path
from typing import Optional

import click

from torrentcli import __version__
from torrentcli.config import Config, load_config
from torrentcli.engine import DownloadEngine
from torrentcli.trackers.manager import TrackerManager
from torrentcli.utils.formatters import format_bytes, format_duration


@click.group(invoke_without_command=True)
@click.version_option(__version__, prog_name="TorrentCLI Pro")
@click.pass_context
def main(ctx: click.Context) -> None:
    """
    ▓▓▓▓ TORRENTCLI PRO - Hardcore torrent CLI for rare content

    Intelligent aria2c wrapper with health analysis, auto-tracker management,
    and cyberpunk terminal aesthetics.

    \b
    Examples:
      # Download with automatic profile selection
      torrentcli download "magnet:?xt=..."

      # Force rare-torrent mode for dead torrents
      torrentcli download "magnet:?xt=..." --profile rare

      # Batch download from file
      cat magnets.txt | while read m; do torrentcli dl "$m"; done

      # View download history
      torrentcli history --limit 20
    """
    # If no subcommand, show help
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@main.command(name="download")
@click.argument("source", type=str, required=True)
@click.option(
    "--profile",
    "-p",
    type=click.Choice(
        ["auto", "default", "rare", "fast", "seeder", "privacy", "batch"],
        case_sensitive=False,
    ),
    default="auto",
    help="Download profile (auto analyzes torrent health)",
)
@click.option(
    "--dir",
    "-d",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    default=None,
    help="Download directory (default: ~/Downloads)",
)
@click.option(
    "--theme",
    type=str,
    default=None,
    help="TUI theme (cyberpunk|matrix|solar|nord|gruvbox|midnight)",
)
@click.option(
    "--max-speed",
    type=str,
    default=None,
    help="Max download speed (e.g., 5M, 1.5G)",
)
@click.option(
    "--seed-time",
    type=int,
    default=None,
    help="Seed for N minutes after download",
)
@click.option(
    "--seed-ratio",
    type=float,
    default=None,
    help="Seed until ratio reached",
)
@click.option(
    "--no-seed",
    is_flag=True,
    default=False,
    help="Exit immediately after download",
)
@click.option(
    "--select",
    "-s",
    is_flag=True,
    default=False,
    help="Interactive file selection (multi-file torrents)",
)
@click.option(
    "--no-extra-trackers",
    is_flag=True,
    default=False,
    help="Don't append public tracker lists",
)
@click.option(
    "--timeout",
    type=str,
    default=None,
    help="Give up after duration (e.g., 30m, 2h)",
)
@click.option(
    "--on-complete",
    type=str,
    default=None,
    help="Shell command to run after download",
)
@click.option(
    "--quiet",
    "-q",
    is_flag=True,
    default=False,
    help="Suppress all output except errors",
)
@click.option(
    "--json",
    is_flag=True,
    default=False,
    help="Output stats as JSON",
)
@click.option(
    "--notify",
    type=click.Choice(["all", "important", "none"], case_sensitive=False),
    default="important",
    help="Desktop notification level",
)
def download(
    source: str,
    profile: str,
    dir: Optional[Path],
    theme: Optional[str],
    max_speed: Optional[str],
    seed_time: Optional[int],
    seed_ratio: Optional[float],
    no_seed: bool,
    select: bool,
    no_extra_trackers: bool,
    timeout: Optional[str],
    on_complete: Optional[str],
    quiet: bool,
    json: bool,
    notify: str,
) -> None:
    """
    Download a torrent from magnet URI or .torrent file.

    SOURCE can be:
      - Magnet URI: magnet:?xt=urn:btih:...
      - .torrent file path: /path/to/file.torrent
      - HTTP URL to .torrent: https://example.com/file.torrent
    """
    try:
        # Load configuration
        config = load_config()

        # Override config with CLI options
        if dir:
            config.download_dir = dir
        if theme:
            config.ui_theme = theme
        if max_speed:
            config.max_download_speed = max_speed
        if seed_time is not None:
            config.seed_time = seed_time
        if seed_ratio is not None:
            config.seed_ratio = seed_ratio
        if no_seed:
            config.seed_time = 0
            config.seed_ratio = 0.0
        if quiet:
            config.ui_mode = "quiet"
        if json:
            config.ui_mode = "json"
        if notify:
            config.notify_level = notify

        # Initialize download engine
        engine = DownloadEngine(config)

        # Start download
        result = engine.download(
            source=source,
            profile=profile,
            select_files=select,
            fetch_trackers=not no_extra_trackers,
            timeout=timeout,
            on_complete_hook=on_complete,
        )

        # Exit with appropriate code
        sys.exit(0 if result.success else 1)

    except KeyboardInterrupt:
        click.echo("\n\n⚠️  Download cancelled by user", err=True)
        sys.exit(130)
    except Exception as e:
        if not quiet:
            click.echo(f"\n❌ Error: {e}", err=True)
        sys.exit(1)


@main.command(name="list")
@click.option(
    "--status",
    type=click.Choice(["active", "paused", "completed", "all"], case_sensitive=False),
    default="all",
    help="Filter by status",
)
def list_downloads(status: str) -> None:
    """List active and resumable downloads."""
    config = load_config()
    engine = DownloadEngine(config)

    sessions = engine.list_sessions(status_filter=status)

    if not sessions:
        click.echo(f"No {status} downloads found.")
        return

    click.echo(f"\n{'HASH':<16} {'NAME':<40} {'PROGRESS':<10} {'STATUS':<10}")
    click.echo("─" * 80)

    for session in sessions:
        hash_short = session.hash[:12]
        name_truncated = (session.name[:37] + "...") if len(session.name) > 40 else session.name
        progress = f"{session.progress_percent:.1f}%"
        status_display = session.status.upper()

        click.echo(f"{hash_short:<16} {name_truncated:<40} {progress:<10} {status_display:<10}")


@main.command()
@click.argument("hash_or_name", type=str, required=True)
def resume(hash_or_name: str) -> None:
    """Resume a paused download by hash or name."""
    config = load_config()
    engine = DownloadEngine(config)

    try:
        result = engine.resume(hash_or_name)
        click.echo(f"✓ Resumed: {result.name} from {result.progress_percent:.1f}%")
    except Exception as e:
        click.echo(f"❌ Failed to resume: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument("hash_or_name", type=str, required=True)
def pause(hash_or_name: str) -> None:
    """Pause an active download."""
    config = load_config()
    engine = DownloadEngine(config)

    try:
        engine.pause(hash_or_name)
        click.echo(f"✓ Paused: {hash_or_name}")
    except Exception as e:
        click.echo(f"❌ Failed to pause: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument("hash", type=str, required=True)
@click.option("--delete-files", is_flag=True, help="Also delete downloaded files")
def cancel(hash: str, delete_files: bool) -> None:
    """Cancel a download and delete session."""
    config = load_config()
    engine = DownloadEngine(config)

    try:
        engine.cancel(hash, delete_files=delete_files)
        click.echo(f"✓ Cancelled: {hash}")
    except Exception as e:
        click.echo(f"❌ Failed to cancel: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option("--older-than", type=str, default="30d", help="Clean sessions older than (e.g., 7d)")
def clean(older_than: str) -> None:
    """Remove old completed sessions."""
    config = load_config()
    engine = DownloadEngine(config)

    try:
        count = engine.clean_sessions(older_than)
        click.echo(f"✓ Cleaned {count} sessions older than {older_than}")
    except Exception as e:
        click.echo(f"❌ Failed to clean: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument("source", type=str, required=True)
def info(source: str) -> None:
    """Show torrent metadata without downloading."""
    config = load_config()
    engine = DownloadEngine(config)

    try:
        metadata = engine.get_metadata(source)

        click.echo(f"\n📦 {metadata.name}")
        click.echo("─" * 80)
        click.echo(f"Hash:       {metadata.hash}")
        click.echo(f"Size:       {format_bytes(metadata.size_bytes)}")
        click.echo(f"Files:      {metadata.file_count}")
        click.echo(f"Pieces:     {metadata.piece_count} ({format_bytes(metadata.piece_length)} each)")
        click.echo(f"Trackers:   {len(metadata.trackers)}")

        if metadata.trackers:
            click.echo("\nTrackers:")
            for tracker in metadata.trackers[:5]:
                click.echo(f"  • {tracker}")
            if len(metadata.trackers) > 5:
                click.echo(f"  ... {len(metadata.trackers) - 5} more")

    except Exception as e:
        click.echo(f"❌ Failed to get metadata: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option("--limit", type=int, default=20, help="Max number of entries to show")
@click.option("--profile", type=str, default=None, help="Filter by profile")
def history(limit: int, profile: Optional[str]) -> None:
    """Show download history."""
    config = load_config()
    engine = DownloadEngine(config)

    entries = engine.get_history(limit=limit, profile_filter=profile)

    if not entries:
        click.echo("No download history found.")
        return

    click.echo(
        f"\n{'DATE':<20} {'NAME':<30} {'SIZE':<10} {'SPEED':<12} {'PROFILE':<10}"
    )
    click.echo("─" * 85)

    for entry in entries:
        date = entry.completed_at.strftime("%Y-%m-%d %H:%M")
        name = (entry.name[:27] + "...") if len(entry.name) > 30 else entry.name
        size = format_bytes(entry.size_bytes)
        speed = f"{entry.avg_speed_mbps:.1f} MiB/s"
        profile_name = entry.profile[:9]

        click.echo(f"{date:<20} {name:<30} {size:<10} {speed:<12} {profile_name:<10}")


@main.command()
def stats() -> None:
    """Show aggregate download statistics."""
    config = load_config()
    engine = DownloadEngine(config)

    stats = engine.get_aggregate_stats()

    click.echo("\n╔══════════════════════════════════════════════════════════════╗")
    click.echo("║              TORRENTCLI PRO - AGGREGATE STATS                ║")
    click.echo("╚══════════════════════════════════════════════════════════════╝\n")

    click.echo(f"Total Downloads:     {stats.total_downloads}")
    click.echo(f"Total Data:          {format_bytes(stats.total_bytes)}")
    click.echo(f"Avg Speed:           {stats.avg_speed_mbps:.1f} MiB/s")
    click.echo(f"Avg Duration:        {format_duration(int(stats.avg_duration_sec))}")
    click.echo(f"Success Rate:        {stats.success_rate:.1%}")
    click.echo(
        f"\nMost Used Profile:   {stats.most_used_profile} ({stats.profile_usage[stats.most_used_profile]} downloads)"
    )


@main.command(name="tracker-stats")
@click.option("--limit", type=int, default=20, help="Number of trackers to show")
def tracker_stats(limit: int) -> None:
    """Show tracker performance leaderboard."""
    config = load_config()
    tracker_manager = TrackerManager(config)

    stats = tracker_manager.get_tracker_stats(limit=limit)

    if not stats:
        click.echo("No tracker stats available yet.")
        return

    click.echo(
        f"\n{'TRACKER':<45} {'SUCCESS':<10} {'PEERS':<8} {'AVG RTT':<10}"
    )
    click.echo("─" * 75)

    for stat in stats:
        tracker = stat.tracker[:42] + "..." if len(stat.tracker) > 45 else stat.tracker
        success = f"{stat.success_rate:.1%}"
        peers = str(stat.total_peers_found)
        rtt = f"{stat.avg_rtt_ms:.0f}ms"

        click.echo(f"{tracker:<45} {success:<10} {peers:<8} {rtt:<10}")


@main.command(name="update-trackers")
def update_trackers() -> None:
    """Manually refresh tracker lists from sources."""
    config = load_config()
    tracker_manager = TrackerManager(config)

    try:
        click.echo("🔄 Fetching tracker lists from sources...")
        count = tracker_manager.update_tracker_lists(force=True)
        click.echo(f"✓ Updated {count} trackers")
    except Exception as e:
        click.echo(f"❌ Failed to update trackers: {e}", err=True)
        sys.exit(1)


@main.group(name="config")
def config_group() -> None:
    """Configuration management commands."""
    pass


@config_group.command(name="show")
def config_show() -> None:
    """Display current configuration."""
    config = load_config()
    click.echo(config.to_toml())


@config_group.command(name="init")
@click.option("--force", is_flag=True, help="Overwrite existing config")
def config_init(force: bool) -> None:
    """Initialize default configuration."""
    config_path = Path.home() / ".config" / "torrentcli" / "config.toml"

    if config_path.exists() and not force:
        click.echo(f"Config already exists at {config_path}")
        click.echo("Use --force to overwrite")
        return

    config_path.parent.mkdir(parents=True, exist_ok=True)

    default_config = Config.default()
    config_path.write_text(default_config.to_toml())

    click.echo(f"✓ Created default config at {config_path}")


@config_group.command(name="edit")
def config_edit() -> None:
    """Open config file in $EDITOR."""
    import os
    import subprocess

    config_path = Path.home() / ".config" / "torrentcli" / "config.toml"

    if not config_path.exists():
        click.echo("Config not initialized. Run 'torrentcli config init' first.")
        sys.exit(1)

    editor = os.environ.get("EDITOR", "nano")

    try:
        subprocess.run([editor, str(config_path)], check=True)
    except subprocess.CalledProcessError:
        click.echo(f"Failed to open editor: {editor}", err=True)
        sys.exit(1)


@main.command(name="list-profiles")
def list_profiles() -> None:
    """Show available download profiles."""
    config = load_config()

    click.echo("\n╔══════════════════════════════════════════════════════════════╗")
    click.echo("║                   AVAILABLE PROFILES                         ║")
    click.echo("╚══════════════════════════════════════════════════════════════╝\n")

    profiles = config.get_all_profiles()

    for name, profile in profiles.items():
        click.echo(f"[{name}]")
        click.echo(f"  Description:  {profile.description}")
        click.echo(f"  Use case:     {profile.use_case}")
        click.echo(f"  Max peers:    {profile.aria2c_options.get('bt-max-peers', 'N/A')}")
        click.echo(f"  Connections:  {profile.aria2c_options.get('max-connection-per-server', 'N/A')}")
        click.echo()



# Register aliases
main.add_command(download, name="dl")
main.add_command(list_downloads, name="ls")

if __name__ == "__main__":
    main()
