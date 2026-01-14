# GID Seminars - Source Collector
"""Orchestrates collection from all configured sources."""

from pathlib import Path
from typing import Any

import toml
from rich.console import Console

from src.core.database import SeminarDatabase
from src.core.keyword_filter import KeywordFilter

from .base import BaseSource
from .bluesky_source import BlueskySource
from .conference_source import ConferenceSource
from .ical_source import ICalSource
from .manual_source import ManualSource
from .podcast_source import PodcastSource
from .rss_source import RSSSource
from .scraper_source import ScraperSource
from .who_source import WHOSource

console = Console()


class SourceCollector:
    """Orchestrates collection from all configured sources."""

    # Map source types to their classes
    SOURCE_CLASSES: dict[str, type[BaseSource]] = {
        "rss": RSSSource,
        "ical": ICalSource,
        "manual": ManualSource,
        "bluesky": BlueskySource,
        "scraper": ScraperSource,
        "podcast": PodcastSource,
        "conference": ConferenceSource,
        "who": WHOSource,
    }

    def __init__(
        self,
        sources_config: dict[str, Any],
        settings_config: dict[str, Any],
        database: SeminarDatabase,
        base_dir: Path | None = None,
    ):
        self.sources_config = sources_config
        self.settings_config = settings_config
        self.database = database
        self.base_dir = base_dir or Path.cwd()
        self.http_config = settings_config.get("http", {})

        # Initialize keyword filter
        filter_config = settings_config.get("filtering", {})
        self.keyword_filter = KeywordFilter(filter_config) if filter_config.get("keywords") else None

        self.sources = self._initialize_sources()

    def _initialize_sources(self) -> list[BaseSource]:
        """Initialize all configured sources."""
        sources = []
        source_configs = self.sources_config.get("source", {})

        for source_id, source_config in source_configs.items():
            if not source_config.get("enabled", True):
                continue

            source_type = source_config.get("type", "rss")
            source_class = self.SOURCE_CLASSES.get(source_type)

            if not source_class:
                console.print(
                    f"[yellow]Unknown source type '{source_type}' for {source_id}[/yellow]"
                )
                continue

            try:
                if source_type in ("manual", "conference"):
                    source = source_class(
                        source_id,
                        source_config,
                        self.database,
                        self.http_config,
                        self.keyword_filter,
                        self.base_dir,
                    )
                else:
                    source = source_class(
                        source_id,
                        source_config,
                        self.database,
                        self.http_config,
                        self.keyword_filter,
                    )
                sources.append(source)
            except Exception as e:
                console.print(f"[red]Failed to initialize source {source_id}: {e}[/red]")

        return sources

    def collect_all(self) -> dict[str, dict[str, Any]]:
        """
        Collect from all sources, isolating failures.

        Returns:
            Dict mapping source_id -> result dict with 'status' and 'stats' or 'error'
        """
        results: dict[str, dict[str, Any]] = {}

        console.print(f"\n[bold]Collecting from {len(self.sources)} source(s)...[/bold]")

        for source in self.sources:
            try:
                stats = source.run()
                results[source.source_id] = {"status": "success", "stats": stats}

            except Exception as e:
                console.print(f"  [red]Source {source.source_id} failed: {e}[/red]")
                results[source.source_id] = {"status": "error", "error": str(e)}
                # Continue to next source - don't let one failure stop others

        # Log summary
        successful = sum(1 for r in results.values() if r["status"] == "success")
        failed = sum(1 for r in results.values() if r["status"] == "error")

        console.print(f"\n[bold]Collection Summary:[/bold]")
        console.print(f"  Successful: {successful}")
        if failed > 0:
            console.print(f"  Failed: {failed}", style="red")

        # Calculate totals
        total_found = sum(
            r.get("stats", {}).get("found", 0)
            for r in results.values()
            if r["status"] == "success"
        )
        total_added = sum(
            r.get("stats", {}).get("added", 0)
            for r in results.values()
            if r["status"] == "success"
        )
        total_updated = sum(
            r.get("stats", {}).get("updated", 0)
            for r in results.values()
            if r["status"] == "success"
        )

        console.print(f"  Total seminars found: {total_found}")
        console.print(f"  Total added: {total_added}")
        console.print(f"  Total updated: {total_updated}")

        return results


def collect_seminars(base_dir: Path | None = None) -> dict[str, dict[str, Any]]:
    """
    Main entry point for collecting seminars.

    Args:
        base_dir: Base directory for config files (defaults to cwd)

    Returns:
        Collection results by source
    """
    base_dir = base_dir or Path.cwd()
    config_dir = base_dir / "config"

    # Load configurations
    sources_config = toml.load(config_dir / "sources.toml")
    settings_config = toml.load(config_dir / "settings.toml")

    # Initialize database
    db_path = base_dir / settings_config.get("database", {}).get("path", "data/seminars.db")
    database = SeminarDatabase(db_path)

    # Create collector and run
    collector = SourceCollector(
        sources_config=sources_config,
        settings_config=settings_config,
        database=database,
        base_dir=base_dir,
    )

    return collector.collect_all()


if __name__ == "__main__":
    collect_seminars()
