# GID Seminars - iCal Source
"""iCal/ICS feed parser for calendar subscriptions."""

from datetime import datetime, timedelta
from typing import Any

import pytz
from icalendar import Calendar

from src.core.models import Seminar
from src.core.utils import MAX_DESCRIPTION_LENGTH, console, extract_url_from_text

from .base import BaseSource


class ICalSource(BaseSource):
    """Parse iCal/ICS feeds."""

    def fetch_seminars(self) -> list[Seminar]:
        """Fetch and parse iCal feed."""
        if not self.url:
            console.print("    [yellow]No URL configured[/yellow]")
            return []

        response = self._make_request(self.url)

        try:
            cal = Calendar.from_ical(response.content)
        except Exception as e:
            console.print(f"    [red]Failed to parse iCal: {e}[/red]")
            return []

        seminars = []
        for component in cal.walk():
            if component.name == "VEVENT":
                try:
                    seminar = self._parse_event(component)
                    if seminar:
                        seminars.append(seminar)
                except Exception as e:
                    console.print(f"    [yellow]Error parsing event: {e}[/yellow]")
                    continue

        return seminars

    def _parse_event(self, event: Any) -> Seminar | None:
        """Parse a VEVENT component into a Seminar."""
        # Get title
        title = str(event.get("summary", "")).strip()
        if not title:
            return None

        # Get start datetime
        dtstart = event.get("dtstart")
        if not dtstart:
            return None

        start_datetime = self._parse_ical_datetime(dtstart.dt)
        if not start_datetime:
            return None

        # Get end datetime
        end_datetime = None
        dtend = event.get("dtend")
        if dtend:
            end_datetime = self._parse_ical_datetime(dtend.dt)

        # If no end time, estimate 1 hour duration
        if not end_datetime:
            end_datetime = start_datetime + timedelta(hours=1)

        # Get description
        description = str(event.get("description", "")).strip() or None

        # Get URL - check explicit field first, then look in description
        url = str(event.get("url", "")).strip() or None
        if not url and description:
            url = extract_url_from_text(description)

        # Get location
        location = str(event.get("location", "")).strip() or "Online"

        # Get organizer
        organizer = None
        org = event.get("organizer")
        if org:
            organizer = str(org).replace("mailto:", "")

        # Get categories
        categories = event.get("categories")
        category = self.category
        if categories:
            if hasattr(categories, "cats"):
                cats = categories.cats
                if cats:
                    category = str(cats[0])

        # Get UID for deduplication
        uid = str(event.get("uid", ""))

        return Seminar(
            source_id=self.source_id,
            title=title,
            description=description[:MAX_DESCRIPTION_LENGTH] if description else None,
            url=url,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            timezone=self.default_timezone,
            location=location,
            organizer=organizer,
            category=category,
            raw_data={"uid": uid} if uid else None,
        )

    def _parse_ical_datetime(self, dt: Any) -> datetime | None:
        """Parse iCal datetime to Python datetime."""
        if dt is None:
            return None

        # Handle date-only (all-day events)
        if not isinstance(dt, datetime):
            # It's a date object, convert to datetime at midnight
            return datetime(dt.year, dt.month, dt.day, 0, 0, 0)

        # If timezone-aware, convert to UTC then to naive
        if dt.tzinfo is not None:
            dt = dt.astimezone(pytz.UTC).replace(tzinfo=None)

        return dt
