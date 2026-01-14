# GID Seminars - Exclusion Filter
"""Filter to exclude specific events by URL or title pattern."""

import re
from pathlib import Path
from typing import Any

import toml

from .models import Seminar
from .utils import console


class ExclusionFilter:
    """Filter to exclude events based on URL or title patterns."""

    def __init__(self, exclusions_path: Path | None = None):
        """
        Initialize the exclusion filter.

        Args:
            exclusions_path: Path to excluded_events.toml file
        """
        self.excluded_urls: set[str] = set()
        self.excluded_patterns: list[tuple[re.Pattern, str]] = []

        if exclusions_path and exclusions_path.exists():
            self._load_exclusions(exclusions_path)

    def _load_exclusions(self, path: Path) -> None:
        """Load exclusions from TOML file."""
        try:
            config = toml.load(path)

            # Load URL exclusions
            for entry in config.get("exclude_url", []):
                url = entry.get("url")
                if url:
                    self.excluded_urls.add(url)
                    reason = entry.get("reason", "No reason given")
                    console.print(f"  [dim]Excluding URL: {url[:50]}... ({reason})[/dim]")

            # Load title pattern exclusions
            for entry in config.get("exclude_title", []):
                pattern_str = entry.get("pattern")
                if pattern_str:
                    try:
                        pattern = re.compile(pattern_str, re.IGNORECASE)
                        reason = entry.get("reason", "No reason given")
                        self.excluded_patterns.append((pattern, reason))
                        console.print(f"  [dim]Excluding pattern: {pattern_str} ({reason})[/dim]")
                    except re.error as e:
                        console.print(f"  [yellow]Invalid regex pattern '{pattern_str}': {e}[/yellow]")

            total = len(self.excluded_urls) + len(self.excluded_patterns)
            if total > 0:
                console.print(f"  [dim]Loaded {total} exclusion rule(s)[/dim]")

        except Exception as e:
            console.print(f"[yellow]Failed to load exclusions: {e}[/yellow]")

    def is_excluded(self, seminar: Seminar) -> tuple[bool, str | None]:
        """
        Check if a seminar should be excluded.

        Args:
            seminar: The seminar to check

        Returns:
            Tuple of (is_excluded, reason)
        """
        # Check URL exclusion
        if seminar.url and seminar.url in self.excluded_urls:
            return True, "URL in exclusion list"

        # Check title patterns
        for pattern, reason in self.excluded_patterns:
            if pattern.search(seminar.title):
                return True, f"Title matches pattern: {reason}"

        return False, None

    def filter_seminars(self, seminars: list[Seminar]) -> list[Seminar]:
        """
        Filter out excluded seminars.

        Args:
            seminars: List of seminars to filter

        Returns:
            List of seminars that are not excluded
        """
        if not self.excluded_urls and not self.excluded_patterns:
            return seminars

        filtered = []
        excluded_count = 0

        for seminar in seminars:
            is_excluded, reason = self.is_excluded(seminar)
            if is_excluded:
                excluded_count += 1
                console.print(f"  [dim]Excluded: {seminar.title[:50]}... - {reason}[/dim]")
            else:
                filtered.append(seminar)

        if excluded_count > 0:
            console.print(f"  [dim]Filtered out {excluded_count} excluded event(s)[/dim]")

        return filtered
