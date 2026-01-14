# GID Seminars - Web Scraper Source
"""HTML scraper for sites without RSS/iCal feeds."""

import re
from datetime import datetime
from typing import Any

from bs4 import BeautifulSoup
from rich.console import Console

from src.core.keyword_filter import KeywordFilter
from src.core.models import Seminar

from .base import BaseSource

console = Console()


class ScraperSource(BaseSource):
    """Scrape seminars from HTML pages."""

    def __init__(
        self,
        source_id: str,
        config: dict[str, Any],
        database: Any,
        http_config: dict[str, Any] | None = None,
        keyword_filter: KeywordFilter | None = None,
    ):
        super().__init__(source_id, config, database, http_config, keyword_filter)
        self.scraper_type = config.get("scraper_type", "generic")

        # Override with browser-like headers for scraping
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        })

    def fetch_seminars(self) -> list[Seminar]:
        """Fetch and parse seminars from HTML page."""
        if not self.url:
            console.print("    [yellow]No URL configured[/yellow]")
            return []

        response = self._make_request(self.url)
        soup = BeautifulSoup(response.content, "html.parser")

        # Route to appropriate scraper based on type
        if self.scraper_type == "iasusa":
            return self._parse_iasusa(soup)
        elif self.scraper_type == "avac":
            return self._parse_avac(soup)
        elif self.scraper_type == "tephi":
            return self._parse_tephi(soup)
        elif self.scraper_type == "tghn":
            return self._parse_tghn(soup)
        elif self.scraper_type == "astmh":
            return self._parse_astmh(soup)
        else:
            console.print(f"    [yellow]Unknown scraper type: {self.scraper_type}[/yellow]")
            return []

    def _parse_iasusa(self, soup: BeautifulSoup) -> list[Seminar]:
        """Parse IAS-USA webinars page."""
        seminars = []
        seen_urls = set()

        # Find webinar links - they have href pattern /events/webinar-
        webinar_links = soup.find_all("a", href=re.compile(r"/events/webinar-"))

        for link in webinar_links:
            href = link.get("href", "")
            if not href or href in seen_urls:
                continue
            seen_urls.add(href)

            # Build full URL
            if href.startswith("/"):
                full_url = f"https://www.iasusa.org{href}"
            else:
                full_url = href

            # Get title from link title attribute or text
            title = link.get("title", "") or link.get_text(strip=True)
            if not title or len(title) < 10:
                continue

            # Find parent container to get more details
            # Go up to find the containing event-item div
            parent = link.find_parent("div", class_=re.compile(r"event-item|post-item"))
            if not parent:
                # Try going up multiple levels
                parent = link
                for _ in range(6):
                    parent = parent.parent
                    if parent and parent.name == "div":
                        text = parent.get_text()
                        if "January" in text or "February" in text or "March" in text:
                            break

            if parent:
                block_text = parent.get_text(separator="\n", strip=True)
            else:
                block_text = ""

            # Extract date and time from the block
            date_str = None
            time_str = None
            presenter = None

            # Look for date pattern
            date_match = re.search(
                r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}",
                block_text, re.IGNORECASE
            )
            if date_match:
                date_str = date_match.group(0)

            # Look for time pattern
            time_match = re.search(r"(\d{1,2}:\d{2}\s*(AM|PM))", block_text, re.IGNORECASE)
            if time_match:
                time_str = time_match.group(1)

            # Look for presenter
            presenter_match = re.search(r"Presenter:\s*([^\n]+)", block_text, re.IGNORECASE)
            if presenter_match:
                presenter = presenter_match.group(1).strip()

            # Parse datetime
            if date_str:
                dt_str = f"{date_str} {time_str}".strip() if time_str else date_str
                start_datetime = self._parse_datetime(dt_str)
            else:
                start_datetime = None

            if not start_datetime:
                # Skip entries without dates
                continue

            seminars.append(Seminar(
                source_id=self.source_id,
                title=title,
                description=f"Presenter: {presenter}" if presenter else None,
                url=full_url,
                start_datetime=start_datetime,
                timezone=self.default_timezone,
                location="Online",
                organizer=presenter.split(",")[0] if presenter else None,
                category=self.category,
            ))

        return seminars

    def _extract_iasusa_webinar(self, block: Any, detail_url: str) -> Seminar | None:
        """Extract webinar info from a block element."""
        text = block.get_text(separator=" ", strip=True)

        # Try to extract title
        title_elem = block.find(["h2", "h3", "h4", "a", "strong"])
        title = title_elem.get_text(strip=True) if title_elem else None

        if not title:
            # Use first substantial text as title
            title = text[:150] if text else None

        if not title:
            return None

        # Try to extract date
        date_match = re.search(
            r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}",
            text, re.IGNORECASE
        )

        start_datetime = None
        if date_match:
            date_str = date_match.group(0)
            # Also look for time
            time_match = re.search(r"(\d{1,2}:\d{2})\s*(AM|PM)", text, re.IGNORECASE)
            if time_match:
                time_str = time_match.group(0)
                start_datetime = self._parse_datetime(f"{date_str} {time_str}")
            else:
                start_datetime = self._parse_datetime(date_str)

        if not start_datetime:
            return None

        # Build full URL
        if detail_url.startswith("/"):
            full_url = f"https://www.iasusa.org{detail_url}"
        elif detail_url.startswith("http"):
            full_url = detail_url
        else:
            full_url = f"https://www.iasusa.org/{detail_url}"

        # Extract presenter if available
        presenter_match = re.search(r"(?:Presenter|Speaker|By)[:\s]+([^,\n]+)", text, re.IGNORECASE)
        organizer = presenter_match.group(1).strip() if presenter_match else None

        return Seminar(
            source_id=self.source_id,
            title=title,
            description=text[:1000] if text else None,
            url=full_url,
            start_datetime=start_datetime,
            timezone=self.default_timezone,
            location="Online",
            organizer=organizer,
            category=self.category,
        )

    def _parse_iasusa_text(self, text: str, soup: BeautifulSoup) -> list[Seminar]:
        """Parse webinars from page text content."""
        seminars = []

        # Pattern for IAS-USA webinar entries:
        # Title followed by date and time
        pattern = r"([A-Z][^:\n]{20,200})\s*(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}"

        # Find all date occurrences and work backwards to find titles
        date_pattern = r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(\d{4})"
        time_pattern = r"(\d{1,2}:\d{2})\s*(AM|PM)\s*(?:–|-)\s*(\d{1,2}:\d{2})\s*(AM|PM)\s*(PT|ET|CT|MT)?"

        for date_match in re.finditer(date_pattern, text, re.IGNORECASE):
            date_str = date_match.group(0)
            pos = date_match.start()

            # Look for time after the date
            time_match = re.search(time_pattern, text[pos:pos+100], re.IGNORECASE)
            time_str = ""
            if time_match:
                time_str = f"{time_match.group(1)} {time_match.group(2)}"

            # Look for title before the date (find the previous block of text)
            preceding_text = text[max(0, pos-300):pos]

            # Find the last substantial line before the date
            lines = [l.strip() for l in preceding_text.split("\n") if l.strip()]
            title = None
            for line in reversed(lines):
                if len(line) > 20 and not re.match(r"^\d", line):
                    title = line
                    break

            if not title:
                continue

            # Parse datetime
            dt_str = f"{date_str} {time_str}".strip()
            start_datetime = self._parse_datetime(dt_str)

            if not start_datetime:
                continue

            # Try to find URL for this webinar
            url = self._find_webinar_url(soup, title)

            seminars.append(Seminar(
                source_id=self.source_id,
                title=title[:200],
                description=None,
                url=url,
                start_datetime=start_datetime,
                timezone=self.default_timezone,
                location="Online",
                organizer=None,
                category=self.category,
            ))

        return seminars

    def _parse_avac(self, soup: BeautifulSoup) -> list[Seminar]:
        """Parse AVAC events page."""
        seminars = []
        seen_urls = set()

        # Find event cards - they're <a> tags with class event-card
        event_cards = soup.find_all("a", class_=re.compile(r"event-card"))

        for card in event_cards:
            href = card.get("href", "")
            if not href or href in seen_urls:
                continue
            seen_urls.add(href)

            # Get title from h3 inside the card
            title_elem = card.find("h3")
            title = title_elem.get_text(strip=True) if title_elem else card.get_text(strip=True)

            if not title or len(title) < 10:
                continue

            # Get date from time element with datetime attribute
            time_elem = card.find("time", datetime=True)
            start_datetime = None

            if time_elem:
                datetime_str = time_elem.get("datetime", "")
                if datetime_str:
                    try:
                        start_datetime = datetime.strptime(datetime_str, "%Y-%m-%d")
                    except ValueError:
                        pass

            # Fallback: extract from text
            if not start_datetime:
                card_text = card.get_text(separator=" ", strip=True)
                date_match = re.search(
                    r"(\d{1,2})\s*(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)",
                    card_text, re.IGNORECASE
                )
                if date_match:
                    day = date_match.group(1)
                    month = date_match.group(2)
                    current_year = datetime.now().year
                    try:
                        dt = datetime.strptime(f"{day} {month} {current_year}", "%d %b %Y")
                        if dt < datetime.now():
                            dt = datetime.strptime(f"{day} {month} {current_year + 1}", "%d %b %Y")
                        start_datetime = dt
                    except ValueError:
                        pass

            # Check if it's a webinar
            card_text = card.get_text(separator=" ", strip=True).lower()
            is_webinar = "webinar" in card_text

            # Build full URL
            if href.startswith("/"):
                full_url = f"https://avac.org{href}"
            else:
                full_url = href

            # Only include if we have a date
            if start_datetime:
                seminars.append(Seminar(
                    source_id=self.source_id,
                    title=title,
                    description=None,
                    url=full_url,
                    start_datetime=start_datetime,
                    timezone=self.default_timezone,
                    location="Online" if is_webinar else None,
                    organizer="AVAC",
                    category=self.category,
                ))

        return seminars

    def _parse_tephi(self, soup: BeautifulSoup) -> list[Seminar]:
        """Parse Texas EPHI events page."""
        seminars = []
        seen_urls = set()

        # Find event divs with class "event"
        event_divs = soup.find_all("div", class_="event")

        for event_div in event_divs:
            # Find the link inside
            link = event_div.find("a", href=True)
            if not link:
                continue

            href = link.get("href", "")
            if not href or href in seen_urls:
                continue
            seen_urls.add(href)

            # Get title from h3.title
            title_elem = event_div.find("h3", class_="title")
            title = title_elem.get_text(strip=True) if title_elem else None
            if not title:
                continue

            # Get date from span elements
            date_div = event_div.find("div", class_="date")
            start_datetime = None
            if date_div:
                month = date_div.find("span", class_="month")
                day = date_div.find("span", class_="day")
                year = date_div.find("span", class_="year")
                if month and day and year:
                    date_str = f"{month.get_text(strip=True)} {day.get_text(strip=True)} {year.get_text(strip=True)}"
                    try:
                        start_datetime = datetime.strptime(date_str, "%b %d %Y")
                    except ValueError:
                        pass

            # Get time
            time_elem = event_div.find("p", string=re.compile(r"Time:"))
            if time_elem:
                time_match = re.search(r"(\d{1,2}:\d{2}\s*(AM|PM))", time_elem.get_text(), re.IGNORECASE)
                if time_match and start_datetime:
                    time_str = time_match.group(1)
                    try:
                        time_obj = datetime.strptime(time_str, "%I:%M %p")
                        start_datetime = start_datetime.replace(
                            hour=time_obj.hour, minute=time_obj.minute
                        )
                    except ValueError:
                        pass

            # Get location
            location_elem = event_div.find("p", class_="subtitle")
            location = None
            if location_elem:
                loc_text = location_elem.get_text(strip=True)
                if "Location:" in loc_text:
                    location = loc_text.replace("Location:", "").strip()

            if not start_datetime:
                continue

            # Build full URL
            if href.startswith("/"):
                full_url = f"https://tephi.texas.gov{href}"
            else:
                full_url = href

            seminars.append(Seminar(
                source_id=self.source_id,
                title=title,
                description=None,
                url=full_url,
                start_datetime=start_datetime,
                timezone=self.default_timezone,
                location=location or "Online",
                organizer="Texas EPHI",
                category=self.category,
            ))

        return seminars

    def _parse_tghn(self, soup: BeautifulSoup) -> list[Seminar]:
        """Parse TGHN events page - currently returns empty as events are JS-loaded."""
        # TGHN events appear to be dynamically loaded via JavaScript
        # Would need Playwright/Selenium to scrape
        console.print("    [yellow]TGHN events are JS-loaded - skipping[/yellow]")
        return []

    def _parse_astmh(self, soup: BeautifulSoup) -> list[Seminar]:
        """Parse ASTMH events page."""
        seminars = []
        seen_titles = set()

        # Find BoxList divs containing events
        box_lists = soup.find_all("div", class_="BoxList")

        for box in box_lists:
            # Get title element - contains link and date span
            title_div = box.find("div", class_="Title")
            if not title_div:
                continue

            # Get title from link
            title_link = title_div.find("a")
            title = title_link.get_text(strip=True) if title_link else None
            if not title or title in seen_titles:
                continue
            seen_titles.add(title)

            # Get date from span.Date
            date_span = title_div.find("span", class_="Date")
            date_text = date_span.get_text(strip=True) if date_span else ""

            # Parse date - can be single or range
            start_datetime = None
            end_datetime = None

            # Check for date range first
            range_match = re.search(r"(\d{1,2}/\d{1,2}/\d{4})\s*-\s*(\d{1,2}/\d{1,2}/\d{4})", date_text)
            if range_match:
                try:
                    start_datetime = datetime.strptime(range_match.group(1), "%m/%d/%Y")
                    end_datetime = datetime.strptime(range_match.group(2), "%m/%d/%Y")
                except ValueError:
                    pass
            else:
                # Single date
                date_match = re.search(r"(\d{1,2}/\d{1,2}/\d{4})", date_text)
                if date_match:
                    try:
                        start_datetime = datetime.strptime(date_match.group(1), "%m/%d/%Y")
                    except ValueError:
                        pass

            if not start_datetime:
                continue

            # Get description
            desc_parts = []
            for p in box.find_all("p"):
                text = p.get_text(strip=True)
                if text and "Location:" not in text:
                    desc_parts.append(text)
            description = " ".join(desc_parts) if desc_parts else None

            # Get location - it's in a div with strong "Location:" label
            location = None
            for div in box.find_all("div"):
                strong = div.find("strong")
                if strong and "Location" in strong.get_text():
                    # Get text after the strong tag
                    full_text = div.get_text(strip=True)
                    location = full_text.replace("Location:", "").strip()
                    break

            # Get URL from title link
            url = None
            if title_link:
                href = title_link.get("href", "")
                if href.startswith("/"):
                    url = f"https://www.astmh.org{href}"
                elif href.startswith("http"):
                    url = href

            # Determine if virtual
            is_virtual = location and "virtual" in location.lower()

            seminars.append(Seminar(
                source_id=self.source_id,
                title=title,
                description=description,
                url=url,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                timezone=self.default_timezone,
                location=location or ("Online" if is_virtual else None),
                organizer="ASTMH",
                category=self.category,
            ))

        return seminars

    def _find_webinar_url(self, soup: BeautifulSoup, title: str) -> str | None:
        """Find URL for a webinar by matching title."""
        # Look for links containing parts of the title
        title_words = set(title.lower().split())
        best_match = None
        best_score = 0

        for link in soup.find_all("a", href=True):
            href = link.get("href", "")
            link_text = link.get_text(strip=True).lower()

            if not href or "webinar" not in href.lower():
                continue

            # Score by word overlap
            link_words = set(link_text.split())
            overlap = len(title_words & link_words)

            if overlap > best_score:
                best_score = overlap
                best_match = href

        if best_match:
            if best_match.startswith("/"):
                return f"https://www.iasusa.org{best_match}"
            return best_match

        return "https://www.iasusa.org/activities/webinars/upcoming-webinars/"

    def _parse_datetime(self, dt_str: str) -> datetime | None:
        """Parse various datetime formats."""
        formats = [
            "%B %d, %Y %I:%M %p",
            "%B %d %Y %I:%M %p",
            "%B %d, %Y %I:%M%p",
            "%B %d %Y %I:%M%p",
            "%B %d, %Y",
            "%B %d %Y",
        ]

        dt_str = dt_str.strip()

        for fmt in formats:
            try:
                return datetime.strptime(dt_str, fmt)
            except ValueError:
                continue

        return None
