# GID Seminars - Database Handler
"""SQLite database operations for seminar storage and caching."""

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Generator

from .exceptions import DatabaseError
from .models import Seminar, SourceRun, SourceRunStatus
from .utils import DEFAULT_DAYS_AHEAD, DEFAULT_DAYS_BEHIND


class SeminarDatabase:
    """SQLite database handler for seminars."""

    SCHEMA_VERSION = 1

    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    @contextmanager
    def connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise DatabaseError(f"Database error: {e}") from e
        finally:
            conn.close()

    def _ensure_schema(self) -> None:
        """Create tables if they don't exist."""
        with self.connection() as conn:
            cursor = conn.cursor()

            # Main seminars table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS seminars (
                    id TEXT PRIMARY KEY,
                    source_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    url TEXT,
                    start_datetime TEXT NOT NULL,
                    end_datetime TEXT,
                    timezone TEXT DEFAULT 'America/New_York',
                    location TEXT,
                    organizer TEXT,
                    category TEXT,
                    tags TEXT,
                    access_restriction TEXT DEFAULT 'Public',
                    registration_url TEXT,
                    recording_url TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    checksum TEXT,
                    raw_data TEXT
                )
            """)

            # Source run history
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS source_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_id TEXT NOT NULL,
                    run_started_at TEXT NOT NULL,
                    run_completed_at TEXT,
                    status TEXT NOT NULL,
                    events_found INTEGER DEFAULT 0,
                    events_added INTEGER DEFAULT 0,
                    events_updated INTEGER DEFAULT 0,
                    events_removed INTEGER DEFAULT 0,
                    etag TEXT,
                    last_modified TEXT,
                    content_hash TEXT,
                    error_message TEXT,
                    duration_seconds REAL
                )
            """)

            # HTTP cache for conditional requests
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS http_cache (
                    url TEXT PRIMARY KEY,
                    etag TEXT,
                    last_modified TEXT,
                    content_hash TEXT,
                    cached_at TEXT NOT NULL
                )
            """)

            # Indexes
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_seminars_source ON seminars(source_id)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_seminars_start ON seminars(start_datetime)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_seminars_category ON seminars(category)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_source_runs_source ON source_runs(source_id)"
            )

    # =========================================================================
    # Seminar Operations
    # =========================================================================

    def upsert_seminar(self, seminar: Seminar) -> tuple[bool, str]:
        """
        Insert or update a seminar.

        Returns:
            Tuple of (is_new, change_type) where change_type is 'added', 'updated', or 'unchanged'
        """
        with self.connection() as conn:
            cursor = conn.cursor()

            # Check if seminar exists
            cursor.execute("SELECT checksum FROM seminars WHERE id = ?", (seminar.id,))
            row = cursor.fetchone()

            now = datetime.utcnow().isoformat()
            tags_json = json.dumps(seminar.tags)
            raw_data_json = json.dumps(seminar.raw_data) if seminar.raw_data else None

            if row is None:
                # Insert new seminar
                cursor.execute(
                    """
                    INSERT INTO seminars (
                        id, source_id, title, description, url,
                        start_datetime, end_datetime, timezone, location, organizer,
                        category, tags, access_restriction, registration_url, recording_url,
                        created_at, updated_at, checksum, raw_data
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        seminar.id,
                        seminar.source_id,
                        seminar.title,
                        seminar.description,
                        seminar.url,
                        seminar.start_datetime.isoformat(),
                        seminar.end_datetime.isoformat() if seminar.end_datetime else None,
                        seminar.timezone,
                        seminar.location,
                        seminar.organizer,
                        seminar.category,
                        tags_json,
                        seminar.access_restriction,
                        seminar.registration_url,
                        seminar.recording_url,
                        now,
                        now,
                        seminar.checksum,
                        raw_data_json,
                    ),
                )
                return True, "added"

            else:
                # Check if content changed
                if row["checksum"] == seminar.checksum:
                    return False, "unchanged"

                # Update existing seminar
                cursor.execute(
                    """
                    UPDATE seminars SET
                        title = ?, description = ?, url = ?,
                        start_datetime = ?, end_datetime = ?, timezone = ?,
                        location = ?, organizer = ?, category = ?, tags = ?,
                        access_restriction = ?, registration_url = ?, recording_url = ?,
                        updated_at = ?, checksum = ?, raw_data = ?
                    WHERE id = ?
                """,
                    (
                        seminar.title,
                        seminar.description,
                        seminar.url,
                        seminar.start_datetime.isoformat(),
                        seminar.end_datetime.isoformat() if seminar.end_datetime else None,
                        seminar.timezone,
                        seminar.location,
                        seminar.organizer,
                        seminar.category,
                        tags_json,
                        seminar.access_restriction,
                        seminar.registration_url,
                        seminar.recording_url,
                        now,
                        seminar.checksum,
                        raw_data_json,
                        seminar.id,
                    ),
                )
                return False, "updated"

    def get_seminar_by_id(self, seminar_id: str) -> Seminar | None:
        """Retrieve a seminar by ID."""
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM seminars WHERE id = ?", (seminar_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_seminar(row)
            return None

    def get_seminars_in_window(
        self,
        days_behind: int = DEFAULT_DAYS_BEHIND,
        days_ahead: int = DEFAULT_DAYS_AHEAD,
        source_ids: list[str] | None = None,
        categories: list[str] | None = None,
    ) -> list[Seminar]:
        """Get seminars within the specified time window."""
        now = datetime.utcnow()
        start_date = (now - timedelta(days=days_behind)).isoformat()
        end_date = (now + timedelta(days=days_ahead)).isoformat()

        with self.connection() as conn:
            cursor = conn.cursor()

            query = """
                SELECT * FROM seminars
                WHERE start_datetime >= ? AND start_datetime <= ?
            """
            params: list[Any] = [start_date, end_date]

            if source_ids:
                placeholders = ",".join("?" * len(source_ids))
                query += f" AND source_id IN ({placeholders})"
                params.extend(source_ids)

            if categories:
                placeholders = ",".join("?" * len(categories))
                query += f" AND category IN ({placeholders})"
                params.extend(categories)

            query += " ORDER BY start_datetime ASC"

            cursor.execute(query, params)
            return [self._row_to_seminar(row) for row in cursor.fetchall()]

    def get_seminars_by_source(self, source_id: str) -> list[Seminar]:
        """Get all seminars from a specific source."""
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM seminars WHERE source_id = ? ORDER BY start_datetime",
                (source_id,),
            )
            return [self._row_to_seminar(row) for row in cursor.fetchall()]

    def delete_stale_seminars(self, source_id: str, current_ids: list[str]) -> int:
        """Delete seminars from source that are no longer present in the feed."""
        if not current_ids:
            return 0

        with self.connection() as conn:
            cursor = conn.cursor()

            # Get count of seminars to delete
            placeholders = ",".join("?" * len(current_ids))
            cursor.execute(
                f"""
                SELECT COUNT(*) FROM seminars
                WHERE source_id = ? AND id NOT IN ({placeholders})
            """,
                [source_id] + current_ids,
            )
            count = cursor.fetchone()[0]

            # Delete stale seminars
            if count > 0:
                cursor.execute(
                    f"""
                    DELETE FROM seminars
                    WHERE source_id = ? AND id NOT IN ({placeholders})
                """,
                    [source_id] + current_ids,
                )

            return count

    def get_all_categories(self) -> list[str]:
        """Get list of all unique categories."""
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT DISTINCT category FROM seminars WHERE category IS NOT NULL ORDER BY category"
            )
            return [row[0] for row in cursor.fetchall()]

    def get_all_sources(self) -> list[str]:
        """Get list of all unique source IDs."""
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT source_id FROM seminars ORDER BY source_id")
            return [row[0] for row in cursor.fetchall()]

    def get_statistics(self) -> dict[str, Any]:
        """Get database statistics."""
        with self.connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM seminars")
            total = cursor.fetchone()[0]

            cursor.execute(
                "SELECT source_id, COUNT(*) as count FROM seminars GROUP BY source_id"
            )
            by_source = {row["source_id"]: row["count"] for row in cursor.fetchall()}

            cursor.execute(
                "SELECT category, COUNT(*) as count FROM seminars GROUP BY category"
            )
            by_category = {
                row["category"] or "Uncategorized": row["count"]
                for row in cursor.fetchall()
            }

            return {
                "total_seminars": total,
                "by_source": by_source,
                "by_category": by_category,
            }

    def _row_to_seminar(self, row: sqlite3.Row) -> Seminar:
        """Convert a database row to a Seminar model."""
        return Seminar(
            id=row["id"],
            source_id=row["source_id"],
            title=row["title"],
            description=row["description"],
            url=row["url"],
            start_datetime=datetime.fromisoformat(row["start_datetime"]),
            end_datetime=datetime.fromisoformat(row["end_datetime"])
            if row["end_datetime"]
            else None,
            timezone=row["timezone"],
            location=row["location"],
            organizer=row["organizer"],
            category=row["category"],
            tags=json.loads(row["tags"]) if row["tags"] else [],
            access_restriction=row["access_restriction"],
            registration_url=row["registration_url"],
            recording_url=row["recording_url"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            checksum=row["checksum"],
            raw_data=json.loads(row["raw_data"]) if row["raw_data"] else None,
        )

    # =========================================================================
    # Source Run Operations
    # =========================================================================

    def start_source_run(self, source_id: str) -> int:
        """Record the start of a source run. Returns run ID."""
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO source_runs (source_id, run_started_at, status)
                VALUES (?, ?, ?)
            """,
                (source_id, datetime.utcnow().isoformat(), SourceRunStatus.RUNNING.value),
            )
            return cursor.lastrowid or 0

    def complete_source_run(
        self,
        run_id: int,
        status: str,
        events_found: int = 0,
        events_added: int = 0,
        events_updated: int = 0,
        events_removed: int = 0,
        error_message: str | None = None,
        etag: str | None = None,
        content_hash: str | None = None,
    ) -> None:
        """Record the completion of a source run."""
        with self.connection() as conn:
            cursor = conn.cursor()

            # Calculate duration
            cursor.execute(
                "SELECT run_started_at FROM source_runs WHERE id = ?", (run_id,)
            )
            row = cursor.fetchone()
            duration = None
            if row:
                started = datetime.fromisoformat(row["run_started_at"])
                duration = (datetime.utcnow() - started).total_seconds()

            cursor.execute(
                """
                UPDATE source_runs SET
                    run_completed_at = ?,
                    status = ?,
                    events_found = ?,
                    events_added = ?,
                    events_updated = ?,
                    events_removed = ?,
                    error_message = ?,
                    etag = ?,
                    content_hash = ?,
                    duration_seconds = ?
                WHERE id = ?
            """,
                (
                    datetime.utcnow().isoformat(),
                    status,
                    events_found,
                    events_added,
                    events_updated,
                    events_removed,
                    error_message,
                    etag,
                    content_hash,
                    duration,
                    run_id,
                ),
            )

    def get_last_successful_run(self, source_id: str) -> SourceRun | None:
        """Get the most recent successful run for a source."""
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM source_runs
                WHERE source_id = ? AND status = ?
                ORDER BY run_started_at DESC
                LIMIT 1
            """,
                (source_id, SourceRunStatus.SUCCESS.value),
            )
            row = cursor.fetchone()
            if row:
                return SourceRun(
                    id=row["id"],
                    source_id=row["source_id"],
                    run_started_at=datetime.fromisoformat(row["run_started_at"]),
                    run_completed_at=datetime.fromisoformat(row["run_completed_at"])
                    if row["run_completed_at"]
                    else None,
                    status=SourceRunStatus(row["status"]),
                    events_found=row["events_found"],
                    events_added=row["events_added"],
                    events_updated=row["events_updated"],
                    events_removed=row["events_removed"],
                    etag=row["etag"],
                    content_hash=row["content_hash"],
                    error_message=row["error_message"],
                    duration_seconds=row["duration_seconds"],
                )
            return None

    # =========================================================================
    # HTTP Cache Operations
    # =========================================================================

    def get_http_cache(self, url: str) -> dict[str, str | None] | None:
        """Get cached HTTP headers for a URL."""
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT etag, last_modified, content_hash FROM http_cache WHERE url = ?",
                (url,),
            )
            row = cursor.fetchone()
            if row:
                return {
                    "etag": row["etag"],
                    "last_modified": row["last_modified"],
                    "content_hash": row["content_hash"],
                }
            return None

    def update_http_cache(
        self,
        url: str,
        etag: str | None = None,
        last_modified: str | None = None,
        content_hash: str | None = None,
    ) -> None:
        """Update HTTP cache entry."""
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO http_cache (url, etag, last_modified, content_hash, cached_at)
                VALUES (?, ?, ?, ?, ?)
            """,
                (url, etag, last_modified, content_hash, datetime.utcnow().isoformat()),
            )
