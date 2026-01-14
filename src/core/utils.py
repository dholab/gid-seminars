# GID Seminars - Shared Utilities
"""Shared utility functions and constants used across the codebase."""

import re
from datetime import datetime, timedelta
from typing import Any

from rich.console import Console

# Shared console instance - use this instead of creating new Console() in each file
console = Console()


# =============================================================================
# Constants
# =============================================================================

# Maximum lengths for various fields
MAX_TITLE_LENGTH = 150
MAX_DESCRIPTION_LENGTH = 2000
MAX_DESCRIPTION_PREVIEW = 200

# Default time window settings
DEFAULT_DAYS_BEHIND = 30
DEFAULT_DAYS_AHEAD = 30

# HTTP defaults
DEFAULT_TIMEOUT = 30
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 2


# =============================================================================
# Datetime Parsing Utilities
# =============================================================================

# Comprehensive list of datetime formats used across the application
DATETIME_FORMATS = [
    # ISO formats
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%dT%H:%M",
    "%Y-%m-%d %H:%M",
    "%Y-%m-%d",
    # US formats with time
    "%m/%d/%Y %I:%M:%S %p",
    "%m/%d/%Y %I:%M %p",
    "%m/%d/%Y",
    # Full month name formats
    "%B %d, %Y %I:%M %p",
    "%B %d %Y %I:%M %p",
    "%B %d, %Y %I:%M%p",
    "%B %d %Y %I:%M%p",
    "%B %d, %Y",
    "%B %d %Y",
    # Abbreviated month formats
    "%b %d, %Y %I:%M %p",
    "%b %d %Y %I:%M %p",
    "%b %d, %Y",
    "%b %d %Y",
    "%b %d",
    # RFC formats
    "%a, %d %b %Y %H:%M:%S %z",
    "%a, %d %b %Y %H:%M:%S",
]


def parse_datetime(dt_str: str, formats: list[str] | None = None) -> datetime | None:
    """
    Parse a datetime string using multiple format patterns.

    Args:
        dt_str: The datetime string to parse
        formats: Optional list of format strings to try. Uses DATETIME_FORMATS if None.

    Returns:
        Parsed datetime or None if parsing fails
    """
    if not dt_str:
        return None

    dt_str = dt_str.strip()
    formats = formats or DATETIME_FORMATS

    for fmt in formats:
        try:
            return datetime.strptime(dt_str, fmt)
        except ValueError:
            continue

    return None


def parse_date_time_parts(date_str: str, time_str: str) -> datetime | None:
    """
    Parse separate date and time strings into a datetime.

    Args:
        date_str: Date string (e.g., "January 15, 2025" or "1/15/2025")
        time_str: Time string (e.g., "2:00 PM" or "14:00")

    Returns:
        Combined datetime or None if parsing fails
    """
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

    time_formats = ["%I:%M%p", "%I%p", "%I:%M %p", "%I %p", "%H:%M"]
    for fmt in time_formats:
        try:
            parsed_time = datetime.strptime(time_str, fmt)
            return parsed_date.replace(hour=parsed_time.hour, minute=parsed_time.minute)
        except ValueError:
            continue

    # Return date with noon as default time
    return parsed_date.replace(hour=12, minute=0)


# =============================================================================
# URL Extraction Utilities
# =============================================================================

# URL pattern for extraction from text
URL_PATTERN = re.compile(r'https?://[^\s<>"\')\]]+[^\s<>"\')\].,;:!?]')


def extract_url_from_text(text: str) -> str | None:
    """
    Extract the first URL from a text string.

    Args:
        text: Text to search for URLs

    Returns:
        First URL found or None
    """
    if not text:
        return None

    match = URL_PATTERN.search(text)
    return match.group(0) if match else None


def extract_all_urls_from_text(text: str) -> list[str]:
    """
    Extract all URLs from a text string.

    Args:
        text: Text to search for URLs

    Returns:
        List of URLs found
    """
    if not text:
        return []

    return URL_PATTERN.findall(text)


# =============================================================================
# String Utilities
# =============================================================================

def clean_string(value: Any) -> str:
    """
    Clean and normalize a string value.

    Args:
        value: Value to clean (can be None or any type)

    Returns:
        Cleaned string or empty string if None
    """
    if value is None:
        return ""
    return str(value).strip()


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate a string to a maximum length, adding suffix if truncated.

    Args:
        text: Text to truncate
        max_length: Maximum length including suffix
        suffix: Suffix to add if truncated

    Returns:
        Truncated string
    """
    if not text or len(text) <= max_length:
        return text

    return text[: max_length - len(suffix)] + suffix


# =============================================================================
# Config Loading Utilities
# =============================================================================

def load_config(config_path: Any) -> dict[str, Any]:
    """
    Load a TOML configuration file.

    Args:
        config_path: Path to TOML file

    Returns:
        Configuration dictionary
    """
    import toml
    from pathlib import Path

    return toml.load(Path(config_path))


def get_config_value(config: dict[str, Any], *keys: str, default: Any = None) -> Any:
    """
    Safely get a nested config value.

    Args:
        config: Configuration dictionary
        *keys: Keys to traverse
        default: Default value if not found

    Returns:
        Config value or default
    """
    current = config
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current
