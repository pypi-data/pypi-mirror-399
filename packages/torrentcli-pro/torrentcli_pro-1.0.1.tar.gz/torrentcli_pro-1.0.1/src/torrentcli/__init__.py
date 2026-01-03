"""
TorrentCLI Pro - Hardcore terminal torrent client optimized for rare content.

Wraps aria2c with intelligent health analysis, auto-tracker management,
and distinctive cyberpunk TUI aesthetics.
"""

__version__ = "1.0.0"
__author__ = "TorrentCLI Contributors"
__license__ = "MIT"

# Expose key classes for programmatic use
from torrentcli.config import Config, Profile
from torrentcli.engine import DownloadEngine, DownloadStats, TorrentHealth

__all__ = [
    "__version__",
    "Config",
    "Profile",
    "DownloadEngine",
    "DownloadStats",
    "TorrentHealth",
]
