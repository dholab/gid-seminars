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
            config: Filtering configuration with 'keywords', 'exclude_keywords',
                   and 'exclude_categories' lists
        """
        self.keywords = config.get("keywords", [])
        self.exclude_keywords = config.get("exclude_keywords", [])
        self.exclude_categories = [
            cat.lower() for cat in config.get("exclude_categories", [])
        ]

        # Compile regex patterns for efficient matching (case-insensitive, word boundaries)
        self.include_patterns = [
            re.compile(rf"\b{re.escape(kw)}\b", re.IGNORECASE)
            for kw in self.keywords
        ]
        self.exclude_patterns = [
            re.compile(rf"\b{re.escape(kw)}\b", re.IGNORECASE)
            for kw in self.exclude_keywords
        ]

    def is_excluded_category(self, seminar: Seminar) -> bool:
        """
        Check if a seminar's category is in the exclusion list.

        Args:
            seminar: The seminar to check

        Returns:
            True if category should be excluded, False otherwise
        """
        if not self.exclude_categories or not seminar.category:
            return False
        return seminar.category.lower() in self.exclude_categories

    def matches(self, seminar: Seminar) -> bool:
        """
        Check if a seminar matches the keyword criteria.

        Returns True if:
        - Category is not in exclude_categories
        - Title or description contains at least one include keyword
        - AND does not contain any exclude keywords

        Args:
            seminar: The seminar to check

        Returns:
            True if seminar matches criteria, False otherwise
        """
        # Check category exclusion first
        if self.is_excluded_category(seminar):
            return False

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
        Filter a list of seminars based on keywords and category exclusions.

        Args:
            seminars: List of seminars to filter
            require_keywords: If True, filter by keywords. If False, only apply
                            category exclusions.

        Returns:
            Tuple of (filtered_seminars, excluded_count)
        """
        filtered = []
        excluded = 0

        for seminar in seminars:
            # Always check category exclusions
            if self.is_excluded_category(seminar):
                excluded += 1
                continue

            # If keyword filtering required, check keywords
            if require_keywords:
                if self.matches(seminar):
                    filtered.append(seminar)
                else:
                    excluded += 1
            else:
                filtered.append(seminar)

        return filtered, excluded
