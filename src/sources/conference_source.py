# GID Seminars - Conference Archive Source
"""Load conference archive entries from TOML file."""

from datetime import datetime
from pathlib import Path
from typing import Any

import toml

from src.core.keyword_filter import KeywordFilter
from src.core.models import Seminar
from src.core.utils import console

from .base import BaseSource


class ConferenceSource(BaseSource):
    """Load conference archives from TOML configuration."""

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
        self.file_path = config.get("file_path", "data/conference_archives.toml")

    def fetch_seminars(self) -> list[Seminar]:
        """Load conference archives from TOML file."""
        full_path = self.base_dir / self.file_path

        if not full_path.exists():
            console.print(f"    [yellow]Conference file not found: {full_path}[/yellow]")
            return []

        try:
            data = toml.load(full_path)
        except Exception as e:
            console.print(f"    [red]Failed to parse conference file: {e}[/red]")
            return []

        seminars = []
        conferences = data.get("conference", [])

        for conf in conferences:
            seminar = self._parse_conference(conf)
            if seminar:
                seminars.append(seminar)

        return seminars

    def _parse_conference(self, conf: dict[str, Any]) -> Seminar | None:
        """Parse a conference entry into a Seminar object."""
        name = conf.get("name", "").strip()
        if not name:
            return None

        url = conf.get("url", "")
        year = conf.get("year", datetime.now().year)
        date_range = conf.get("date_range", "")
        description = conf.get("description", "")
        organizer = conf.get("organizer", "")
        category = conf.get("category", self.category)
        topics = conf.get("topics", [])
        access = conf.get("access", "Free")
        session_count = conf.get("session_count")

        # Build description
        desc_parts = []
        if description:
            desc_parts.append(description)
        if date_range:
            desc_parts.append(f"Conference dates: {date_range}")
        if session_count:
            desc_parts.append(f"Sessions available: ~{session_count}")
        if access:
            desc_parts.append(f"Access: {access}")
        if topics:
            desc_parts.append(f"Topics: {', '.join(topics[:5])}")

        full_description = "\n".join(desc_parts) if desc_parts else None

        # Create a datetime for the conference (use year start as placeholder)
        # This allows sorting by year
        start_datetime = datetime(year, 1, 1, 0, 0, 0)

        return Seminar(
            source_id=self.source_id,
            title=f"[Archive] {name}",
            description=full_description,
            url=url,
            start_datetime=start_datetime,
            timezone="UTC",
            location="Conference Archive",
            organizer=organizer,
            category=f"Conference - {category}" if category else "Conference",
            raw_data={
                "type": "conference_archive",
                "year": year,
                "date_range": date_range,
                "access": access,
                "topics": topics,
            },
        )
