"""
Tracker list management system.

Fetches, caches, and manages public tracker lists from multiple sources.
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx

from torrentcli.trackers.sources import get_sources_for_profile

logger = logging.getLogger(__name__)


@dataclass
class TrackerStats:
    """Statistics for a single tracker."""

    tracker: str
    total_announces: int
    successful_announces: int
    total_peers_found: int
    avg_rtt_ms: float
    last_seen: float  # timestamp
    success_rate: float  # 0.0-1.0


class TrackerManager:
    """
    Manages tracker lists with caching and statistics.

    Fetches tracker lists from multiple sources, caches them locally,
    and tracks performance statistics.
    """

    def __init__(self, config: Any) -> None:
        """
        Initialize tracker manager.

        Args:
            config: Config object with cache_dir and update_interval
        """
        self.config = config

        # Cache directory for tracker lists
        self.cache_dir = Path.home() / ".cache" / "torrentcli"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.cache_file = self.cache_dir / "trackers.json"
        self.update_interval = getattr(
            config, "tracker_update_interval", 86400
        )  # 24h default

    async def get_trackers(
        self, profile: str = "best", force_update: bool = False
    ) -> List[str]:
        """
        Get tracker list for a profile.

        Args:
            profile: Profile name (best/all/http_only/stable)
            force_update: Force fetch even if cache is fresh

        Returns:
            List of tracker URLs
        """
        # Check cache first
        if not force_update:
            cached = self._load_cache(profile)
            if cached:
                logger.info(f"Using cached trackers for profile '{profile}'")
                return cached

        # Fetch fresh trackers
        logger.info(f"Fetching fresh trackers for profile '{profile}'...")
        trackers = await self._fetch_trackers(profile)

        # Save to cache
        self._save_cache(profile, trackers)

        return trackers

    def _load_cache(self, profile: str) -> Optional[List[str]]:
        """
        Load trackers from cache if fresh enough.

        Args:
            profile: Profile name

        Returns:
            List of trackers if cache is valid, None otherwise
        """
        if not self.cache_file.exists():
            return None

        try:
            with open(self.cache_file, "r") as f:
                cache_data = json.load(f)

            # Check if this profile is cached
            if profile not in cache_data:
                return None

            profile_data = cache_data[profile]

            # Check freshness
            cached_at = profile_data.get("fetched_at", 0)
            age = time.time() - cached_at

            if age > self.update_interval:
                logger.debug(
                    f"Cache for '{profile}' is stale ({age / 3600:.1f}h old)"
                )
                return None

            trackers = profile_data.get("trackers", [])
            logger.debug(f"Loaded {len(trackers)} trackers from cache")
            return trackers

        except Exception as e:
            logger.warning(f"Failed to load cache: {e}")
            return None

    def _save_cache(self, profile: str, trackers: List[str]) -> None:
        """
        Save trackers to cache.

        Args:
            profile: Profile name
            trackers: List of tracker URLs
        """
        try:
            # Load existing cache
            cache_data: Dict[str, Any] = {}
            if self.cache_file.exists():
                with open(self.cache_file, "r") as f:
                    cache_data = json.load(f)

            # Update this profile
            cache_data[profile] = {
                "fetched_at": time.time(),
                "trackers": trackers,
            }

            # Save
            with open(self.cache_file, "w") as f:
                json.dump(cache_data, f, indent=2)

            logger.debug(f"Saved {len(trackers)} trackers to cache")

        except Exception as e:
            logger.warning(f"Failed to save cache: {e}")

    async def _fetch_trackers(self, profile: str) -> List[str]:
        """
        Fetch tracker lists from sources.

        Args:
            profile: Profile name

        Returns:
            Merged and deduplicated tracker list
        """
        sources = get_sources_for_profile(profile)

        # Fetch from all sources in parallel
        tasks = [self._fetch_single_source(url) for url in sources]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Merge and deduplicate
        all_trackers: List[str] = []
        for result in results:
            if isinstance(result, list):
                all_trackers.extend(result)
            elif isinstance(result, Exception):
                logger.warning(f"Failed to fetch source: {result}")

        # Deduplicate (case-insensitive)
        seen = set()
        unique_trackers = []
        for tracker in all_trackers:
            tracker_lower = tracker.lower()
            if tracker_lower not in seen:
                seen.add(tracker_lower)
                unique_trackers.append(tracker)

        logger.info(
            f"Fetched {len(unique_trackers)} unique trackers from {len(sources)} sources"
        )

        return unique_trackers

    async def _fetch_single_source(self, url: str, timeout: int = 10) -> List[str]:
        """
        Fetch tracker list from a single source.

        Args:
            url: Source URL
            timeout: Request timeout in seconds

        Returns:
            List of tracker URLs
        """
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(url, follow_redirects=True)
                response.raise_for_status()

                # Parse response (newline-separated list)
                content = response.text

                # Split by newlines, filter empty and comments
                trackers = [
                    line.strip()
                    for line in content.split("\n")
                    if line.strip() and not line.startswith("#")
                ]

                # Filter valid tracker URLs
                valid_trackers = [
                    t
                    for t in trackers
                    if t.startswith(("http://", "https://", "udp://"))
                ]

                logger.debug(f"Fetched {len(valid_trackers)} trackers from {url}")
                return valid_trackers

        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            raise

    def update_tracker_lists(self, force: bool = False) -> int:
        """
        Manually update all tracker lists.

        Args:
            force: Force update even if cache is fresh

        Returns:
            Total number of trackers fetched
        """
        # Run async fetch synchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            trackers = loop.run_until_complete(self.get_trackers("all", force_update=force))
            return len(trackers)
        finally:
            loop.close()

    def get_tracker_stats(self, limit: int = 20) -> List[TrackerStats]:
        """
        Get tracker performance statistics.

        Args:
            limit: Maximum number of results

        Returns:
            List of TrackerStats sorted by success rate
        """
        # TODO: Implement when database layer is ready
        # For now, return empty list
        logger.warning("Tracker stats not yet implemented (requires database)")
        return []

    def append_to_magnet(self, magnet: str, trackers: List[str]) -> str:
        """
        Append tracker list to magnet URI.

        Args:
            magnet: Original magnet URI
            trackers: List of tracker URLs to add

        Returns:
            Modified magnet URI with additional trackers
        """
        from urllib.parse import quote

        # Append &tr=<encoded_tracker> for each tracker
        for tracker in trackers:
            encoded = quote(tracker, safe="")
            magnet += f"&tr={encoded}"

        return magnet

    def inject_trackers_to_file(
        self, torrent_file: Path, trackers: List[str]
    ) -> None:
        """
        Inject additional trackers into .torrent file.

        This would require bencoding manipulation.
        For MVP, not implemented - use --bt-tracker aria2c option instead.

        Args:
            torrent_file: Path to .torrent file
            trackers: List of trackers to add
        """
        raise NotImplementedError(
            "Direct .torrent file modification not yet supported. "
            "Use aria2c's --bt-tracker option instead."
        )
