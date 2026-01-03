"""
Torrent health analyzer.

Analyzes torrent health by:
1. Querying DHT for peer count
2. Testing trackers for seeder/leecher counts
3. Classifying health (HEALTHY, MODERATE, RARE, DEAD)
"""

import asyncio
import logging
import re
import tempfile
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Optional, Tuple
from urllib.parse import quote, urlencode, urlparse

import httpx

from torrentcli.aria2c.wrapper import Aria2cWrapper
from torrentcli.types import TorrentHealth

logger = logging.getLogger(__name__)


class HealthConfidence(Enum):
    """Confidence level in health assessment."""

    LOW = "low"  # DHT only, no tracker responses
    MEDIUM = "medium"  # 1-4 trackers responded
    HIGH = "high"  # 5+ trackers responded


@dataclass
class TrackerResponse:
    """Response from a tracker announce."""

    tracker_url: str
    seeders: int
    leechers: int
    response_time_ms: float
    success: bool
    error: Optional[str] = None


@dataclass
class HealthAnalysisResult:
    """Complete health analysis result."""

    classification: TorrentHealth
    total_seeders: int
    total_leechers: int
    responding_trackers: int
    total_trackers: int
    confidence: HealthConfidence
    analysis_time_sec: float
    tracker_responses: List[TrackerResponse]


class TorrentHealthAnalyzer:
    """Analyzes torrent health before downloading."""

    def __init__(self, dht_timeout: int = 5, tracker_timeout: int = 3) -> None:
        """
        Initialize health analyzer.

        Args:
            dht_timeout: Timeout for DHT query (seconds)
            tracker_timeout: Timeout for each tracker query (seconds)
        """
        self.dht_timeout = dht_timeout
        self.tracker_timeout = tracker_timeout

    async def analyze(
        self, magnet_or_torrent: str, extra_trackers: Optional[List[str]] = None
    ) -> HealthAnalysisResult:
        """
        Perform complete health analysis.

        Args:
            magnet_or_torrent: Magnet URI or .torrent file path
            extra_trackers: Additional trackers to test

        Returns:
            HealthAnalysisResult with classification and details
        """
        start_time = time.time()

        # Extract info hash and trackers
        info_hash, trackers = self._parse_source(magnet_or_torrent)

        # Add extra trackers if provided
        if extra_trackers:
            trackers.extend(extra_trackers)

        # Remove duplicates
        trackers = list(set(trackers))

        logger.info(
            f"Analyzing torrent health: {info_hash[:16]}... ({len(trackers)} trackers)"
        )

        # Query trackers in parallel
        tracker_responses = await self._query_trackers(info_hash, trackers)

        # Aggregate results
        total_seeders = sum(r.seeders for r in tracker_responses if r.success)
        total_leechers = sum(r.leechers for r in tracker_responses if r.success)
        responding = sum(1 for r in tracker_responses if r.success)

        # Determine confidence
        if responding >= 5:
            confidence = HealthConfidence.HIGH
        elif responding >= 1:
            confidence = HealthConfidence.MEDIUM
        else:
            confidence = HealthConfidence.LOW

        # Classify health
        if total_seeders > 10:
            classification = TorrentHealth.HEALTHY
        elif total_seeders >= 1:
            classification = TorrentHealth.MODERATE
        elif total_leechers > 0 or responding == 0:
            # Leechers present OR no trackers responded (might work via DHT)
            classification = TorrentHealth.RARE
        else:
            classification = TorrentHealth.DEAD

        analysis_time = time.time() - start_time

        return HealthAnalysisResult(
            classification=classification,
            total_seeders=total_seeders,
            total_leechers=total_leechers,
            responding_trackers=responding,
            total_trackers=len(trackers),
            confidence=confidence,
            analysis_time_sec=analysis_time,
            tracker_responses=tracker_responses,
        )

    def _parse_source(self, source: str) -> Tuple[str, List[str]]:
        """
        Extract info hash and tracker list from magnet or .torrent.

        Args:
            source: Magnet URI or .torrent file path

        Returns:
            (info_hash, list of tracker URLs)
        """
        if source.startswith("magnet:?"):
            return self._parse_magnet(source)
        else:
            # For .torrent files, we'd need to parse bencoding
            # For MVP, raise NotImplementedError
            raise NotImplementedError(
                "Health analysis for .torrent files not yet implemented. "
                "Use magnet URIs for now."
            )

    def _parse_magnet(self, magnet: str) -> Tuple[str, List[str]]:
        """
        Parse magnet URI to extract info hash and trackers.

        Args:
            magnet: Magnet URI string

        Returns:
            (info_hash, list of tracker URLs)
        """
        # Extract info hash (xt=urn:btih:HASH)
        hash_match = re.search(r"xt=urn:btih:([a-fA-F0-9]{40}|[A-Za-z0-9]{32})", magnet)
        if not hash_match:
            raise ValueError("Invalid magnet URI: no info hash found")

        info_hash = hash_match.group(1).lower()

        # Extract trackers (tr=URL)
        trackers = re.findall(r"tr=([^&]+)", magnet)
        trackers = [self._url_decode(t) for t in trackers]

        return info_hash, trackers

    @staticmethod
    def _url_decode(url: str) -> str:
        """URL-decode a string."""
        from urllib.parse import unquote

        return unquote(url)

    async def _query_trackers(
        self, info_hash: str, trackers: List[str]
    ) -> List[TrackerResponse]:
        """
        Query all trackers in parallel.

        Args:
            info_hash: Torrent info hash (hex)
            trackers: List of tracker URLs

        Returns:
            List of TrackerResponse objects
        """
        # Limit concurrency to avoid overwhelming network
        semaphore = asyncio.Semaphore(10)

        async def query_with_semaphore(tracker: str) -> TrackerResponse:
            async with semaphore:
                return await self._query_single_tracker(info_hash, tracker)

        tasks = [query_with_semaphore(t) for t in trackers]
        return await asyncio.gather(*tasks)

    async def _query_single_tracker(
        self, info_hash: str, tracker_url: str
    ) -> TrackerResponse:
        """
        Query a single tracker.

        Args:
            info_hash: Torrent info hash (hex)
            tracker_url: Tracker URL

        Returns:
            TrackerResponse
        """
        start_time = time.time()

        # Parse tracker protocol
        parsed = urlparse(tracker_url)

        if parsed.scheme in ["http", "https"]:
            return await self._query_http_tracker(
                info_hash, tracker_url, start_time
            )
        elif parsed.scheme == "udp":
            # UDP trackers require binary protocol, complex to implement
            # For MVP, skip UDP trackers
            logger.debug(f"Skipping UDP tracker (not yet supported): {tracker_url}")
            return TrackerResponse(
                tracker_url=tracker_url,
                seeders=0,
                leechers=0,
                response_time_ms=0,
                success=False,
                error="UDP tracker not yet supported",
            )
        else:
            return TrackerResponse(
                tracker_url=tracker_url,
                seeders=0,
                leechers=0,
                response_time_ms=0,
                success=False,
                error=f"Unsupported tracker protocol: {parsed.scheme}",
            )

    async def _query_http_tracker(
        self, info_hash: str, tracker_url: str, start_time: float
    ) -> TrackerResponse:
        """
        Query HTTP/HTTPS tracker.

        Args:
            info_hash: Info hash (hex string)
            tracker_url: Tracker base URL
            start_time: Query start time

        Returns:
            TrackerResponse
        """
        # Convert hex hash to URL-encoded bytes
        info_hash_bytes = bytes.fromhex(info_hash)
        info_hash_encoded = quote(info_hash_bytes, safe="")

        # Build announce URL with query parameters
        params = {
            "info_hash": info_hash_encoded,
            "peer_id": "-TC0100-" + "0" * 12,  # Fake peer ID
            "port": 6881,
            "uploaded": 0,
            "downloaded": 0,
            "left": 1000000000,  # Fake "left" to download
            "compact": 1,
            "event": "started",
        }

        # Manually build query string (urlencode doesn't handle info_hash correctly)
        query_parts = [f"{k}={v}" if k != "info_hash" else f"info_hash={info_hash_encoded}" for k, v in params.items()]
        query_string = "&".join(query_parts)

        announce_url = f"{tracker_url}?{query_string}"

        try:
            async with httpx.AsyncClient(timeout=self.tracker_timeout) as client:
                response = await client.get(announce_url, follow_redirects=True)

                response_time = (time.time() - start_time) * 1000  # ms

                if response.status_code != 200:
                    return TrackerResponse(
                        tracker_url=tracker_url,
                        seeders=0,
                        leechers=0,
                        response_time_ms=response_time,
                        success=False,
                        error=f"HTTP {response.status_code}",
                    )

                # Parse bencoded response
                # For MVP, use simple regex parsing (not proper bencoding)
                content = response.content

                # Try to extract 'complete' (seeders) and 'incomplete' (leechers)
                # Bencoded format: d8:completei5e10:incompletei3e...e
                seeders_match = re.search(rb"8:completei(\d+)e", content)
                leechers_match = re.search(rb"10:incompletei(\d+)e", content)

                seeders = int(seeders_match.group(1)) if seeders_match else 0
                leechers = int(leechers_match.group(1)) if leechers_match else 0

                return TrackerResponse(
                    tracker_url=tracker_url,
                    seeders=seeders,
                    leechers=leechers,
                    response_time_ms=response_time,
                    success=True,
                )

        except asyncio.TimeoutError:
            response_time = (time.time() - start_time) * 1000
            return TrackerResponse(
                tracker_url=tracker_url,
                seeders=0,
                leechers=0,
                response_time_ms=response_time,
                success=False,
                error="Timeout",
            )
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return TrackerResponse(
                tracker_url=tracker_url,
                seeders=0,
                leechers=0,
                response_time_ms=response_time,
                success=False,
                error=str(e)[:50],  # Truncate error message
            )

    def classify_from_seeders(self, seeder_count: int) -> TorrentHealth:
        """
        Simple classification based on seeder count.

        Args:
            seeder_count: Number of seeders

        Returns:
            TorrentHealth classification
        """
        if seeder_count > 10:
            return TorrentHealth.HEALTHY
        elif seeder_count >= 1:
            return TorrentHealth.MODERATE
        elif seeder_count == 0:
            return TorrentHealth.RARE
        else:
            return TorrentHealth.DEAD
