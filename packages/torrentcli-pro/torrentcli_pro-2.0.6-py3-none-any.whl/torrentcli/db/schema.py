"""
SQLite database schema for download history and tracker statistics.
"""

import logging
import sqlite3
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Database schema version (for future migrations)
SCHEMA_VERSION = 1


def get_db_path() -> Path:
    """Get path to SQLite database file."""
    db_dir = Path.home() / ".local" / "share" / "torrentcli"
    db_dir.mkdir(parents=True, exist_ok=True)
    return db_dir / "history.db"


def init_database(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """
    Initialize database with schema.

    Args:
        db_path: Optional custom database path

    Returns:
        SQLite connection object
    """
    if db_path is None:
        db_path = get_db_path()

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row  # Enable dict-like access

    _create_tables(conn)
    _create_indexes(conn)

    return conn


def _create_tables(conn: sqlite3.Connection) -> None:
    """Create database tables if they don't exist."""
    cursor = conn.cursor()

    # Schema version table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schema_version (
            version INTEGER PRIMARY KEY,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Check current version
    cursor.execute("SELECT version FROM schema_version ORDER BY version DESC LIMIT 1")
    row = cursor.fetchone()
    current_version = row[0] if row else 0

    if current_version < SCHEMA_VERSION:
        logger.info(
            f"Initializing database schema (version {current_version} -> {SCHEMA_VERSION})"
        )

        # Downloads table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS downloads (
                hash TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                size_bytes INTEGER NOT NULL,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                avg_speed_bps REAL,
                peak_speed_bps REAL,
                seeders_found INTEGER DEFAULT 0,
                peers_max INTEGER DEFAULT 0,
                profile TEXT,
                destination TEXT,
                success BOOLEAN DEFAULT TRUE,
                error_message TEXT,
                metadata TEXT  -- JSON blob for extra info
            )
        """)

        # Tracker stats table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tracker_stats (
                tracker TEXT PRIMARY KEY,
                total_announces INTEGER DEFAULT 0,
                successful_announces INTEGER DEFAULT 0,
                total_peers_found INTEGER DEFAULT 0,
                avg_response_time_ms REAL DEFAULT 0.0,
                last_seen TIMESTAMP,
                success_rate REAL GENERATED ALWAYS AS (
                    CASE
                        WHEN total_announces > 0
                        THEN CAST(successful_announces AS REAL) / total_announces
                        ELSE 0.0
                    END
                ) VIRTUAL
            )
        """)

        # Session state table (for resume support)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                hash TEXT PRIMARY KEY,
                magnet_uri TEXT,
                download_dir TEXT,
                profile TEXT,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                progress_percent REAL DEFAULT 0.0,
                status TEXT DEFAULT 'active',  -- active, paused, completed, failed
                aria2c_session_file TEXT,
                FOREIGN KEY (hash) REFERENCES downloads(hash)
            )
        """)

        # Update schema version
        cursor.execute(
            "INSERT OR REPLACE INTO schema_version (version) VALUES (?)",
            (SCHEMA_VERSION,),
        )

        conn.commit()
        logger.info("Database schema initialized successfully")


def _create_indexes(conn: sqlite3.Connection) -> None:
    """Create indexes for common queries."""
    cursor = conn.cursor()

    # Index on downloads.completed_at for history queries
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_downloads_completed
        ON downloads(completed_at DESC)
    """)

    # Index on downloads.profile for profile filtering
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_downloads_profile
        ON downloads(profile)
    """)

    # Index on tracker_stats.success_rate for leaderboard
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_tracker_success_rate
        ON tracker_stats(success_rate DESC)
    """)

    # Index on tracker_stats.last_seen for staleness checks
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_tracker_last_seen
        ON tracker_stats(last_seen DESC)
    """)

    # Index on sessions.status for listing active sessions
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_sessions_status
        ON sessions(status)
    """)

    conn.commit()


def vacuum_database(conn: sqlite3.Connection) -> None:
    """
    Vacuum database to reclaim space and optimize.

    Should be called periodically (e.g., after cleaning old records).
    """
    logger.info("Vacuuming database...")
    conn.execute("VACUUM")
    logger.info("Database vacuumed successfully")


def check_integrity(conn: sqlite3.Connection) -> bool:
    """
    Check database integrity.

    Returns:
        True if database is healthy, False otherwise
    """
    cursor = conn.cursor()
    cursor.execute("PRAGMA integrity_check")
    result = cursor.fetchone()[0]

    if result == "ok":
        logger.info("Database integrity check passed")
        return True
    else:
        logger.error(f"Database integrity check failed: {result}")
        return False
