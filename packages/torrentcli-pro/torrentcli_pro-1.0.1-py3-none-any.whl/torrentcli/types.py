from enum import Enum

class TorrentHealth(Enum):
    """Torrent health classification."""

    HEALTHY = "healthy"  # >10 seeders
    MODERATE = "moderate"  # 1-10 seeders
    RARE = "rare"  # 0-1 seeders, peers available
    DEAD = "dead"  # 0 peers after full analysis
