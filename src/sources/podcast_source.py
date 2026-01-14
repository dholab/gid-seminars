# GID Seminars - Podcast Source
"""Fetch recent podcast episodes from RSS feeds."""

import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime
from typing import Any

from src.core.keyword_filter import KeywordFilter
from src.core.models import Seminar
from src.core.utils import DEFAULT_DAYS_BEHIND, console

from .base import BaseSource


class PodcastSource(BaseSource):
    """Fetch recent podcast episodes from RSS feeds."""

    def __init__(
        self,
        source_id: str,
        config: dict[str, Any],
        database: Any,
        http_config: dict[str, Any] | None = None,
        keyword_filter: KeywordFilter | None = None,
    ):
        super().__init__(source_id, config, database, http_config, keyword_filter)
        self.days_back = config.get("days_back", DEFAULT_DAYS_BEHIND)
        self.max_episodes = config.get("max_episodes", 10)

    def fetch_seminars(self) -> list[Seminar]:
        """Fetch recent podcast episodes from RSS feed."""
        if not self.url:
            console.print("    [yellow]No URL configured[/yellow]")
            return []

        response = self._make_request(self.url)

        try:
            root = ET.fromstring(response.content)
        except ET.ParseError as e:
            console.print(f"    [red]Failed to parse RSS: {e}[/red]")
            return []

        seminars = []
        cutoff_date = datetime.utcnow() - timedelta(days=self.days_back)

        # Find channel element
        channel = root.find("channel")
        if channel is None:
            console.print("    [yellow]No channel found in RSS[/yellow]")
            return []

        # Get podcast info
        podcast_title = channel.findtext("title", "Unknown Podcast")

        # Parse items (episodes)
        items = channel.findall("item")
        for item in items[:self.max_episodes * 2]:  # Get extra in case some are too old
            try:
                seminar = self._parse_episode(item, podcast_title, cutoff_date)
                if seminar:
                    seminars.append(seminar)
                    if len(seminars) >= self.max_episodes:
                        break
            except Exception as e:
                console.print(f"    [yellow]Error parsing episode: {e}[/yellow]")
                continue

        return seminars

    def _parse_episode(
        self, item: ET.Element, podcast_title: str, cutoff_date: datetime
    ) -> Seminar | None:
        """Parse a single RSS item (episode) into a Seminar."""
        # Get title
        title = item.findtext("title", "").strip()
        if not title:
            return None

        # Get publication date
        pub_date_str = item.findtext("pubDate", "")
        if not pub_date_str:
            return None

        try:
            pub_date = parsedate_to_datetime(pub_date_str)
            # Convert to naive datetime in UTC
            pub_date = pub_date.replace(tzinfo=None)
        except (ValueError, TypeError):
            return None

        # Check if within date range
        if pub_date < cutoff_date:
            return None

        # Get description
        description = item.findtext("description", "")
        # Also check for content:encoded
        content_ns = "{http://purl.org/rss/1.0/modules/content/}"
        content_encoded = item.findtext(f"{content_ns}encoded", "")
        if content_encoded and len(content_encoded) > len(description):
            description = content_encoded

        # Strip HTML tags from description
        import re
        description = re.sub(r"<[^>]+>", " ", description)
        description = re.sub(r"\s+", " ", description).strip()

        # Get episode URL (link or enclosure)
        url = item.findtext("link", "")
        enclosure = item.find("enclosure")
        if not url and enclosure is not None:
            url = enclosure.get("url", "")

        # Get duration if available
        itunes_ns = "{http://www.itunes.com/dtds/podcast-1.0.dtd}"
        duration = item.findtext(f"{itunes_ns}duration", "")

        # Format description with podcast name and duration
        full_desc = f"[Podcast: {podcast_title}]"
        if duration:
            full_desc += f" Duration: {duration}"
        if description:
            full_desc += f"\n\n{description[:1500]}"

        return Seminar(
            source_id=self.source_id,
            title=title,
            description=full_desc,
            url=url,
            start_datetime=pub_date,
            timezone="UTC",
            location="Podcast",
            organizer=podcast_title,
            category=self.category,
            raw_data={"type": "podcast", "duration": duration},
        )
