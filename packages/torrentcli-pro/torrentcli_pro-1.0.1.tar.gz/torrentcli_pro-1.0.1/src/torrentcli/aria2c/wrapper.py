"""
aria2c subprocess wrapper with robust error handling.

Spawns aria2c as a subprocess, monitors output, and provides
a simple API for controlling downloads.
"""

import logging
import os
import re
import shutil
import signal
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class Aria2cStats:
    """Real-time statistics from aria2c."""

    download_speed: float  # bytes/sec
    upload_speed: float
    downloaded: int  # bytes
    total_size: int
    connections: int
    seeders: int
    progress_percent: float
    eta_seconds: int
    status: str  # "downloading", "seeding", "paused", "complete", "error"


class Aria2cWrapper:
    """
    Wrapper for aria2c subprocess.

    Manages lifecycle of aria2c process, parses stdout for statistics,
    and provides control methods.
    """

    # Regex patterns for parsing aria2c output
    PROGRESS_PATTERN = re.compile(
        r"\[#[a-f0-9]+\s+([\d.]+[KMGT]?i?B)/([\d.]+[KMGT]?i?B)\((\d+)%\)"
        r".*?CN:(\d+).*?(?:SD:(\d+))?"
        r".*?DL:([\d.]+[KMGT]?i?B)(?:.*?ETA:([\dhms]+))?"
    )

    def __init__(
        self,
        magnet_or_torrent: str,
        download_dir: Path,
        aria2c_options: Dict[str, Any],
        session_file: Optional[Path] = None,
    ) -> None:
        """
        Initialize aria2c wrapper.

        Args:
            magnet_or_torrent: Magnet URI or path to .torrent file
            download_dir: Directory to save downloads
            aria2c_options: Dict of aria2c options (from profile)
            session_file: Optional session file for resume support
        """
        self.source = magnet_or_torrent
        self.download_dir = download_dir
        self.options = aria2c_options
        self.session_file = session_file

        self.process: Optional[subprocess.Popen] = None
        self.last_stats: Optional[Aria2cStats] = None
        self._stdout_lines: List[str] = []

    def _check_aria2c_installed(self) -> None:
        """Verify aria2c is installed and accessible."""
        if not shutil.which("aria2c"):
            raise RuntimeError(
                "aria2c not found in PATH. Install with:\n"
                "  macOS: brew install aria2\n"
                "  Ubuntu/Debian: sudo apt install aria2\n"
                "  Arch: sudo pacman -S aria2"
            )

    def _build_command(self) -> List[str]:
        """Build aria2c command with options."""
        cmd = ["aria2c"]

        # Add download directory
        cmd.extend(["--dir", str(self.download_dir)])

        # Add session file if resuming
        if self.session_file and self.session_file.exists():
            cmd.extend(["--input-file", str(self.session_file)])
            cmd.extend(["--save-session", str(self.session_file)])
        elif self.session_file:
            # Create new session file for future resume
            self.session_file.parent.mkdir(parents=True, exist_ok=True)
            cmd.extend(["--save-session", str(self.session_file)])
            cmd.extend(["--save-session-interval", "10"])  # Save every 10s

        # Add options from profile
        for key, value in self.options.items():
            option_name = f"--{key}"

            if isinstance(value, bool):
                if value:  # Only add flag if True
                    cmd.append(option_name)
            elif isinstance(value, (int, float, str)):
                cmd.extend([option_name, str(value)])
            else:
                logger.warning(f"Skipping unsupported option type: {key}={value}")

        # Add source (magnet or torrent file)
        cmd.append(self.source)

        return cmd

    def start(self) -> None:
        """Start aria2c subprocess."""
        self._check_aria2c_installed()

        cmd = self._build_command()
        logger.info(f"Starting aria2c: {' '.join(cmd[:5])}...")  # Log first 5 args

        try:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,  # Line buffered
                universal_newlines=True,
            )
        except Exception as e:
            raise RuntimeError(f"Failed to start aria2c: {e}")

    def poll_stats(self) -> Optional[Aria2cStats]:
        """
        Poll aria2c output and return latest statistics.

        Returns:
            Aria2cStats if available, None if no new data
        """
        if not self.process or not self.process.stdout:
            return None

        # Read available lines (non-blocking)
        try:
            # Check if process is still running
            if self.process.poll() is not None:
                # Process exited
                exit_code = self.process.returncode
                if exit_code == 0:
                    self.last_stats = Aria2cStats(
                        download_speed=0,
                        upload_speed=0,
                        downloaded=self.last_stats.total_size
                        if self.last_stats
                        else 0,
                        total_size=self.last_stats.total_size if self.last_stats else 0,
                        connections=0,
                        seeders=0,
                        progress_percent=100.0,
                        eta_seconds=0,
                        status="complete",
                    )
                else:
                    if self.last_stats:
                        self.last_stats.status = "error"
                    else:
                        self.last_stats = Aria2cStats(
                            download_speed=0,
                            upload_speed=0,
                            downloaded=0,
                            total_size=0,
                            connections=0,
                            seeders=0,
                            progress_percent=0,
                            eta_seconds=0,
                            status="error",
                        )
                return self.last_stats

            # Read new lines
            while True:
                line = self.process.stdout.readline()
                if not line:
                    break

                line = line.strip()
                if line:
                    self._stdout_lines.append(line)
                    self._parse_line(line)

        except Exception as e:
            logger.error(f"Error polling aria2c stats: {e}")

        return self.last_stats

    def _parse_line(self, line: str) -> None:
        """Parse a line of aria2c output and update stats."""
        # Try to match progress pattern
        match = self.PROGRESS_PATTERN.search(line)
        if match:
            downloaded_str = match.group(1)
            total_str = match.group(2)
            progress = int(match.group(3))
            connections = int(match.group(4))
            seeders = int(match.group(5)) if match.group(5) else 0
            speed_str = match.group(6)
            eta_str = match.group(7) if match.group(7) else "0s"

            # Convert sizes to bytes
            downloaded = self._parse_size(downloaded_str)
            total_size = self._parse_size(total_str)
            download_speed = self._parse_speed(speed_str)
            eta_seconds = self._parse_eta(eta_str)

            self.last_stats = Aria2cStats(
                download_speed=download_speed,
                upload_speed=0,  # aria2c doesn't show upload in this format
                downloaded=downloaded,
                total_size=total_size,
                connections=connections,
                seeders=seeders,
                progress_percent=float(progress),
                eta_seconds=eta_seconds,
                status="downloading" if download_speed > 0 else "stalled",
            )

    @staticmethod
    def _parse_size(size_str: str) -> int:
        """Convert size string (e.g., '2.3GiB') to bytes."""
        size_str = size_str.strip()

        # Extract number and unit
        match = re.match(r"([\d.]+)([KMGT]?i?B)", size_str)
        if not match:
            return 0

        value = float(match.group(1))
        unit = match.group(2)

        multipliers = {
            "B": 1,
            "KiB": 1024,
            "MiB": 1024**2,
            "GiB": 1024**3,
            "TiB": 1024**4,
            "KB": 1000,
            "MB": 1000**2,
            "GB": 1000**3,
            "TB": 1000**4,
        }

        return int(value * multipliers.get(unit, 1))

    @staticmethod
    def _parse_speed(speed_str: str) -> float:
        """Convert speed string (e.g., '5.2MiB') to bytes/sec."""
        # Speed is typically shown as 'X.XMiB' (per second implied)
        return float(Aria2cWrapper._parse_size(speed_str))

    @staticmethod
    def _parse_eta(eta_str: str) -> int:
        """Convert ETA string (e.g., '5m30s') to seconds."""
        if not eta_str or eta_str == "0s":
            return 0

        total_seconds = 0

        # Parse hours
        hours_match = re.search(r"(\d+)h", eta_str)
        if hours_match:
            total_seconds += int(hours_match.group(1)) * 3600

        # Parse minutes
        minutes_match = re.search(r"(\d+)m", eta_str)
        if minutes_match:
            total_seconds += int(minutes_match.group(1)) * 60

        # Parse seconds
        seconds_match = re.search(r"(\d+)s", eta_str)
        if seconds_match:
            total_seconds += int(seconds_match.group(1))

        return total_seconds

    def pause(self) -> None:
        """Pause download by sending SIGSTOP to process."""
        if self.process:
            os.kill(self.process.pid, signal.SIGSTOP)
            if self.last_stats:
                self.last_stats.status = "paused"

    def resume(self) -> None:
        """Resume paused download by sending SIGCONT."""
        if self.process:
            os.kill(self.process.pid, signal.SIGCONT)
            if self.last_stats:
                self.last_stats.status = "downloading"

    def stop(self, graceful: bool = True) -> int:
        """
        Stop aria2c process.

        Args:
            graceful: If True, send SIGTERM; if False, send SIGKILL

        Returns:
            Exit code of process
        """
        if not self.process:
            return 0

        if graceful:
            self.process.terminate()  # SIGTERM
            try:
                return self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                logger.warning("aria2c did not terminate gracefully, killing...")
                self.process.kill()  # SIGKILL
                return self.process.wait()
        else:
            self.process.kill()
            return self.process.wait()

    def is_running(self) -> bool:
        """Check if aria2c process is still running."""
        return self.process is not None and self.process.poll() is None

    def get_exit_code(self) -> Optional[int]:
        """Get exit code if process has terminated."""
        if self.process:
            return self.process.poll()
        return None

    def get_logs(self, last_n: int = 50) -> List[str]:
        """
        Get last N lines of aria2c output.

        Args:
            last_n: Number of lines to return

        Returns:
            List of log lines
        """
        return self._stdout_lines[-last_n:]

    def __enter__(self) -> "Aria2cWrapper":
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit - ensure cleanup."""
        self.stop(graceful=True)
