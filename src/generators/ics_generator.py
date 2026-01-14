# GID Seminars - ICS Generator
"""Generate iCalendar files from seminars."""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import pytz
from icalendar import Alarm, Calendar, Event
from rich.console import Console

from src.core.database import SeminarDatabase
from src.core.exclusion_filter import ExclusionFilter
from src.core.models import Seminar

console = Console()


class ICSGenerator:
    """Generate iCalendar files from seminars."""

    def __init__(
        self,
        config: dict[str, Any],
        database: SeminarDatabase,
        exclusion_filter: ExclusionFilter | None = None,
    ):
        self.config = config
        self.database = database
        self.exclusion_filter = exclusion_filter
        self.calendar_config = config.get("calendar", {})
        self.time_window = config.get("time_window", {})

    def generate(self, output_path: Path) -> tuple[Path, int]:
        """
        Generate .ics file with seminars in time window.

        Returns:
            Tuple of (output_path, event_count)
        """
        # Create calendar
        cal = Calendar()
        cal.add(
            "prodid",
            self.calendar_config.get("calendar_prodid", "-//GID Seminars//Aggregator//EN"),
        )
        cal.add("version", "2.0")
        cal.add("calscale", "GREGORIAN")
        cal.add("method", "PUBLISH")
        cal.add(
            "x-wr-calname",
            self.calendar_config.get("calendar_name", "GID Seminars"),
        )
        cal.add(
            "x-wr-caldesc",
            self.calendar_config.get("calendar_description", ""),
        )

        # Get seminars in time window
        days_behind = self.time_window.get("days_behind", 30)
        days_ahead = self.time_window.get("days_ahead", 30)

        seminars = self.database.get_seminars_in_window(
            days_behind=days_behind,
            days_ahead=days_ahead,
        )

        # Apply exclusion filter
        if self.exclusion_filter:
            seminars = self.exclusion_filter.filter_seminars(seminars)

        # Add events
        for seminar in seminars:
            event = self._create_event(seminar)
            cal.add_component(event)

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write file
        with open(output_path, "wb") as f:
            f.write(cal.to_ical())

        console.print(f"  Generated ICS with {len(seminars)} events: {output_path.name}")

        return output_path, len(seminars)

    def _create_event(self, seminar: Seminar) -> Event:
        """Create iCalendar Event from Seminar."""
        event = Event()

        # Unique ID
        event.add("uid", f"{seminar.id}@gid-seminars.wnprc.wisc.edu")

        # Timestamps
        event.add("dtstamp", datetime.utcnow())

        # Start time - convert to timezone-aware
        tz = pytz.timezone(seminar.timezone)
        start_dt = tz.localize(seminar.start_datetime.replace(tzinfo=None))
        event.add("dtstart", start_dt)

        # End time
        if seminar.end_datetime:
            end_dt = tz.localize(seminar.end_datetime.replace(tzinfo=None))
            event.add("dtend", end_dt)
        else:
            # Default to 1 hour duration
            event.add("dtend", start_dt + timedelta(hours=1))

        # Title
        event.add("summary", seminar.title)

        # Build description with links
        description_parts = []
        if seminar.description:
            description_parts.append(seminar.description)

        description_parts.append("")  # Blank line

        if seminar.url:
            description_parts.append(f"Event URL: {seminar.url}")
        if seminar.registration_url:
            description_parts.append(f"Registration: {seminar.registration_url}")
        if seminar.recording_url:
            description_parts.append(f"Recording: {seminar.recording_url}")

        description_parts.append("")
        description_parts.append(f"Source: {seminar.source_id}")
        if seminar.access_restriction != "Public":
            description_parts.append(f"Access: {seminar.access_restriction}")

        event.add("description", "\n".join(description_parts))

        # Location
        if seminar.location:
            event.add("location", seminar.location)

        # URL
        if seminar.url:
            event.add("url", seminar.url)

        # Categories
        if seminar.category:
            event.add("categories", [seminar.category])

        # Add reminder
        reminder_mins = self.calendar_config.get("default_reminder_minutes", 60)
        if reminder_mins > 0:
            alarm = Alarm()
            alarm.add("action", "DISPLAY")
            alarm.add("trigger", timedelta(minutes=-reminder_mins))
            alarm.add("description", f"Reminder: {seminar.title}")
            event.add_component(alarm)

        return event
