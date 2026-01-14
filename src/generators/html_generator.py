# GID Seminars - HTML Generator
"""Generate HTML page with collapsible Upcoming/Past sections."""

from datetime import datetime
from pathlib import Path
from typing import Any

from rich.console import Console

from src.core.database import SeminarDatabase
from src.core.exclusion_filter import ExclusionFilter
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
    """Generate HTML page with collapsible sections."""

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
        self.calendar_config = config.get("calendar", {})

    def generate(self, output_path: Path) -> tuple[Path, int]:
        """
        Generate HTML page with Upcoming and Past sections.

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

        # Apply exclusion filter
        if self.exclusion_filter:
            seminars = self.exclusion_filter.filter_seminars(seminars)

        # Split into upcoming and past
        now = datetime.utcnow()
        upcoming = [s for s in seminars if s.start_datetime >= now]
        past = [s for s in seminars if s.start_datetime < now]

        # Sort: upcoming by soonest first, past by most recent first
        upcoming.sort(key=lambda s: s.start_datetime)
        past.sort(key=lambda s: s.start_datetime, reverse=True)

        # Get unique values for filters
        sources = sorted(set(s.source_id for s in seminars))
        categories = sorted(set(s.category for s in seminars if s.category))

        # Build HTML
        html_parts = [
            self._get_html_header(),
            self._generate_title_banner(len(upcoming), len(past)),
            self._generate_filter_controls(sources, categories),
            self._generate_quick_links(),
            self._generate_upcoming_section(upcoming),
            self._generate_past_section(past),
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

        console.print(f"  Generated HTML: {len(upcoming)} upcoming, {len(past)} past → {output_path.name}")

        return output_path, len(seminars)

    def _get_html_header(self) -> str:
        """Generate HTML header."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GID Seminars - Global Infectious Disease Webinars &amp; Seminars</title>
    <style>
        * {{ box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: {COLORS['dark']};
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: {COLORS['light']};
        }}
        .section-header {{
            background: {COLORS['white']};
            padding: 15px 20px;
            border-radius: 8px;
            margin: 20px 0 10px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            user-select: none;
        }}
        .section-header:hover {{
            background: {COLORS['light']};
        }}
        .section-title {{
            font-size: 1.3em;
            font-weight: 600;
            color: {COLORS['dark']};
            margin: 0;
        }}
        .section-count {{
            background: {COLORS['primary']};
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.9em;
        }}
        .section-toggle {{
            font-size: 1.5em;
            color: {COLORS['muted']};
            transition: transform 0.2s;
        }}
        .section-content {{
            overflow: hidden;
            transition: max-height 0.3s ease-out;
        }}
        .section-content.collapsed {{
            max-height: 0 !important;
        }}
        .seminar-card {{
            background: {COLORS['white']};
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 16px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        .filter-container {{
            background: {COLORS['white']};
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        .filter-row {{
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            align-items: center;
        }}
        .filter-group {{
            flex: 1;
            min-width: 200px;
        }}
        .filter-group.search {{
            flex: 2;
            min-width: 250px;
        }}
        .filter-label {{
            display: block;
            font-size: 0.85em;
            color: {COLORS['muted']};
            margin-bottom: 4px;
        }}
        .filter-select, .filter-input {{
            width: 100%;
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 1em;
            background: white;
        }}
        .badge {{
            display: inline-block;
            padding: 2px 10px;
            border-radius: 4px;
            font-size: 0.75em;
            margin-right: 6px;
        }}
        .no-results {{
            text-align: center;
            padding: 40px;
            color: {COLORS['muted']};
        }}
    </style>
</head>
<body>"""

    def _generate_title_banner(self, upcoming_count: int, past_count: int) -> str:
        """Generate title banner with gradient background."""
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        total = upcoming_count + past_count
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
        <span id="visible-count">{total}</span> events
        (<span id="upcoming-visible">{upcoming_count}</span> upcoming,
        <span id="past-visible">{past_count}</span> past) |
        Last updated: {now}
    </p>
</div>"""

    def _generate_filter_controls(self, sources: list[str], categories: list[str]) -> str:
        """Generate filter dropdowns and search box."""
        source_options = '<option value="all">All Sources</option>\n'
        for source in sources:
            source_options += f'        <option value="{source}">{source}</option>\n'

        category_options = '<option value="all">All Categories</option>\n'
        for category in categories:
            category_options += f'        <option value="{category}">{category}</option>\n'

        return f"""
<div class="filter-container">
    <div class="filter-row">
        <div class="filter-group">
            <label class="filter-label">Source</label>
            <select id="filter-source" class="filter-select">
                {source_options}
            </select>
        </div>
        <div class="filter-group">
            <label class="filter-label">Category</label>
            <select id="filter-category" class="filter-select">
                {category_options}
            </select>
        </div>
        <div class="filter-group search">
            <label class="filter-label">Search</label>
            <input type="text" id="search-box" class="filter-input" placeholder="Search titles and descriptions...">
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
    <span style="border-left: 1px solid #ddd; padding-left: 15px; margin-left: 5px;">
        <a href="submit.html" style="
            display: inline-flex;
            align-items: center;
            padding: 8px 16px;
            background: {COLORS['success']};
            color: white;
            text-decoration: none;
            border-radius: 6px;
            font-size: 0.9em;
        ">+ Submit Event</a>
    </span>
</div>"""

    def _generate_upcoming_section(self, seminars: list[Seminar]) -> str:
        """Generate collapsible upcoming seminars section."""
        cards = "".join(self._generate_seminar_card(s, is_past=False) for s in seminars)

        if not cards:
            cards = f'<div class="no-results">No upcoming seminars in the next 30 days.</div>'

        return f"""
<div class="section-header" id="upcoming-header">
    <div style="display: flex; align-items: center; gap: 15px;">
        <h2 class="section-title" style="color: {COLORS['success']};">Upcoming Seminars</h2>
        <span class="section-count" id="upcoming-count" style="background: {COLORS['success']};">{len(seminars)}</span>
    </div>
    <span class="section-toggle" id="upcoming-toggle">▼</span>
</div>
<div class="section-content" id="upcoming-content">
    {cards}
</div>"""

    def _generate_past_section(self, seminars: list[Seminar]) -> str:
        """Generate collapsible past seminars section."""
        cards = "".join(self._generate_seminar_card(s, is_past=True) for s in seminars)

        if not cards:
            cards = f'<div class="no-results">No past seminars in the last 30 days.</div>'

        return f"""
<div class="section-header" id="past-header">
    <div style="display: flex; align-items: center; gap: 15px;">
        <h2 class="section-title" style="color: {COLORS['secondary']};">Past Seminars (Recordings)</h2>
        <span class="section-count" id="past-count" style="background: {COLORS['secondary']};">{len(seminars)}</span>
    </div>
    <span class="section-toggle" id="past-toggle">▼</span>
</div>
<div class="section-content" id="past-content">
    {cards}
</div>"""

    def _generate_seminar_card(self, seminar: Seminar, is_past: bool) -> str:
        """Generate a single seminar card."""
        now = datetime.utcnow()
        is_today = seminar.start_datetime.date() == now.date()

        # Determine border color and badge
        if is_past:
            border_color = COLORS["secondary"]
            time_badge = f'<span class="badge" style="background: {COLORS["secondary"]}; color: white;">Recording Available</span>'
            opacity = "0.9"
        elif is_today:
            border_color = COLORS["success"]
            time_badge = f'<span class="badge" style="background: {COLORS["success"]}; color: white;">Today</span>'
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

        # Hide event link - creates a GitHub Issue to exclude this event
        hide_url = seminar.url or ""
        hide_title = seminar.title.replace('"', "'")[:60]
        hide_issue_title = f"Hide Event: {hide_title}"
        hide_issue_body = f"""**Event to hide:**
- Title: {seminar.title}
- URL: {seminar.url or 'N/A'}
- Source: {seminar.source_id}
- Date: {date_str}

**Reason for hiding:**
(Please describe why this event should be removed from the calendar)

---
*Submitted via the events page*"""
        hide_link = f"https://github.com/dholab/gid-seminars/issues/new?title={hide_issue_title}&labels=hide-event&body=" + hide_issue_body.replace("\n", "%0A").replace(" ", "%20").replace(":", "%3A").replace("/", "%2F")

        # Access restriction badge
        access_badge = ""
        if seminar.access_restriction and seminar.access_restriction != "Public":
            access_badge = f'<span class="badge" style="background: {COLORS["warning"]}; color: {COLORS["dark"]};">{seminar.access_restriction}</span>'

        # Search text for filtering
        search_text = f"{seminar.title} {seminar.description or ''} {seminar.organizer or ''}".replace('"', "'").replace("\n", " ")

        section = "past" if is_past else "upcoming"

        return f"""
<div class="seminar-card"
     data-source="{seminar.source_id}"
     data-category="{seminar.category or ''}"
     data-section="{section}"
     data-search="{search_text}"
     style="border-left: 4px solid {border_color}; opacity: {opacity};">
    <div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
        <div style="font-size: 0.9em; color: {COLORS['muted']};">
            {date_str} at {time_str} ({seminar.timezone})
        </div>
        <div>{time_badge}</div>
    </div>
    <div style="margin-bottom: 8px;">
        <span class="badge" style="background: {COLORS['info']}; color: white;">{seminar.source_id}</span>
        {f'<span class="badge" style="background: {COLORS["light"]}; color: {COLORS["dark"]};">{seminar.category}</span>' if seminar.category else ''}
        {access_badge}
    </div>
    <h3 style="margin: 8px 0; font-size: 1.15em; color: {COLORS['dark']}; font-weight: 600;">
        {seminar.title}
    </h3>
    {desc_preview}
    {f'<div style="margin-top: 12px;">{links_html}</div>' if links_html else ''}
    <div style="margin-top: 8px; text-align: right;">
        <a href="{hide_link}" target="_blank" style="color: {COLORS['muted']}; text-decoration: none; font-size: 0.75em; opacity: 0.7;">Hide this event</a>
    </div>
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
        <a href="https://github.com/dholab/gid-seminars" style="color: {COLORS['primary']};">GitHub</a>
    </p>
    <p style="margin: 8px 0 0 0;">
        Wisconsin National Primate Research Center - Global Infectious Diseases
    </p>
</div>"""

    def _get_filter_script(self) -> str:
        """Generate JavaScript for filtering and collapsible sections."""
        return """
<script>
// Collapsible section functionality
function setupCollapsible(headerId, contentId, toggleId) {
    var header = document.getElementById(headerId);
    var content = document.getElementById(contentId);
    var toggle = document.getElementById(toggleId);

    header.addEventListener('click', function() {
        content.classList.toggle('collapsed');
        toggle.textContent = content.classList.contains('collapsed') ? '▶' : '▼';
    });
}

setupCollapsible('upcoming-header', 'upcoming-content', 'upcoming-toggle');
setupCollapsible('past-header', 'past-content', 'past-toggle');

// Filtering functionality
function filterSeminars() {
    var sourceFilter = document.getElementById('filter-source').value;
    var categoryFilter = document.getElementById('filter-category').value;
    var searchQuery = document.getElementById('search-box').value.toLowerCase();

    var cards = document.querySelectorAll('.seminar-card');
    var upcomingVisible = 0;
    var pastVisible = 0;

    cards.forEach(function(card) {
        var source = card.getAttribute('data-source');
        var category = card.getAttribute('data-category');
        var section = card.getAttribute('data-section');
        var searchText = card.getAttribute('data-search').toLowerCase();

        var showSource = sourceFilter === 'all' || source === sourceFilter;
        var showCategory = categoryFilter === 'all' || category === categoryFilter;
        var showSearch = searchQuery === '' || searchText.indexOf(searchQuery) !== -1;

        if (showSource && showCategory && showSearch) {
            card.style.display = 'block';
            if (section === 'upcoming') upcomingVisible++;
            else pastVisible++;
        } else {
            card.style.display = 'none';
        }
    });

    // Update counts
    document.getElementById('upcoming-count').textContent = upcomingVisible;
    document.getElementById('past-count').textContent = pastVisible;
    document.getElementById('upcoming-visible').textContent = upcomingVisible;
    document.getElementById('past-visible').textContent = pastVisible;
    document.getElementById('visible-count').textContent = upcomingVisible + pastVisible;
}

// Add event listeners
document.getElementById('filter-source').addEventListener('change', filterSeminars);
document.getElementById('filter-category').addEventListener('change', filterSeminars);
document.getElementById('search-box').addEventListener('keyup', filterSeminars);
</script>"""

    def _get_html_footer(self) -> str:
        """Close HTML document."""
        return """
</body>
</html>"""
