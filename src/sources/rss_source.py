# GID Seminars - RSS Source
"""RSS feed parser for NIH VideoCast and similar sources."""

import re
from datetime import datetime
from html import unescape
from typing import Any

import feedparser

from src.core.models import AccessRestriction, Seminar
from src.core.utils import MAX_DESCRIPTION_LENGTH, console, parse_datetime

from .base import BaseSource


class RSSSource(BaseSource):
    """Parse RSS feeds (primarily for NIH VideoCast)."""

    def fetch_seminars(self) -> list[Seminar]:
        """Fetch and parse RSS feed."""
        if not self.url:
            console.print("    [yellow]No URL configured[/yellow]")
            return []

        response = self._make_request(self.url)
        feed = feedparser.parse(response.content)

        if feed.bozo and feed.bozo_exception:
            console.print(
                f"    [yellow]Feed parsing warning: {feed.bozo_exception}[/yellow]"
            )

        seminars = []
        for entry in feed.entries:
            try:
                seminar = self._parse_entry(entry)
                if seminar:
                    seminars.append(seminar)
            except Exception as e:
                console.print(f"    [yellow]Error parsing entry: {e}[/yellow]")
                continue

        return seminars

    def _parse_entry(self, entry: dict[str, Any]) -> Seminar | None:
        """Parse a single RSS entry into a Seminar."""
        # Get title
        title = entry.get("title", "").strip()
        if not title:
            return None

        # Clean HTML entities from title
        title = unescape(title)

        # Get link/URL
        url = entry.get("link", "")

        # Get description and clean it
        description = entry.get("description", "") or entry.get("summary", "")
        description = self._clean_html(description)

        # Extract datetime - NIH VideoCast uses various formats
        start_datetime = self._extract_datetime(entry)
        if not start_datetime:
            return None

        # Determine access restriction from title
        access = self._parse_access_restriction(title)

        # Extract category
        category = self.category
        if "category" in entry:
            if isinstance(entry["category"], str):
                category = entry["category"]
            elif isinstance(entry["category"], list) and entry["category"]:
                category = entry["category"][0]

        # Create seminar
        return Seminar(
            source_id=self.source_id,
            title=title,
            description=description[:MAX_DESCRIPTION_LENGTH] if description else None,
            url=url,
            start_datetime=start_datetime,
            timezone=self.default_timezone,
            location="Online",
            organizer=self._extract_organizer(entry),
            category=category,
            access_restriction=access,
            raw_data=dict(entry),
        )

    def _extract_datetime(self, entry: dict[str, Any]) -> datetime | None:
        """Extract datetime from RSS entry using multiple strategies."""
        # Strategy 1: Look for air date in description (NIH VideoCast format)
        description = entry.get("description", "") or entry.get("summary", "")
        air_date = self._parse_air_date_from_description(description)
        if air_date:
            return air_date

        # Strategy 2: Use author field (NIH VideoCast sometimes puts date here)
        author = entry.get("author", "")
        if author:
            air_date = self._parse_date_string(author)
            if air_date:
                return air_date

        # Strategy 3: Use published date
        if "published_parsed" in entry and entry["published_parsed"]:
            try:
                return datetime(*entry["published_parsed"][:6])
            except (TypeError, ValueError):
                pass

        # Strategy 4: Use updated date
        if "updated_parsed" in entry and entry["updated_parsed"]:
            try:
                return datetime(*entry["updated_parsed"][:6])
            except (TypeError, ValueError):
                pass

        return None

    def _parse_air_date_from_description(self, description: str) -> datetime | None:
        """Parse air date from NIH VideoCast description format."""
        # Pattern: "Air date: 1/14/2025 2:00:00 PM"
        patterns = [
            r"Air date:\s*(\d{1,2}/\d{1,2}/\d{4}\s+\d{1,2}:\d{2}:\d{2}\s*[AP]M)",
            r"Air date:\s*(\d{1,2}/\d{1,2}/\d{4}\s+\d{1,2}:\d{2}\s*[AP]M)",
            r"Air date:\s*(\d{1,2}/\d{1,2}/\d{4})",
        ]

        for pattern in patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                date_str = match.group(1).strip()
                return self._parse_date_string(date_str)

        return None

    def _parse_date_string(self, date_str: str) -> datetime | None:
        """Parse various date string formats using shared utility."""
        return parse_datetime(date_str)

    def _parse_access_restriction(self, title: str) -> AccessRestriction:
        """Determine access restriction from title."""
        title_lower = title.lower()
        if "nih only" in title_lower:
            return AccessRestriction.NIH_ONLY
        elif "hhs only" in title_lower:
            return AccessRestriction.HHS_ONLY
        elif "members only" in title_lower:
            return AccessRestriction.MEMBERS_ONLY
        elif "registration" in title_lower:
            return AccessRestriction.REGISTRATION
        return AccessRestriction.PUBLIC

    def _extract_organizer(self, entry: dict[str, Any]) -> str | None:
        """Extract organizer/source from entry."""
        # Try various fields
        for field in ["source", "dc_creator", "author_detail"]:
            if field in entry:
                val = entry[field]
                if isinstance(val, dict):
                    return val.get("name") or val.get("title")
                elif isinstance(val, str):
                    return val
        return None

    def _clean_html(self, text: str) -> str:
        """Remove HTML tags and clean up text."""
        if not text:
            return ""

        # Unescape HTML entities
        text = unescape(text)

        # Remove HTML tags
        text = re.sub(r"<[^>]+>", " ", text)

        # Clean up whitespace
        text = " ".join(text.split())

        return text.strip()
