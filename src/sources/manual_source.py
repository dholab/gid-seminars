# GID Seminars - Manual Source
"""Load manually curated seminar entries from TOML file."""

from datetime import datetime
from pathlib import Path
from typing import Any

import toml
from rich.console import Console

from src.core.keyword_filter import KeywordFilter
from src.core.models import AccessRestriction, Seminar

from .base import BaseSource

console = Console()


class ManualSource(BaseSource):
    """Load seminars from manual TOML entries."""

    def __init__(
        self,
        source_id: str,
        config: dict[str, Any],
        database: Any,
        http_config: dict[str, Any] | None = None,
        keyword_filter: KeywordFilter | None = None,
        base_dir: Path | None = None,
    ):
        super().__init__(source_id, config, database, http_config, keyword_filter)
        self.base_dir = base_dir or Path.cwd()
        self.file_path = self.base_dir / config.get("file_path", "data/manual_seminars.toml")

    def fetch_seminars(self) -> list[Seminar]:
        """Load seminars from TOML file."""
        if not self.file_path.exists():
            console.print(f"    [yellow]Manual entries file not found: {self.file_path}[/yellow]")
            return []

        try:
            data = toml.load(self.file_path)
        except Exception as e:
            console.print(f"    [red]Failed to parse TOML: {e}[/red]")
            return []

        seminars = []
        entries = data.get("seminar", [])

        for entry in entries:
            try:
                seminar = self._parse_entry(entry)
                if seminar:
                    seminars.append(seminar)
            except Exception as e:
                console.print(f"    [yellow]Error parsing entry: {e}[/yellow]")
                continue

        return seminars

    def _parse_entry(self, entry: dict[str, Any]) -> Seminar | None:
        """Parse a manual entry dict into a Seminar."""
        # Required fields
        title = entry.get("title", "").strip()
        if not title:
            return None

        start_datetime_str = entry.get("start_datetime")
        if not start_datetime_str:
            return None

        # Parse start datetime
        start_datetime = self._parse_datetime(start_datetime_str)
        if not start_datetime:
            console.print(f"    [yellow]Could not parse datetime: {start_datetime_str}[/yellow]")
            return None

        # Parse end datetime
        end_datetime = None
        if entry.get("end_datetime"):
            end_datetime = self._parse_datetime(entry["end_datetime"])

        # Parse access restriction
        access_str = entry.get("access_restriction", "Public")
        try:
            access = AccessRestriction(access_str)
        except ValueError:
            access = AccessRestriction.PUBLIC

        # Get tags
        tags = entry.get("tags", [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",")]

        return Seminar(
            source_id=self.source_id,
            title=title,
            description=entry.get("description"),
            url=entry.get("url"),
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            timezone=entry.get("timezone", self.default_timezone),
            location=entry.get("location", "Online"),
            organizer=entry.get("organizer"),
            category=entry.get("category", self.category),
            tags=tags,
            access_restriction=access,
            registration_url=entry.get("registration_url"),
            recording_url=entry.get("recording_url"),
        )

    def _parse_datetime(self, dt_str: str) -> datetime | None:
        """Parse datetime string in various formats."""
        formats = [
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M",
            "%Y-%m-%d %H:%M",
            "%Y-%m-%d",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(dt_str, fmt)
            except ValueError:
                continue

        return None
