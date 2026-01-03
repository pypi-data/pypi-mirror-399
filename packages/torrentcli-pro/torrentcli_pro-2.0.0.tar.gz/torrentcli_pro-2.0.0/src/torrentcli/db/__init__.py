"""Database layer for history and stats."""

from torrentcli.db.schema import check_integrity, init_database, vacuum_database

__all__ = ["init_database", "vacuum_database", "check_integrity"]
