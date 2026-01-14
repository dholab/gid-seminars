# GID Seminars - Base Source Class
"""Abstract base class for all seminar sources."""

import time
from abc import ABC, abstractmethod
from hashlib import sha256
from typing import Any

import requests
from rich.console import Console

from src.core.database import SeminarDatabase
from src.core.exceptions import NetworkError
from src.core.models import Seminar, SourceRunStatus

console = Console()


class BaseSource(ABC):
    """Abstract base class for all seminar sources."""

    def __init__(
        self,
        source_id: str,
        config: dict[str, Any],
        database: SeminarDatabase,
        http_config: dict[str, Any] | None = None,
    ):
        self.source_id = source_id
        self.config = config
        self.database = database
        self.http_config = http_config or {}

        # Source metadata from config
        self.name = config.get("name", source_id)
        self.enabled = config.get("enabled", True)
        self.category = config.get("category")
        self.default_timezone = config.get("default_timezone", "America/New_York")
        self.url = config.get("url")

        # HTTP settings
        self.timeout = self.http_config.get("timeout", 30)
        self.max_retries = self.http_config.get("max_retries", 3)
        self.retry_delay_base = self.http_config.get("retry_delay_base", 2)
        self.user_agent = self.http_config.get(
            "user_agent", "GID-Seminars-Aggregator/1.0"
        )

        # Create session
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})

    @abstractmethod
    def fetch_seminars(self) -> list[Seminar]:
        """Fetch seminars from the source. Must be implemented by subclasses."""
        pass

    def run(self) -> dict[str, int]:
        """
        Execute the source collection with logging and database updates.

        Returns:
            Statistics dict with keys: found, added, updated, removed
        """
        if not self.enabled:
            console.print(f"[dim]  Skipping disabled source: {self.name}[/dim]")
            return {"found": 0, "added": 0, "updated": 0, "removed": 0}

        console.print(f"\n[bold cyan]  {self.name}[/bold cyan]")
        run_id = self.database.start_source_run(self.source_id)
        stats = {"found": 0, "added": 0, "updated": 0, "removed": 0}

        try:
            seminars = self.fetch_seminars()
            stats["found"] = len(seminars)

            # Upsert each seminar
            current_ids = []
            for seminar in seminars:
                is_new, change_type = self.database.upsert_seminar(seminar)
                current_ids.append(seminar.id)
                if change_type == "added":
                    stats["added"] += 1
                elif change_type == "updated":
                    stats["updated"] += 1

            # Remove stale entries (only if we found some seminars)
            if current_ids:
                stats["removed"] = self.database.delete_stale_seminars(
                    self.source_id, current_ids
                )

            self.database.complete_source_run(
                run_id,
                SourceRunStatus.SUCCESS.value,
                events_found=stats["found"],
                events_added=stats["added"],
                events_updated=stats["updated"],
                events_removed=stats["removed"],
            )

            # Log results
            console.print(f"    Found: {stats['found']}", style="green")
            if stats["added"] > 0:
                console.print(f"    Added: {stats['added']}", style="green")
            if stats["updated"] > 0:
                console.print(f"    Updated: {stats['updated']}", style="yellow")
            if stats["removed"] > 0:
                console.print(f"    Removed: {stats['removed']}", style="red")

        except Exception as e:
            console.print(f"    [red]Error: {e}[/red]")
            self.database.complete_source_run(
                run_id, SourceRunStatus.ERROR.value, error_message=str(e)
            )
            raise

        return stats

    def _make_request(
        self,
        url: str,
        method: str = "GET",
        **kwargs: Any,
    ) -> requests.Response:
        """Make HTTP request with retry logic."""
        last_error = None

        for attempt in range(self.max_retries):
            try:
                response = self.session.request(
                    method, url, timeout=self.timeout, **kwargs
                )
                response.raise_for_status()
                return response

            except requests.exceptions.RequestException as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay_base * (2**attempt)
                    console.print(
                        f"    [yellow]Request failed, retrying in {delay}s...[/yellow]"
                    )
                    time.sleep(delay)

        raise NetworkError(
            self.source_id,
            f"Request failed after {self.max_retries} attempts: {last_error}",
            last_error,
        )

    def _compute_content_hash(self, content: bytes) -> str:
        """Compute SHA256 hash of content."""
        return sha256(content).hexdigest()[:16]
