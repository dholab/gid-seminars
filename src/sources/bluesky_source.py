# GID Seminars - Bluesky Source
"""Search Bluesky for seminar announcements from research institutions.

Requires authentication via environment variables:
- BLUESKY_HANDLE: Your Bluesky handle (e.g., username.bsky.social)
- BLUESKY_APP_PASSWORD: An app password from Bluesky settings
"""

import os
import re
from datetime import datetime, timedelta
from typing import Any

from rich.console import Console

from src.core.keyword_filter import KeywordFilter
from src.core.models import Seminar

from .base import BaseSource

console = Console()


class BlueskySource(BaseSource):
    """Search Bluesky for seminar/webinar announcements using AT Protocol SDK."""

    def __init__(
        self,
        source_id: str,
        config: dict[str, Any],
        database: Any,
        http_config: dict[str, Any] | None = None,
        keyword_filter: KeywordFilter | None = None,
    ):
        super().__init__(source_id, config, database, http_config, keyword_filter)

        # Bluesky-specific config
        self.search_queries = config.get("search_queries", [])
        self.search_accounts = config.get("search_accounts", [])
        self.days_back = config.get("days_back", 30)
        self.limit_per_query = config.get("limit_per_query", 50)

        # Authentication from environment
        self.handle = os.environ.get("BLUESKY_HANDLE", "")
        self.app_password = os.environ.get("BLUESKY_APP_PASSWORD", "")

        self._client = None

    def _get_client(self):
        """Get authenticated Bluesky client."""
        if self._client is not None:
            return self._client

        if not self.handle or not self.app_password:
            raise ValueError(
                "Bluesky authentication required. Set BLUESKY_HANDLE and BLUESKY_APP_PASSWORD environment variables."
            )

        try:
            from atproto import Client
            self._client = Client()
            self._client.login(self.handle, self.app_password)
            console.print(f"    [dim]Authenticated as {self.handle}[/dim]")
            return self._client
        except ImportError:
            raise ImportError("atproto package required. Install with: uv add atproto")

    def fetch_seminars(self) -> list[Seminar]:
        """Fetch seminar announcements from Bluesky."""
        try:
            client = self._get_client()
        except (ValueError, ImportError) as e:
            console.print(f"    [yellow]Bluesky auth failed: {e}[/yellow]")
            return []

        all_seminars = []
        seen_uris = set()

        # Calculate date range
        since_date = (datetime.utcnow() - timedelta(days=self.days_back)).strftime("%Y-%m-%dT00:00:00.000Z")

        # Search by queries
        for query in self.search_queries:
            try:
                response = client.app.bsky.feed.search_posts(
                    params={
                        "q": query,
                        "limit": self.limit_per_query,
                        "sort": "latest",
                        "since": since_date,
                    }
                )
                posts = response.posts if response else []
                seminars = self._parse_posts(posts, seen_uris)
                all_seminars.extend(seminars)
                if seminars:
                    console.print(f"    [dim]Query '{query}': {len(seminars)} posts[/dim]")
            except Exception as e:
                console.print(f"    [yellow]Query '{query}' failed: {e}[/yellow]")

        # Search by accounts
        for account in self.search_accounts:
            if not account:
                continue
            try:
                response = client.app.bsky.feed.search_posts(
                    params={
                        "q": "seminar OR webinar OR lecture",
                        "author": account,
                        "limit": self.limit_per_query,
                        "sort": "latest",
                        "since": since_date,
                    }
                )
                posts = response.posts if response else []
                seminars = self._parse_posts(posts, seen_uris)
                all_seminars.extend(seminars)
                if seminars:
                    console.print(f"    [dim]Account '{account}': {len(seminars)} posts[/dim]")
            except Exception as e:
                console.print(f"    [yellow]Account '{account}' search failed: {e}[/yellow]")

        return all_seminars

    def _parse_posts(
        self,
        posts: list[Any],
        seen_uris: set[str],
    ) -> list[Seminar]:
        """Parse Bluesky posts into Seminar objects."""
        seminars = []

        for post in posts:
            try:
                uri = post.uri if hasattr(post, "uri") else ""
                if uri in seen_uris:
                    continue
                seen_uris.add(uri)

                seminar = self._parse_post(post)
                if seminar:
                    seminars.append(seminar)
            except Exception as e:
                console.print(f"    [dim]Skipping post: {e}[/dim]")

        return seminars

    def _parse_post(self, post: Any) -> Seminar | None:
        """Parse a single Bluesky post into a Seminar."""
        # Get record data
        record = post.record if hasattr(post, "record") else {}
        author = post.author if hasattr(post, "author") else None

        # Get post text
        text = record.text if hasattr(record, "text") else ""
        text = text.strip()
        if not text:
            return None

        # Check if this looks like a seminar announcement
        if not self._looks_like_seminar(text):
            return None

        # Extract datetime from post
        event_datetime = self._extract_datetime_from_text(text)

        # If no date found in text, use post creation time as fallback
        if not event_datetime:
            created_at = record.created_at if hasattr(record, "created_at") else ""
            if created_at:
                try:
                    event_datetime = datetime.fromisoformat(created_at.replace("Z", "+00:00")).replace(tzinfo=None)
                except ValueError:
                    return None
            else:
                return None

        # Build title from first line
        title = self._extract_title(text)
        if not title:
            return None

        # Get author info
        author_handle = author.handle if author and hasattr(author, "handle") else ""
        author_name = author.display_name if author and hasattr(author, "display_name") else author_handle

        # Build URL to the post
        post_uri = post.uri if hasattr(post, "uri") else ""
        post_url = self._uri_to_url(post_uri, author_handle)

        # Extract any URLs from the post
        event_url = self._extract_url_from_record(record)

        return Seminar(
            source_id=self.source_id,
            title=title,
            description=text[:2000],
            url=event_url or post_url,
            start_datetime=event_datetime,
            timezone=self.default_timezone,
            location="Online",
            organizer=author_name or None,
            category=self.category,
            raw_data={
                "bluesky_uri": post_uri,
                "author_handle": author_handle,
                "post_url": post_url,
            },
        )

    def _looks_like_seminar(self, text: str) -> bool:
        """Check if text looks like a seminar announcement."""
        text_lower = text.lower()

        # Must have seminar-related keywords
        seminar_keywords = [
            "seminar", "webinar", "lecture", "talk", "presentation",
            "symposium", "colloquium", "workshop", "conference",
            "speaker", "presenting", "join us",
        ]

        has_seminar_keyword = any(kw in text_lower for kw in seminar_keywords)
        if not has_seminar_keyword:
            return False

        # Should have time indicators
        time_indicators = [
            "pm", "am", "noon", "et", "pt", "ct", "est", "pst", "cst",
            "register", "zoom", "link", "join",
            r"\d{1,2}:\d{2}",  # Time format
            r"\d{1,2}/\d{1,2}",  # Date format
        ]

        has_time_indicator = any(
            re.search(ind, text_lower) if "\\" in ind else ind in text_lower
            for ind in time_indicators
        )

        return has_time_indicator

    def _extract_title(self, text: str) -> str | None:
        """Extract a title from the post text."""
        lines = text.strip().split("\n")
        first_line = lines[0].strip()

        # Remove hashtags at the end
        first_line = re.sub(r"\s*#\w+\s*$", "", first_line)

        # If first line is too long, truncate
        if len(first_line) > 150:
            first_line = first_line[:147] + "..."

        # If first line is too short, use more of the text
        if len(first_line) < 20 and len(lines) > 1:
            first_line = " ".join(lines[:2])[:150]

        return first_line if first_line else None

    def _extract_datetime_from_text(self, text: str) -> datetime | None:
        """Try to extract event date/time from post text."""
        patterns = [
            # "January 15, 2025 at 2:00 PM"
            r"(\w+ \d{1,2},? \d{4})\s+(?:at\s+)?(\d{1,2}:\d{2}\s*[AP]M)",
            # "1/15/2025 2:00 PM"
            r"(\d{1,2}/\d{1,2}/\d{4})\s+(\d{1,2}:\d{2}\s*[AP]M)",
            # "Jan 15 at 2pm"
            r"(\w{3,9}\s+\d{1,2})(?:st|nd|rd|th)?\s+(?:at\s+)?(\d{1,2}(?::\d{2})?\s*[AP]M)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    date_str = match.group(1)
                    time_str = match.group(2)
                    return self._parse_date_time(date_str, time_str)
                except (ValueError, IndexError):
                    continue

        return None

    def _parse_date_time(self, date_str: str, time_str: str) -> datetime | None:
        """Parse date and time strings into datetime."""
        time_str = time_str.upper().replace(" ", "")

        date_formats = [
            "%B %d, %Y",
            "%B %d %Y",
            "%b %d, %Y",
            "%b %d %Y",
            "%m/%d/%Y",
            "%b %d",
        ]

        parsed_date = None
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_str.strip(), fmt)
                if "%Y" not in fmt:
                    now = datetime.utcnow()
                    parsed_date = parsed_date.replace(year=now.year)
                    if parsed_date < now - timedelta(days=30):
                        parsed_date = parsed_date.replace(year=now.year + 1)
                break
            except ValueError:
                continue

        if not parsed_date:
            return None

        time_formats = ["%I:%M%p", "%I%p", "%I:%M %p", "%I %p"]
        for fmt in time_formats:
            try:
                parsed_time = datetime.strptime(time_str, fmt)
                return parsed_date.replace(
                    hour=parsed_time.hour,
                    minute=parsed_time.minute
                )
            except ValueError:
                continue

        return parsed_date.replace(hour=12, minute=0)

    def _uri_to_url(self, uri: str, handle: str) -> str:
        """Convert AT URI to Bluesky web URL."""
        if not uri:
            return ""

        try:
            parts = uri.replace("at://", "").split("/")
            if len(parts) >= 3:
                post_id = parts[-1]
                return f"https://bsky.app/profile/{handle}/post/{post_id}"
        except Exception:
            pass

        return ""

    def _extract_url_from_record(self, record: Any) -> str | None:
        """Extract embedded URL from record if present."""
        # Check for embedded link
        embed = record.embed if hasattr(record, "embed") else None
        if embed:
            # External embed
            if hasattr(embed, "external") and embed.external:
                uri = embed.external.uri if hasattr(embed.external, "uri") else None
                if uri:
                    return uri

        # Check facets for links
        facets = record.facets if hasattr(record, "facets") else []
        if facets:
            for facet in facets:
                features = facet.features if hasattr(facet, "features") else []
                for feature in features:
                    if hasattr(feature, "uri"):
                        return feature.uri

        return None
