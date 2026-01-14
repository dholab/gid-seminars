# GID Seminars - Source Collectors
"""Source collectors for various seminar/webinar feeds."""

from .base import BaseSource
from .rss_source import RSSSource
from .ical_source import ICalSource
from .manual_source import ManualSource
from .collector import SourceCollector

__all__ = [
    "BaseSource",
    "RSSSource",
    "ICalSource",
    "ManualSource",
    "SourceCollector",
]
