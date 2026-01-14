# GID Seminars - HTML Generator
"""Generate LabKey WebDAV-compatible HTML page with filtering."""

from datetime import datetime
from pathlib import Path
from typing import Any

from rich.console import Console

from src.core.database import SeminarDatabase
from src.core.models import Seminar

console = Console()

# Color constants for consistent styling
COLORS = {
    "primary": "#2c5aa0",
    "primary_light": "#4a90e2",
    "success": "#28a745",
    "warning": "#ffc107",
    "danger": "#dc3545",
    "info": "#17a2b8",
    "secondary": "#6c757d",
    "light": "#f8f9fa",
    "dark": "#343a40",
    "white": "#ffffff",
    "muted": "#868e96",
}


class HTMLGenerator:
    """Generate LabKey WebDAV-compatible HTML page."""

    def __init__(self, config: dict[str, Any], database: SeminarDatabase):
        self.config = config
        self.database = database
        self.time_window = config.get("time_window", {})
        self.calendar_config = config.get("calendar", {})

    def generate(self, output_path: Path) -> tuple[Path, int]:
        """
        Generate filterable HTML page with inline styles.

        Returns:
            Tuple of (output_path, event_count)
        """
        # Get seminars
        days_behind = self.time_window.get("days_behind", 30)
        days_ahead = self.time_window.get("days_ahead", 30)

        seminars = self.database.get_seminars_in_window(
            days_behind=days_behind,
            days_ahead=days_ahead,
        )

        # Get unique values for filters
        sources = sorted(set(s.source_id for s in seminars))
        categories = sorted(set(s.category for s in seminars if s.category))

        # Build HTML
        html_parts = [
            self._get_html_header(),
            self._generate_title_banner(len(seminars)),
            self._generate_filter_controls(sources, categories),
            self._generate_quick_links(),
            self._generate_seminar_list(seminars),
            self._generate_footer(),
            self._get_filter_script(),
            self._get_html_footer(),
        ]

        html_content = "\n".join(html_parts)

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        console.print(f"  Generated HTML with {len(seminars)} events: {output_path.name}")

        return output_path, len(seminars)

    def _get_html_header(self) -> str:
        """Generate HTML header."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GID Seminars - Global Infectious Disease Webinars &amp; Seminars</title>
</head>
<body style="
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    line-height: 1.6;
    color: {COLORS['dark']};
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    background-color: {COLORS['light']};
">"""

    def _generate_title_banner(self, count: int) -> str:
        """Generate title banner with gradient background."""
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        return f"""
<div style="
    background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['primary_light']} 100%);
    color: {COLORS['white']};
    padding: 30px;
    border-radius: 12px;
    margin-bottom: 20px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
">
    <h1 style="margin: 0 0 10px 0; font-size: 2em;">GID Seminars</h1>
    <p style="margin: 0; opacity: 0.9; font-size: 1.1em;">
        Global Infectious Disease Webinars &amp; Seminars
    </p>
    <p style="margin: 10px 0 0 0; font-size: 0.9em; opacity: 0.8;">
        <span id="visible-count">{count}</span> events | Last updated: {now}
    </p>
</div>"""

    def _generate_filter_controls(self, sources: list[str], categories: list[str]) -> str:
        """Generate filter dropdowns and search box."""
        # Build source options
        source_options = '<option value="all">All Sources</option>\n'
        for source in sources:
            source_options += f'        <option value="{source}">{source}</option>\n'

        # Build category options
        category_options = '<option value="all">All Categories</option>\n'
        for category in categories:
            category_options += f'        <option value="{category}">{category}</option>\n'

        return f"""
<div style="
    background: {COLORS['white']};
    padding: 20px;
    border-radius: 8px;
    margin-bottom: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
">
    <div style="display: flex; flex-wrap: wrap; gap: 15px; align-items: center;">
        <div style="flex: 1; min-width: 200px;">
            <label style="display: block; font-size: 0.85em; color: {COLORS['muted']}; margin-bottom: 4px;">Source</label>
            <select id="filter-source" onchange="filterSeminars()" style="
                width: 100%;
                padding: 8px 12px;
                border: 1px solid #ddd;
                border-radius: 6px;
                font-size: 1em;
                background: white;
            ">
                {source_options}
            </select>
        </div>
        <div style="flex: 1; min-width: 200px;">
            <label style="display: block; font-size: 0.85em; color: {COLORS['muted']}; margin-bottom: 4px;">Category</label>
            <select id="filter-category" onchange="filterSeminars()" style="
                width: 100%;
                padding: 8px 12px;
                border: 1px solid #ddd;
                border-radius: 6px;
                font-size: 1em;
                background: white;
            ">
                {category_options}
            </select>
        </div>
        <div style="flex: 1; min-width: 200px;">
            <label style="display: block; font-size: 0.85em; color: {COLORS['muted']}; margin-bottom: 4px;">Time</label>
            <select id="filter-time" onchange="filterSeminars()" style="
                width: 100%;
                padding: 8px 12px;
                border: 1px solid #ddd;
                border-radius: 6px;
                font-size: 1em;
                background: white;
            ">
                <option value="all">All Times</option>
                <option value="upcoming">Upcoming Only</option>
                <option value="today">Today</option>
                <option value="week">This Week</option>
                <option value="past">Past (Recordings)</option>
            </select>
        </div>
        <div style="flex: 2; min-width: 250px;">
            <label style="display: block; font-size: 0.85em; color: {COLORS['muted']}; margin-bottom: 4px;">Search</label>
            <input type="text" id="search-box" onkeyup="filterSeminars()" placeholder="Search titles and descriptions..." style="
                width: 100%;
                padding: 8px 12px;
                border: 1px solid #ddd;
                border-radius: 6px;
                font-size: 1em;
                box-sizing: border-box;
            ">
        </div>
    </div>
</div>"""

    def _generate_quick_links(self) -> str:
        """Generate quick links section."""
        return f"""
<div style="
    background: {COLORS['white']};
    padding: 15px 20px;
    border-radius: 8px;
    margin-bottom: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    display: flex;
    flex-wrap: wrap;
    gap: 15px;
    align-items: center;
">
    <span style="font-weight: 600; color: {COLORS['dark']};">Subscribe:</span>
    <a href="gid_seminars.ics" style="
        display: inline-flex;
        align-items: center;
        padding: 8px 16px;
        background: {COLORS['primary']};
        color: white;
        text-decoration: none;
        border-radius: 6px;
        font-size: 0.9em;
        transition: background 0.2s;
    ">Download .ics Calendar</a>
    <a href="seminars.json" style="
        display: inline-flex;
        align-items: center;
        padding: 8px 16px;
        background: {COLORS['secondary']};
        color: white;
        text-decoration: none;
        border-radius: 6px;
        font-size: 0.9em;
    ">JSON Feed</a>
</div>"""

    def _generate_seminar_list(self, seminars: list[Seminar]) -> str:
        """Generate list of seminar cards."""
        if not seminars:
            return f"""
<div style="
    background: {COLORS['white']};
    padding: 40px;
    border-radius: 8px;
    text-align: center;
    color: {COLORS['muted']};
">
    <p>No seminars found in the current time window.</p>
</div>"""

        cards = []
        for seminar in seminars:
            cards.append(self._generate_seminar_card(seminar))

        return f"""
<div id="seminar-list">
    {''.join(cards)}
</div>"""

    def _generate_seminar_card(self, seminar: Seminar) -> str:
        """Generate a single seminar card with inline styles."""
        now = datetime.utcnow()
        is_past = seminar.start_datetime < now
        is_today = seminar.start_datetime.date() == now.date()

        # Determine border color and badge
        if is_past:
            border_color = COLORS["secondary"]
            time_badge = f'<span style="background: {COLORS["secondary"]}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.75em;">Recording Available</span>'
            opacity = "0.85"
        elif is_today:
            border_color = COLORS["success"]
            time_badge = f'<span style="background: {COLORS["success"]}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.75em;">Today</span>'
            opacity = "1"
        else:
            border_color = COLORS["primary"]
            time_badge = ""
            opacity = "1"

        # Format datetime
        date_str = seminar.start_datetime.strftime("%a, %b %d, %Y")
        time_str = seminar.start_datetime.strftime("%I:%M %p")

        # Build description preview
        desc_preview = ""
        if seminar.description:
            desc = seminar.description[:200]
            if len(seminar.description) > 200:
                desc += "..."
            desc_preview = f'<p style="font-size: 0.9em; color: {COLORS["secondary"]}; margin: 8px 0; line-height: 1.5;">{desc}</p>'

        # Build links
        links = []
        if seminar.url:
            links.append(f'<a href="{seminar.url}" target="_blank" style="color: {COLORS["primary"]}; text-decoration: none; font-size: 0.9em;">View Event</a>')
        if seminar.registration_url:
            links.append(f'<a href="{seminar.registration_url}" target="_blank" style="color: {COLORS["success"]}; text-decoration: none; font-size: 0.9em;">Register</a>')
        if seminar.recording_url:
            links.append(f'<a href="{seminar.recording_url}" target="_blank" style="color: {COLORS["info"]}; text-decoration: none; font-size: 0.9em;">Watch Recording</a>')

        links_html = " | ".join(links) if links else ""

        # Access restriction badge
        access_badge = ""
        if seminar.access_restriction and seminar.access_restriction != "Public":
            access_badge = f'<span style="background: {COLORS["warning"]}; color: {COLORS["dark"]}; padding: 2px 8px; border-radius: 4px; font-size: 0.75em; margin-left: 8px;">{seminar.access_restriction}</span>'

        # Search text for filtering
        search_text = f"{seminar.title} {seminar.description or ''} {seminar.organizer or ''}".replace('"', "'")

        # Timestamp for time filtering
        timestamp = int(seminar.start_datetime.timestamp() * 1000)

        return f"""
<div class="seminar-card"
     data-source="{seminar.source_id}"
     data-category="{seminar.category or ''}"
     data-timestamp="{timestamp}"
     data-search="{search_text}"
     style="
         background: {COLORS['white']};
         border-radius: 8px;
         border-left: 4px solid {border_color};
         padding: 20px;
         margin-bottom: 16px;
         box-shadow: 0 2px 4px rgba(0,0,0,0.05);
         opacity: {opacity};
     ">
    <div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
        <div style="font-size: 0.9em; color: {COLORS['muted']};">
            {date_str} at {time_str} ({seminar.timezone})
        </div>
        <div>
            {time_badge}
        </div>
    </div>
    <div style="margin-bottom: 8px;">
        <span style="
            display: inline-block;
            background: {COLORS['info']};
            color: white;
            padding: 2px 10px;
            border-radius: 4px;
            font-size: 0.75em;
        ">{seminar.source_id}</span>
        {f'<span style="display: inline-block; background: {COLORS["light"]}; color: {COLORS["dark"]}; padding: 2px 10px; border-radius: 4px; font-size: 0.75em; margin-left: 6px;">{seminar.category}</span>' if seminar.category else ''}
        {access_badge}
    </div>
    <h3 style="margin: 8px 0; font-size: 1.15em; color: {COLORS['dark']}; font-weight: 600;">
        {seminar.title}
    </h3>
    {desc_preview}
    {f'<div style="margin-top: 12px;">{links_html}</div>' if links_html else ''}
</div>"""

    def _generate_footer(self) -> str:
        """Generate page footer."""
        return f"""
<div style="
    margin-top: 30px;
    padding: 20px;
    text-align: center;
    color: {COLORS['muted']};
    font-size: 0.85em;
    border-top: 1px solid #ddd;
">
    <p style="margin: 0;">
        Generated by GID Seminars Aggregator |
        <a href="https://github.com/wnprc/gid-seminars" style="color: {COLORS['primary']};">GitHub</a>
    </p>
    <p style="margin: 8px 0 0 0;">
        Wisconsin National Primate Research Center - Global Infectious Diseases
    </p>
</div>"""

    def _get_filter_script(self) -> str:
        """Generate vanilla JS filtering script."""
        return """
<script>
function filterSeminars() {
    var sourceFilter = document.getElementById('filter-source').value;
    var categoryFilter = document.getElementById('filter-category').value;
    var timeFilter = document.getElementById('filter-time').value;
    var searchQuery = document.getElementById('search-box').value.toLowerCase();

    var cards = document.querySelectorAll('.seminar-card');
    var visibleCount = 0;
    var now = Date.now();
    var dayMs = 86400000;

    cards.forEach(function(card) {
        var source = card.getAttribute('data-source');
        var category = card.getAttribute('data-category');
        var timestamp = parseInt(card.getAttribute('data-timestamp'));
        var searchText = card.getAttribute('data-search').toLowerCase();

        // Check filters
        var showSource = sourceFilter === 'all' || source === sourceFilter;
        var showCategory = categoryFilter === 'all' || category === categoryFilter;
        var showSearch = searchQuery === '' || searchText.indexOf(searchQuery) !== -1;

        // Check time filter
        var showTime = true;
        if (timeFilter === 'upcoming') {
            showTime = timestamp >= now;
        } else if (timeFilter === 'today') {
            var todayStart = new Date().setHours(0,0,0,0);
            var todayEnd = todayStart + dayMs;
            showTime = timestamp >= todayStart && timestamp < todayEnd;
        } else if (timeFilter === 'week') {
            showTime = timestamp >= now && timestamp < now + (7 * dayMs);
        } else if (timeFilter === 'past') {
            showTime = timestamp < now;
        }

        if (showSource && showCategory && showTime && showSearch) {
            card.style.display = 'block';
            visibleCount++;
        } else {
            card.style.display = 'none';
        }
    });

    document.getElementById('visible-count').textContent = visibleCount;
}
</script>"""

    def _get_html_footer(self) -> str:
        """Close HTML document."""
        return """
</body>
</html>"""
