# GID Seminars - WHO Events Source
"""Fetch events from WHO API."""

from datetime import datetime
from typing import Any

from src.core.keyword_filter import KeywordFilter
from src.core.models import Seminar
from src.core.utils import console

from .base import BaseSource


class WHOSource(BaseSource):
    """Fetch events from WHO Events API."""

    API_URL = "https://www.who.int/api/hubs/events"
    BASE_EVENT_URL = "https://www.who.int/news-room/events/detail/"

    def __init__(
        self,
        source_id: str,
        config: dict[str, Any],
        database: Any,
        http_config: dict[str, Any] | None = None,
        keyword_filter: KeywordFilter | None = None,
    ):
        super().__init__(source_id, config, database, http_config, keyword_filter)
        self.max_events = config.get("max_events", 50)

    def fetch_seminars(self) -> list[Seminar]:
        """Fetch upcoming events from WHO API."""
        # Build API request
        params = {
            "$orderby": "EventStart asc",
            "$top": self.max_events,
            "$filter": f"EventStart ge {datetime.now().strftime('%Y-%m-%dT00:00:00Z')}",
        }

        # Set JSON accept header
        self.session.headers.update({"Accept": "application/json"})

        try:
            response = self._make_request(self.API_URL, params=params)
            data = response.json()
        except Exception as e:
            console.print(f"    [red]Failed to fetch WHO API: {e}[/red]")
            return []

        events = data.get("value", [])
        seminars = []

        for event in events:
            seminar = self._parse_event(event)
            if seminar:
                seminars.append(seminar)

        return seminars

    def _parse_event(self, event: dict[str, Any]) -> Seminar | None:
        """Parse a WHO event into a Seminar."""
        title = event.get("Title", "").strip()
        if not title:
            return None

        # Parse dates
        start_str = event.get("EventStart", "")
        end_str = event.get("EventEnd", "")

        start_datetime = None
        end_datetime = None

        if start_str:
            try:
                start_datetime = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
                start_datetime = start_datetime.replace(tzinfo=None)
            except ValueError:
                pass

        if end_str:
            try:
                end_datetime = datetime.fromisoformat(end_str.replace("Z", "+00:00"))
                end_datetime = end_datetime.replace(tzinfo=None)
            except ValueError:
                pass

        if not start_datetime:
            return None

        # Build URL - prefer ItemDefaultUrl (includes date path), fall back to UrlName
        item_url = event.get("ItemDefaultUrl", "")
        url_name = event.get("UrlName", "")
        if item_url:
            if item_url.startswith("http"):
                url = item_url
            else:
                url = f"{self.BASE_EVENT_URL}{item_url.lstrip('/')}"
        elif url_name:
            if url_name.startswith("http"):
                url = url_name
            else:
                url = f"{self.BASE_EVENT_URL}{url_name}"
        else:
            url = "https://www.who.int/news-room/events"

        # Get location
        location = (event.get("Location") or "").strip() or "Online/Geneva"

        # Get description/summary
        description = (event.get("Summary") or "").strip() or None

        return Seminar(
            source_id=self.source_id,
            title=title,
            description=description,
            url=url,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            timezone="UTC",
            location=location,
            organizer="World Health Organization",
            category=self.category,
            raw_data={"who_id": event.get("Id")},
        )
