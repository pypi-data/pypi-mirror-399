"""
Download engine - orchestrates torrent downloads with health analysis.

Responsibilities:
- Analyze torrent health before downloading
- Select optimal profile based on health
- Spawn and monitor aria2c subprocess
- Detect stalls and escalate configuration
- Handle completion/errors
- Persist session state and history
"""

import asyncio
import hashlib
import logging
import re
import signal
import sqlite3
import sys
import tempfile
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from torrentcli.aria2c.wrapper import Aria2cStats, Aria2cWrapper
from torrentcli.db import queries, schema
from torrentcli.trackers.manager import TrackerManager
from torrentcli.types import TorrentHealth
from torrentcli.utils.health import HealthAnalysisResult, TorrentHealthAnalyzer

logger = logging.getLogger(__name__)




@dataclass
class DownloadStats:
    """Real-time download statistics."""

    # Progress
    progress_percent: float
    downloaded: str  # Formatted (e.g., "2.2 GiB")
    total: str
    remaining: str
    eta: str

    # Speed
    speed_current: str
    speed_avg: str
    speed_peak: str
    peak_time: str

    # Upload
    upload_speed: str
    ratio: float

    # Network
    peers_connected: int
    peers_available: int
    seeders: int
    last_peer_seen: str
    seeder_found_time: str

    # Trackers
    trackers_responding: int
    trackers_total: int
    tracker_success_rate: float
    top_trackers: List[Any]

    # Metadata
    health: TorrentHealth
    status: str


@dataclass
class DownloadResult:
    """Result of a download operation."""

    success: bool
    name: str
    size_bytes: int
    progress_percent: float
    error: Optional[str] = None


class DownloadEngine:
    """
    Main download orchestration engine.

    Orchestrates health analysis, tracker fetching, aria2c spawning,
    progress monitoring, and database persistence.
    """

    def __init__(self, config: Any) -> None:
        """
        Initialize download engine.

        Args:
            config: Config object with profiles and settings
        """
        self.config = config
        self.db_conn = schema.init_database()
        self.health_analyzer = TorrentHealthAnalyzer()
        self.tracker_manager = TrackerManager(self.config)
        self.active_downloads: Dict[str, Aria2cWrapper] = {}

        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._handle_interrupt)
        signal.signal(signal.SIGTERM, self._handle_interrupt)

    def download(
        self,
        source: str,
        profile: str,
        select_files: bool,
        fetch_trackers: bool,
        timeout: Optional[str],
        on_complete_hook: Optional[str],
    ) -> DownloadResult:
        """
        Download a torrent.

        Args:
            source: Magnet URI or .torrent file path
            profile: Profile name or "auto"
            select_files: Enable interactive file selection
            fetch_trackers: Fetch external tracker lists
            timeout: Max duration before giving up
            on_complete_hook: Shell command to run on completion

        Returns:
            DownloadResult with success status
        """
        try:
            # Step 1: Parse source and extract info hash
            info_hash = self._extract_info_hash(source)
            logger.info(f"Starting download: {info_hash[:16]}...")

            # Step 2: Analyze torrent health (if magnet)
            health_result: Optional[HealthAnalysisResult] = None
            if source.startswith("magnet:?"):
                logger.info("Analyzing torrent health...")
                health_result = asyncio.run(self.health_analyzer.analyze(source))
                logger.info(
                    f"Health: {health_result.classification.value} "
                    f"({health_result.total_seeders} seeders, "
                    f"{health_result.responding_trackers}/{health_result.total_trackers} trackers)"
                )

            # Step 3: Auto-select profile if needed
            if profile == "auto" and health_result:
                profile = self._select_profile_for_health(health_result.classification)
                logger.info(f"Auto-selected profile: {profile}")
            elif profile == "auto":
                profile = self.config.default_profile

            # Step 4: Fetch additional trackers if requested
            if fetch_trackers:
                logger.info("Fetching external tracker lists...")
                extra_trackers = asyncio.run(self.tracker_manager.get_trackers(profile))
                source = self.tracker_manager.append_to_magnet(source, extra_trackers)
                logger.info(f"Added {len(extra_trackers)} trackers to magnet")

            # Step 5: Get profile configuration
            profile_config = self.config.get_profile(profile)
            download_dir = Path(self.config.download_dir).expanduser()
            download_dir.mkdir(parents=True, exist_ok=True)

            # Step 6: Create database records
            queries.insert_download(
                self.db_conn,
                hash=info_hash,
                name="Unknown",  # Will be updated once aria2c fetches metadata
                size_bytes=0,  # Will be updated
                profile=profile,
                destination=str(download_dir),
                metadata={"health": health_result.classification.value if health_result else "unknown"},
            )

            # Create session for resume support
            session_file = Path.home() / ".local" / "share" / "torrentcli" / "sessions" / f"{info_hash}.aria2"
            session_file.parent.mkdir(parents=True, exist_ok=True)

            queries.create_session(
                self.db_conn,
                hash=info_hash,
                magnet_uri=source,
                download_dir=str(download_dir),
                profile=profile,
                aria2c_session_file=str(session_file),
            )

            # Step 7: Spawn aria2c wrapper
            logger.info(f"Starting download with profile '{profile}'...")
            wrapper = Aria2cWrapper(
                magnet_or_torrent=source,
                download_dir=download_dir,
                aria2c_options=profile_config.aria2c_options,
                session_file=session_file,
            )

            wrapper.start()
            self.active_downloads[info_hash] = wrapper

            # Step 8: Monitor progress
            result = self._monitor_download(
                wrapper=wrapper,
                info_hash=info_hash,
                timeout_str=timeout,
                on_complete_hook=on_complete_hook,
            )

            # Step 9: Cleanup
            del self.active_downloads[info_hash]

            # Update database
            queries.complete_download(
                self.db_conn,
                hash=info_hash,
                success=result.success,
                error_message=result.error,
            )

            queries.complete_session(
                self.db_conn,
                hash=info_hash,
                success=result.success,
            )

            return result

        except KeyboardInterrupt:
            logger.warning("Download interrupted by user")
            return DownloadResult(
                success=False,
                name="Unknown",
                size_bytes=0,
                progress_percent=0.0,
                error="Interrupted by user",
            )
        except Exception as e:
            logger.error(f"Download failed: {e}", exc_info=True)
            return DownloadResult(
                success=False,
                name="Unknown",
                size_bytes=0,
                progress_percent=0.0,
                error=str(e),
            )

    def _monitor_download(
        self,
        wrapper: Aria2cWrapper,
        info_hash: str,
        timeout_str: Optional[str],
        on_complete_hook: Optional[str],
    ) -> DownloadResult:
        """
        Monitor download progress until completion or timeout.

        Args:
            wrapper: Aria2cWrapper instance
            info_hash: Torrent info hash
            timeout_str: Optional timeout (e.g., "30m", "1h")
            on_complete_hook: Shell command to run on completion

        Returns:
            DownloadResult
        """
        start_time = time.time()
        timeout_seconds = self._parse_timeout(timeout_str) if timeout_str else None

        name = "Unknown"
        size_bytes = 0
        peak_speed = 0.0
        total_seeders = 0
        total_peers = 0

        last_progress = 0.0
        stall_start_time: Optional[float] = None

        try:
            while wrapper.is_running():
                stats = wrapper.poll_stats()

                if stats:
                    # Update tracking variables
                    if stats.total_size > 0:
                        size_bytes = stats.total_size

                    if stats.download_speed > peak_speed:
                        peak_speed = stats.download_speed

                    if stats.seeders > total_seeders:
                        total_seeders = stats.seeders

                    if stats.connections > total_peers:
                        total_peers = stats.connections

                    # Update database periodically
                    if stats.progress_percent - last_progress >= 5.0:  # Every 5%
                        queries.update_download_progress(
                            self.db_conn,
                            hash=info_hash,
                            peak_speed_bps=peak_speed,
                            seeders_found=total_seeders,
                            peers_max=total_peers,
                        )
                        queries.update_session_progress(
                            self.db_conn,
                            hash=info_hash,
                            progress_percent=stats.progress_percent,
                            status="active",
                        )
                        last_progress = stats.progress_percent

                    # Check for stalls (no progress for 60 seconds)
                    if stats.download_speed == 0 and stats.progress_percent < 100:
                        if stall_start_time is None:
                            stall_start_time = time.time()
                        elif time.time() - stall_start_time > 60:
                            logger.warning("Download stalled for 60s, considering timeout...")
                    else:
                        stall_start_time = None

                    # Check for completion
                    if stats.status == "complete":
                        logger.info("Download completed successfully!")

                        # Run completion hook if provided
                        if on_complete_hook:
                            self._run_completion_hook(on_complete_hook, info_hash)

                        return DownloadResult(
                            success=True,
                            name=name,
                            size_bytes=size_bytes,
                            progress_percent=100.0,
                        )

                    # Check for errors
                    if stats.status == "error":
                        exit_code = wrapper.get_exit_code()
                        logs = wrapper.get_logs(last_n=10)
                        error_msg = f"aria2c exited with code {exit_code}"
                        logger.error(error_msg)
                        logger.debug(f"Last 10 log lines:\n" + "\n".join(logs))

                        return DownloadResult(
                            success=False,
                            name=name,
                            size_bytes=size_bytes,
                            progress_percent=stats.progress_percent,
                            error=error_msg,
                        )

                # Check timeout
                if timeout_seconds and (time.time() - start_time) > timeout_seconds:
                    logger.warning(f"Download timeout ({timeout_str}) reached")
                    wrapper.stop(graceful=True)
                    return DownloadResult(
                        success=False,
                        name=name,
                        size_bytes=size_bytes,
                        progress_percent=stats.progress_percent if stats else 0.0,
                        error=f"Timeout ({timeout_str})",
                    )

                # Sleep briefly to avoid busy-waiting
                time.sleep(0.5)

            # Process exited without completing
            exit_code = wrapper.get_exit_code()
            if exit_code == 0:
                return DownloadResult(
                    success=True,
                    name=name,
                    size_bytes=size_bytes,
                    progress_percent=100.0,
                )
            else:
                return DownloadResult(
                    success=False,
                    name=name,
                    size_bytes=size_bytes,
                    progress_percent=0.0,
                    error=f"aria2c exited with code {exit_code}",
                )

        except KeyboardInterrupt:
            logger.warning("Download interrupted")
            wrapper.stop(graceful=True)
            raise

    def _extract_info_hash(self, source: str) -> str:
        """
        Extract info hash from magnet URI or .torrent file.

        Args:
            source: Magnet URI or .torrent file path

        Returns:
            Info hash (hex string)
        """
        if source.startswith("magnet:?"):
            # Extract from magnet URI
            match = re.search(r"xt=urn:btih:([a-fA-F0-9]{40}|[A-Za-z0-9]{32})", source)
            if not match:
                raise ValueError("Invalid magnet URI: no info hash found")
            return match.group(1).lower()
        else:
            # For .torrent files, hash the file path as a simple identifier
            # In a real implementation, you'd parse the .torrent file
            return hashlib.sha1(source.encode()).hexdigest()

    def _select_profile_for_health(self, health: TorrentHealth) -> str:
        """
        Auto-select best profile for torrent health.

        Args:
            health: TorrentHealth classification

        Returns:
            Profile name
        """
        mapping = {
            TorrentHealth.HEALTHY: "balanced",
            TorrentHealth.MODERATE: "aggressive",
            TorrentHealth.RARE: "rare",
            TorrentHealth.DEAD: "rare",
        }
        return mapping.get(health, self.config.default_profile)

    def _parse_timeout(self, timeout_str: str) -> int:
        """
        Parse timeout string to seconds.

        Args:
            timeout_str: Timeout string (e.g., "30m", "1h", "2h30m")

        Returns:
            Timeout in seconds
        """
        total_seconds = 0

        # Parse hours
        hours_match = re.search(r"(\d+)h", timeout_str)
        if hours_match:
            total_seconds += int(hours_match.group(1)) * 3600

        # Parse minutes
        minutes_match = re.search(r"(\d+)m", timeout_str)
        if minutes_match:
            total_seconds += int(minutes_match.group(1)) * 60

        # Parse seconds
        seconds_match = re.search(r"(\d+)s", timeout_str)
        if seconds_match:
            total_seconds += int(seconds_match.group(1))

        return total_seconds if total_seconds > 0 else 3600  # Default 1 hour

    def _run_completion_hook(self, hook_command: str, info_hash: str) -> None:
        """
        Run shell command on download completion.

        Args:
            hook_command: Shell command to execute
            info_hash: Torrent info hash (available as $HASH)
        """
        import subprocess

        try:
            env = {"HASH": info_hash}
            subprocess.run(
                hook_command,
                shell=True,
                env=env,
                timeout=30,
                check=False,
            )
            logger.info(f"Completion hook executed: {hook_command}")
        except Exception as e:
            logger.error(f"Completion hook failed: {e}")

    def _handle_interrupt(self, signum: int, frame: Any) -> None:
        """Handle interrupt signals gracefully."""
        logger.warning("Interrupt signal received, stopping downloads...")
        for wrapper in self.active_downloads.values():
            wrapper.stop(graceful=True)
        sys.exit(1)

    def list_sessions(self, status_filter: str) -> List[Any]:
        """
        List active/resumable sessions.

        Args:
            status_filter: Filter by status (active, paused, all)

        Returns:
            List of session records
        """
        if status_filter == "all":
            cursor = self.db_conn.cursor()
            cursor.execute("SELECT * FROM sessions ORDER BY started_at DESC")
            return [dict(row) for row in cursor.fetchall()]
        else:
            return queries.get_active_sessions(self.db_conn)

    def resume(self, hash_or_name: str) -> DownloadResult:
        """
        Resume a paused download.

        Args:
            hash_or_name: Info hash or torrent name

        Returns:
            DownloadResult
        """
        # Find session by hash
        session = queries.get_session(self.db_conn, hash_or_name)

        if not session:
            # Try to find by name (fuzzy match)
            logger.error(f"Session not found: {hash_or_name}")
            return DownloadResult(
                success=False,
                name="Unknown",
                size_bytes=0,
                progress_percent=0.0,
                error="Session not found",
            )

        # Resume download
        logger.info(f"Resuming download: {session['hash'][:16]}...")
        return self.download(
            source=session["magnet_uri"],
            profile=session["profile"] or self.config.general.default_profile,
            select_files=False,
            fetch_trackers=False,
            timeout=None,
            on_complete_hook=None,
        )

    def pause(self, hash_or_name: str) -> None:
        """
        Pause an active download.

        Args:
            hash_or_name: Info hash or torrent name
        """
        wrapper = self.active_downloads.get(hash_or_name)

        if wrapper:
            wrapper.pause()
            queries.update_session_progress(
                self.db_conn,
                hash=hash_or_name,
                progress_percent=wrapper.last_stats.progress_percent if wrapper.last_stats else 0.0,
                status="paused",
            )
            logger.info(f"Paused download: {hash_or_name[:16]}...")
        else:
            logger.error(f"Active download not found: {hash_or_name}")

    def cancel(self, hash: str, delete_files: bool) -> None:
        """
        Cancel a download and optionally delete files.

        Args:
            hash: Info hash
            delete_files: Whether to delete downloaded files
        """
        wrapper = self.active_downloads.get(hash)

        if wrapper:
            wrapper.stop(graceful=False)
            del self.active_downloads[hash]

            if delete_files:
                # Delete files from download directory
                download = queries.get_download(self.db_conn, hash)
                if download and download["destination"]:
                    import shutil
                    dest_path = Path(download["destination"])
                    if dest_path.exists():
                        shutil.rmtree(dest_path, ignore_errors=True)
                        logger.info(f"Deleted files: {dest_path}")

            queries.complete_session(self.db_conn, hash=hash, success=False)
            logger.info(f"Cancelled download: {hash[:16]}...")
        else:
            logger.error(f"Active download not found: {hash}")

    def clean_sessions(self, older_than: str) -> int:
        """
        Remove old completed sessions.

        Args:
            older_than: Age threshold (e.g., "24h", "7d")

        Returns:
            Number of sessions removed
        """
        hours = self._parse_timeout(older_than) // 3600
        return queries.cleanup_completed_sessions(self.db_conn, hours=hours)

    def get_metadata(self, source: str) -> Any:
        """
        Get torrent metadata without downloading.

        Args:
            source: Magnet URI or .torrent file path

        Returns:
            Metadata dict
        """
        # For magnet URIs, analyze health to get basic info
        if source.startswith("magnet:?"):
            health_result = asyncio.run(self.health_analyzer.analyze(source))
            return {
                "health": health_result.classification.value,
                "seeders": health_result.total_seeders,
                "leechers": health_result.total_leechers,
                "trackers": health_result.total_trackers,
                "responding_trackers": health_result.responding_trackers,
            }
        else:
            raise NotImplementedError(".torrent file parsing not yet implemented")

    def get_history(self, limit: int, profile_filter: Optional[str]) -> List[Any]:
        """
        Get download history from database.

        Args:
            limit: Maximum number of records
            profile_filter: Optional profile filter

        Returns:
            List of download records
        """
        return queries.get_recent_downloads(self.db_conn, limit=limit, profile=profile_filter)

    def get_aggregate_stats(self) -> Any:
        """
        Get aggregate statistics.

        Returns:
            Stats dict
        """
        return queries.get_download_stats(self.db_conn)
