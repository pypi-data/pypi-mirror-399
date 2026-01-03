"""
Database queries for download history and tracker statistics.

Provides CRUD operations for downloads, tracker stats, and session management.
"""

import json
import logging
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from torrentcli.types import TorrentHealth

logger = logging.getLogger(__name__)


# ============================================================================
# DOWNLOADS TABLE OPERATIONS
# ============================================================================


def insert_download(
    conn: sqlite3.Connection,
    hash: str,
    name: str,
    size_bytes: int,
    profile: Optional[str] = None,
    destination: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Insert a new download record.

    Args:
        conn: Database connection
        hash: Torrent info hash
        name: Torrent name
        size_bytes: Total size in bytes
        profile: Profile used for download
        destination: Download destination path
        metadata: Optional JSON metadata
    """
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO downloads (hash, name, size_bytes, profile, destination, metadata)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (hash, name, size_bytes, profile, destination, json.dumps(metadata or {})),
    )
    conn.commit()
    logger.debug(f"Inserted download: {hash[:16]}... ({name})")


def update_download_progress(
    conn: sqlite3.Connection,
    hash: str,
    avg_speed_bps: Optional[float] = None,
    peak_speed_bps: Optional[float] = None,
    seeders_found: Optional[int] = None,
    peers_max: Optional[int] = None,
) -> None:
    """
    Update download progress statistics.

    Args:
        conn: Database connection
        hash: Torrent info hash
        avg_speed_bps: Average download speed
        peak_speed_bps: Peak download speed
        seeders_found: Number of seeders found
        peers_max: Maximum number of peers connected
    """
    cursor = conn.cursor()

    # Build dynamic UPDATE query for provided fields
    updates = []
    values = []

    if avg_speed_bps is not None:
        updates.append("avg_speed_bps = ?")
        values.append(avg_speed_bps)
    if peak_speed_bps is not None:
        updates.append("peak_speed_bps = ?")
        values.append(peak_speed_bps)
    if seeders_found is not None:
        updates.append("seeders_found = ?")
        values.append(seeders_found)
    if peers_max is not None:
        updates.append("peers_max = ?")
        values.append(peers_max)

    if not updates:
        return  # Nothing to update

    values.append(hash)
    query = f"UPDATE downloads SET {', '.join(updates)} WHERE hash = ?"

    cursor.execute(query, values)
    conn.commit()


def complete_download(
    conn: sqlite3.Connection, hash: str, success: bool = True, error_message: Optional[str] = None
) -> None:
    """
    Mark download as completed.

    Args:
        conn: Database connection
        hash: Torrent info hash
        success: Whether download succeeded
        error_message: Error message if failed
    """
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE downloads
        SET completed_at = CURRENT_TIMESTAMP,
            success = ?,
            error_message = ?
        WHERE hash = ?
        """,
        (success, error_message, hash),
    )
    conn.commit()
    logger.info(f"Completed download: {hash[:16]}... (success={success})")


def get_download(conn: sqlite3.Connection, hash: str) -> Optional[Dict[str, Any]]:
    """
    Get download record by hash.

    Args:
        conn: Database connection
        hash: Torrent info hash

    Returns:
        Download record as dict, or None if not found
    """
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM downloads WHERE hash = ?", (hash,))
    row = cursor.fetchone()

    if row:
        return dict(row)
    return None


def get_recent_downloads(
    conn: sqlite3.Connection, limit: int = 50, profile: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get recent downloads ordered by completion time.

    Args:
        conn: Database connection
        limit: Maximum number of results
        profile: Optional profile filter

    Returns:
        List of download records
    """
    cursor = conn.cursor()

    if profile:
        cursor.execute(
            """
            SELECT * FROM downloads
            WHERE profile = ?
            ORDER BY completed_at DESC NULLS FIRST
            LIMIT ?
            """,
            (profile, limit),
        )
    else:
        cursor.execute(
            """
            SELECT * FROM downloads
            ORDER BY completed_at DESC NULLS FIRST
            LIMIT ?
            """,
            (limit,),
        )

    return [dict(row) for row in cursor.fetchall()]


def get_download_stats(conn: sqlite3.Connection) -> Dict[str, Any]:
    """
    Get aggregate download statistics.

    Returns:
        Dict with total_downloads, total_bytes, avg_speed, etc.
    """
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            COUNT(*) as total_downloads,
            COUNT(CASE WHEN success = 1 THEN 1 END) as successful_downloads,
            SUM(size_bytes) as total_bytes,
            AVG(avg_speed_bps) as avg_speed,
            MAX(peak_speed_bps) as max_speed,
            AVG(seeders_found) as avg_seeders
        FROM downloads
        WHERE completed_at IS NOT NULL
        """
    )

    row = cursor.fetchone()
    return dict(row) if row else {}


def delete_old_downloads(conn: sqlite3.Connection, days: int = 90) -> int:
    """
    Delete download records older than specified days.

    Args:
        conn: Database connection
        days: Delete records older than this many days

    Returns:
        Number of records deleted
    """
    cursor = conn.cursor()
    cutoff_date = datetime.now() - timedelta(days=days)

    cursor.execute(
        """
        DELETE FROM downloads
        WHERE completed_at < ?
        """,
        (cutoff_date.isoformat(),),
    )

    deleted = cursor.rowcount
    conn.commit()
    logger.info(f"Deleted {deleted} old download records (older than {days} days)")
    return deleted


# ============================================================================
# TRACKER STATS TABLE OPERATIONS
# ============================================================================


def upsert_tracker_stats(
    conn: sqlite3.Connection,
    tracker: str,
    announce_success: bool,
    peers_found: int = 0,
    response_time_ms: float = 0.0,
) -> None:
    """
    Insert or update tracker statistics.

    Args:
        conn: Database connection
        tracker: Tracker URL
        announce_success: Whether announce succeeded
        peers_found: Number of peers returned
        response_time_ms: Response time in milliseconds
    """
    cursor = conn.cursor()

    # Check if tracker exists
    cursor.execute("SELECT * FROM tracker_stats WHERE tracker = ?", (tracker,))
    existing = cursor.fetchone()

    if existing:
        # Update existing record
        total_announces = existing["total_announces"] + 1
        successful_announces = existing["successful_announces"] + (1 if announce_success else 0)
        total_peers = existing["total_peers_found"] + peers_found

        # Calculate new weighted average response time
        old_avg = existing["avg_response_time_ms"]
        old_count = existing["total_announces"]
        new_avg = (old_avg * old_count + response_time_ms) / total_announces

        cursor.execute(
            """
            UPDATE tracker_stats
            SET total_announces = ?,
                successful_announces = ?,
                total_peers_found = ?,
                avg_response_time_ms = ?,
                last_seen = CURRENT_TIMESTAMP
            WHERE tracker = ?
            """,
            (total_announces, successful_announces, total_peers, new_avg, tracker),
        )
    else:
        # Insert new record
        cursor.execute(
            """
            INSERT INTO tracker_stats (
                tracker, total_announces, successful_announces,
                total_peers_found, avg_response_time_ms, last_seen
            )
            VALUES (?, 1, ?, ?, ?, CURRENT_TIMESTAMP)
            """,
            (tracker, 1 if announce_success else 0, peers_found, response_time_ms),
        )

    conn.commit()


def get_tracker_leaderboard(conn: sqlite3.Connection, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Get top trackers by success rate.

    Args:
        conn: Database connection
        limit: Maximum number of results

    Returns:
        List of tracker stats ordered by success rate
    """
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT *
        FROM tracker_stats
        WHERE total_announces >= 5
        ORDER BY success_rate DESC, total_peers_found DESC
        LIMIT ?
        """,
        (limit,),
    )

    return [dict(row) for row in cursor.fetchall()]


def get_all_tracker_stats(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    """
    Get all tracker statistics.

    Returns:
        List of all tracker stats
    """
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tracker_stats ORDER BY success_rate DESC")
    return [dict(row) for row in cursor.fetchall()]


def cleanup_stale_trackers(conn: sqlite3.Connection, days: int = 30) -> int:
    """
    Remove trackers that haven't been seen in specified days.

    Args:
        conn: Database connection
        days: Remove trackers not seen in this many days

    Returns:
        Number of trackers removed
    """
    cursor = conn.cursor()
    cutoff_date = datetime.now() - timedelta(days=days)

    cursor.execute(
        """
        DELETE FROM tracker_stats
        WHERE last_seen < ?
        """,
        (cutoff_date.isoformat(),),
    )

    deleted = cursor.rowcount
    conn.commit()
    logger.info(f"Cleaned up {deleted} stale trackers (not seen in {days} days)")
    return deleted


# ============================================================================
# SESSIONS TABLE OPERATIONS
# ============================================================================


def create_session(
    conn: sqlite3.Connection,
    hash: str,
    magnet_uri: str,
    download_dir: str,
    profile: Optional[str] = None,
    aria2c_session_file: Optional[str] = None,
) -> None:
    """
    Create a new download session.

    Args:
        conn: Database connection
        hash: Torrent info hash
        magnet_uri: Magnet URI
        download_dir: Download directory
        profile: Profile name
        aria2c_session_file: Path to aria2c session file
    """
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO sessions (hash, magnet_uri, download_dir, profile, aria2c_session_file)
        VALUES (?, ?, ?, ?, ?)
        """,
        (hash, magnet_uri, download_dir, profile, aria2c_session_file),
    )
    conn.commit()
    logger.debug(f"Created session: {hash[:16]}...")


def update_session_progress(
    conn: sqlite3.Connection, hash: str, progress_percent: float, status: str = "active"
) -> None:
    """
    Update session progress and status.

    Args:
        conn: Database connection
        hash: Torrent info hash
        progress_percent: Download progress (0-100)
        status: Session status (active, paused, completed, failed)
    """
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE sessions
        SET progress_percent = ?,
            status = ?,
            last_updated = CURRENT_TIMESTAMP
        WHERE hash = ?
        """,
        (progress_percent, status, hash),
    )
    conn.commit()


def get_active_sessions(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    """
    Get all active or paused sessions.

    Returns:
        List of active session records
    """
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT * FROM sessions
        WHERE status IN ('active', 'paused')
        ORDER BY started_at DESC
        """
    )

    return [dict(row) for row in cursor.fetchall()]


def get_session(conn: sqlite3.Connection, hash: str) -> Optional[Dict[str, Any]]:
    """
    Get session by hash.

    Args:
        conn: Database connection
        hash: Torrent info hash

    Returns:
        Session record or None
    """
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sessions WHERE hash = ?", (hash,))
    row = cursor.fetchone()

    if row:
        return dict(row)
    return None


def complete_session(conn: sqlite3.Connection, hash: str, success: bool = True) -> None:
    """
    Mark session as completed or failed.

    Args:
        conn: Database connection
        hash: Torrent info hash
        success: Whether session completed successfully
    """
    status = "completed" if success else "failed"
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE sessions
        SET status = ?,
            last_updated = CURRENT_TIMESTAMP
        WHERE hash = ?
        """,
        (status, hash),
    )
    conn.commit()
    logger.info(f"Completed session: {hash[:16]}... (status={status})")


def delete_session(conn: sqlite3.Connection, hash: str) -> None:
    """
    Delete a session record.

    Args:
        conn: Database connection
        hash: Torrent info hash
    """
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sessions WHERE hash = ?", (hash,))
    conn.commit()
    logger.debug(f"Deleted session: {hash[:16]}...")


def cleanup_completed_sessions(conn: sqlite3.Connection, hours: int = 24) -> int:
    """
    Remove completed/failed sessions older than specified hours.

    Args:
        conn: Database connection
        hours: Remove sessions completed this many hours ago

    Returns:
        Number of sessions removed
    """
    cursor = conn.cursor()
    cutoff_time = datetime.now() - timedelta(hours=hours)

    cursor.execute(
        """
        DELETE FROM sessions
        WHERE status IN ('completed', 'failed')
        AND last_updated < ?
        """,
        (cutoff_time.isoformat(),),
    )

    deleted = cursor.rowcount
    conn.commit()
    logger.info(f"Cleaned up {deleted} old sessions (older than {hours} hours)")
    return deleted


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def get_database_size(conn: sqlite3.Connection) -> int:
    """
    Get database file size in bytes.

    Returns:
        Database size in bytes
    """
    cursor = conn.cursor()
    cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
    row = cursor.fetchone()
    return row["size"] if row else 0


def export_downloads_csv(conn: sqlite3.Connection, output_path: Path) -> int:
    """
    Export downloads table to CSV file.

    Args:
        conn: Database connection
        output_path: Output CSV file path

    Returns:
        Number of records exported
    """
    import csv

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM downloads ORDER BY started_at DESC")

    rows = cursor.fetchall()
    if not rows:
        return 0

    # Write CSV
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        for row in rows:
            writer.writerow(dict(row))

    logger.info(f"Exported {len(rows)} downloads to {output_path}")
    return len(rows)
