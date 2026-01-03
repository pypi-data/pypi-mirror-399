"""
CLI interface using Click framework.

Provides commands for download management, configuration, and stats viewing.
"""

import sys
import logging
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
    # Configure logging
    if "--quiet" not in sys.argv and "-q" not in sys.argv:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%H:%M:%S",
            stream=sys.stderr
        )
    else:
        logging.basicConfig(level=logging.ERROR, stream=sys.stderr)

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
            max_speed=max_speed,
            seed_time=seed_time,
            seed_ratio=seed_ratio,
        )

        # Exit with appropriate code
        if not result.success:
            if not quiet and result.error:
                click.echo(f"\n❌ Download failed: {result.error}", err=True)
            sys.exit(1)

        sys.exit(0)

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
        hash_short = session["hash"][:12]
        name = session.get("name", "Unknown")
        name_truncated = (name[:37] + "...") if len(name) > 40 else name
        progress = f"{session.get('progress_percent', 0.0):.1f}%"
        status_display = session.get("status", "unknown").upper()

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

        # engine.get_metadata returns a dict
        click.echo(f"\n📦 {metadata.get('name', 'Unknown')}")
        click.echo("─" * 80)
        click.echo(f"Hash:       {metadata.get('hash', source)}") # fallback to source if magnet
        click.echo(f"Size:       {format_bytes(metadata.get('size_bytes', 0))}")
        click.echo(f"Files:      {metadata.get('file_count', '?')}")
        click.echo(f"Pieces:     {metadata.get('piece_count', '?')}")

        trackers = metadata.get('trackers', [])
        click.echo(f"Trackers:   {len(trackers)}")

        if trackers:
            click.echo("\nTrackers:")
            for tracker in trackers[:5]:
                click.echo(f"  • {tracker}")
            if len(trackers) > 5:
                click.echo(f"  ... {len(trackers) - 5} more")

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
        # DB returns string timestamps
        date_str = str(entry.get("completed_at", "") or "")
        # Simple truncation/parsing if needed, or just use the string (first 16 chars "YYYY-MM-DD HH:MM")
        date = date_str[:16]

        entry_name = entry.get("name", "Unknown")
        name = (entry_name[:27] + "...") if len(entry_name) > 30 else entry_name
        size = format_bytes(entry.get("size_bytes", 0))

        # Calculate speed from bps
        speed_bps = entry.get("avg_speed_bps")
        if speed_bps:
            speed = f"{speed_bps / 1024 / 1024:.1f} MiB/s"
        else:
            speed = "0.0 MiB/s"

        profile_name = str(entry.get("profile", "unknown"))[:9]

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

    if not stats:
        click.echo("No stats available.")
        return

    click.echo(f"Total Downloads:     {stats.get('total_downloads', 0)}")
    click.echo(f"Total Data:          {format_bytes(stats.get('total_bytes', 0) or 0)}")

    avg_speed = stats.get('avg_speed', 0.0) or 0.0
    click.echo(f"Avg Speed:           {avg_speed / 1024 / 1024:.1f} MiB/s")

    # Duration might not be in the simple stats query?
    # queries.get_download_stats returns: total_downloads, successful_downloads, total_bytes, avg_speed, max_speed, avg_seeders
    # It does NOT return avg_duration_sec or success_rate directly.

    successful = stats.get('successful_downloads', 0)
    total = stats.get('total_downloads', 0)
    success_rate = (successful / total) if total > 0 else 0.0
    click.echo(f"Success Rate:        {success_rate:.1%}")

    # Profile usage analysis is not in the basic query.
    # We'll skip profile stats for MVP to avoid crash.


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
        tracker_url = stat.get("tracker", "unknown")
        tracker = tracker_url[:42] + "..." if len(tracker_url) > 45 else tracker_url
        success_rate = stat.get("success_rate", 0.0) or 0.0
        success = f"{success_rate:.1%}"
        peers = str(stat.get("total_peers_found", 0))
        rtt = f"{stat.get('avg_response_time_ms', 0):.0f}ms"

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


@main.command(name="repl")
@click.option(
    "--rpc-secret",
    type=str,
    default=None,
    envvar="ARIA2_RPC_SECRET",
    help="aria2c RPC secret token (or set ARIA2_RPC_SECRET env var)",
)
def repl_command(rpc_secret: Optional[str]) -> None:
    """
    Start interactive REPL for torrent management.

    The REPL provides an interactive shell with readline history
    for managing downloads via aria2c RPC.

    \b
    Supported source types:
      - Magnet URIs: magnet:?xt=urn:btih:...
      - HTTP/HTTPS URLs: https://example.com/file.torrent
      - Info hashes: dd8255ecdc7ca55fb0bbf81323d87062db1f6d1c
      - Torrent files: /path/to/file.torrent
      - Metalink files: /path/to/file.metalink

    \b
    Commands:
      add <source>           - Add a download
      pause <GID>            - Pause a download
      resume <GID>           - Resume a paused download
      remove <GID>           - Remove a download
      list                   - List all downloads
      details <GID>          - Show download details
      filter <status|name>   - Filter by status or name substring
      set <GID> <k>=<v>      - Set per-download option
      set global <k>=<v>     - Set global aria2c option
      retry                  - Reconnect to aria2c
      help                   - Show help with example magnet
      quit                   - Exit REPL

    \b
    Prerequisites:
      Start aria2c with RPC enabled:
      $ aria2c --enable-rpc --rpc-listen-all=true

    \b
    With RPC secret:
      $ aria2c --enable-rpc --rpc-secret=YOUR_SECRET
      $ torrentcli repl --rpc-secret=YOUR_SECRET
    """
    from torrentcli.repl import run_repl

    config = load_config()
    run_repl(config, rpc_secret=rpc_secret)


# Aliases for common commands
@main.command(name="dl")
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
@click.pass_context
def dl_alias(
    ctx: click.Context,
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
    """Alias for 'download' command with full option parity."""
    ctx.invoke(
        download,
        source=source,
        profile=profile,
        dir=dir,
        theme=theme,
        max_speed=max_speed,
        seed_time=seed_time,
        seed_ratio=seed_ratio,
        no_seed=no_seed,
        select=select,
        no_extra_trackers=no_extra_trackers,
        timeout=timeout,
        on_complete=on_complete,
        quiet=quiet,
        json=json,
        notify=notify,
    )


@main.command(name="ls")
@click.option("--status", type=str, default="all")
@click.pass_context
def ls_alias(ctx: click.Context, status: str) -> None:
    """Alias for 'list' command."""
    ctx.invoke(list_downloads, status=status)


if __name__ == "__main__":
    main()
