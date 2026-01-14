# GID Seminars - JSON Generator
"""Generate JSON feed from seminars."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from src.core.database import SeminarDatabase
from src.core.exclusion_filter import ExclusionFilter
from src.core.utils import DEFAULT_DAYS_AHEAD, DEFAULT_DAYS_BEHIND, console


class JSONGenerator:
    """Generate JSON feed from seminars."""

    def __init__(
        self,
        config: dict[str, Any],
        database: SeminarDatabase,
        exclusion_filter: ExclusionFilter | None = None,
    ):
        self.config = config
        self.database = database
        self.exclusion_filter = exclusion_filter
        self.time_window = config.get("time_window", {})

    def generate(self, output_path: Path) -> tuple[Path, int]:
        """
        Generate JSON feed with seminars in time window.

        Returns:
            Tuple of (output_path, event_count)
        """
        # Get seminars in time window
        days_behind = self.time_window.get("days_behind", DEFAULT_DAYS_BEHIND)
        days_ahead = self.time_window.get("days_ahead", DEFAULT_DAYS_AHEAD)

        seminars = self.database.get_seminars_in_window(
            days_behind=days_behind,
            days_ahead=days_ahead,
        )

        # Apply exclusion filter
        if self.exclusion_filter:
            seminars = self.exclusion_filter.filter_seminars(seminars)

        # Get statistics
        stats = self.database.get_statistics()

        # Build JSON structure
        data = {
            "metadata": {
                "title": "GID Seminars Feed",
                "description": "Aggregated seminars and webinars for Global Infectious Disease research",
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "time_window": {
                    "days_behind": days_behind,
                    "days_ahead": days_ahead,
                },
                "total_events": len(seminars),
                "sources": list(stats.get("by_source", {}).keys()),
                "categories": list(stats.get("by_category", {}).keys()),
            },
            "events": [self._seminar_to_dict(s) for s in seminars],
        }

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write file
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)

        console.print(f"  Generated JSON with {len(seminars)} events: {output_path.name}")

        return output_path, len(seminars)

    def _seminar_to_dict(self, seminar: Any) -> dict[str, Any]:
        """Convert Seminar to JSON-serializable dict."""
        return {
            "id": seminar.id,
            "title": seminar.title,
            "description": seminar.description,
            "url": seminar.url,
            "start_datetime": seminar.start_datetime.isoformat(),
            "end_datetime": seminar.end_datetime.isoformat() if seminar.end_datetime else None,
            "timezone": seminar.timezone,
            "location": seminar.location,
            "organizer": seminar.organizer,
            "source": seminar.source_id,
            "category": seminar.category,
            "tags": seminar.tags,
            "access_restriction": seminar.access_restriction,
            "registration_url": seminar.registration_url,
            "recording_url": seminar.recording_url,
        }
