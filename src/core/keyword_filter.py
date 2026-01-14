# GID Seminars - Keyword Filter
"""Filter seminars based on keyword matching."""

import re
from typing import Any

from rich.console import Console

from src.core.models import Seminar

console = Console()


class KeywordFilter:
    """Filter seminars based on keyword matching in title and description."""

    def __init__(self, config: dict[str, Any]):
        """
        Initialize the keyword filter.

        Args:
            config: Filtering configuration with 'keywords' and 'exclude_keywords' lists
        """
        self.keywords = config.get("keywords", [])
        self.exclude_keywords = config.get("exclude_keywords", [])

        # Compile regex patterns for efficient matching (case-insensitive, word boundaries)
        self.include_patterns = [
            re.compile(rf"\b{re.escape(kw)}\b", re.IGNORECASE)
            for kw in self.keywords
        ]
        self.exclude_patterns = [
            re.compile(rf"\b{re.escape(kw)}\b", re.IGNORECASE)
            for kw in self.exclude_keywords
        ]

    def matches(self, seminar: Seminar) -> bool:
        """
        Check if a seminar matches the keyword criteria.

        Returns True if:
        - Title or description contains at least one include keyword
        - AND does not contain any exclude keywords

        Args:
            seminar: The seminar to check

        Returns:
            True if seminar matches criteria, False otherwise
        """
        # Combine searchable text
        text = f"{seminar.title} {seminar.description or ''}"

        # Check exclusion first (faster rejection)
        for pattern in self.exclude_patterns:
            if pattern.search(text):
                return False

        # Check inclusion
        for pattern in self.include_patterns:
            if pattern.search(text):
                return True

        return False

    def filter_seminars(
        self,
        seminars: list[Seminar],
        require_keywords: bool = True,
    ) -> tuple[list[Seminar], int]:
        """
        Filter a list of seminars based on keywords.

        Args:
            seminars: List of seminars to filter
            require_keywords: If True, filter by keywords. If False, return all.

        Returns:
            Tuple of (filtered_seminars, excluded_count)
        """
        if not require_keywords:
            return seminars, 0

        filtered = []
        excluded = 0

        for seminar in seminars:
            if self.matches(seminar):
                filtered.append(seminar)
            else:
                excluded += 1

        return filtered, excluded
