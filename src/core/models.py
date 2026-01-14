# GID Seminars - Data Models
"""Pydantic models for seminars and source runs."""

from datetime import datetime
from enum import Enum
from hashlib import sha256
from typing import Any

from pydantic import BaseModel, Field, field_validator


class AccessRestriction(str, Enum):
    """Access restriction levels for seminars."""

    PUBLIC = "Public"
    REGISTRATION = "Registration Required"
    NIH_ONLY = "NIH Only"
    HHS_ONLY = "HHS Only"
    MEMBERS_ONLY = "Members Only"
    UNKNOWN = "Unknown"


class Seminar(BaseModel):
    """Core seminar data model."""

    id: str | None = Field(default=None, description="Unique identifier (SHA256 hash)")
    source_id: str = Field(..., description="Source identifier")
    title: str = Field(..., min_length=1)
    description: str | None = None
    url: str | None = None
    start_datetime: datetime
    end_datetime: datetime | None = None
    timezone: str = "America/New_York"
    location: str | None = None
    organizer: str | None = None
    category: str | None = None
    tags: list[str] = Field(default_factory=list)
    access_restriction: AccessRestriction = AccessRestriction.PUBLIC
    registration_url: str | None = None
    recording_url: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    checksum: str | None = None
    raw_data: dict[str, Any] | None = None

    model_config = {"use_enum_values": True}

    @field_validator("title")
    @classmethod
    def clean_title(cls, v: str) -> str:
        """Clean up title whitespace."""
        return " ".join(v.split())

    def compute_id(self) -> str:
        """Compute unique ID from source, URL/title, and start time."""
        # Use URL if available, otherwise use title
        unique_part = self.url or self.title
        id_string = f"{self.source_id}|{unique_part}|{self.start_datetime.isoformat()}"
        return sha256(id_string.encode()).hexdigest()[:16]

    def compute_checksum(self) -> str:
        """Compute content checksum for change detection."""
        content = f"{self.title}|{self.description or ''}|{self.url or ''}|{self.start_datetime.isoformat()}"
        return sha256(content.encode()).hexdigest()[:16]

    def model_post_init(self, __context: Any) -> None:
        """Auto-compute ID and checksum after initialization."""
        if self.id is None:
            self.id = self.compute_id()
        if self.checksum is None:
            self.checksum = self.compute_checksum()


class SourceRunStatus(str, Enum):
    """Status of a source collection run."""

    RUNNING = "running"
    SUCCESS = "success"
    ERROR = "error"
    SKIPPED = "skipped"


class SourceRun(BaseModel):
    """Record of a source scraping run."""

    id: int | None = None
    source_id: str
    run_started_at: datetime
    run_completed_at: datetime | None = None
    status: SourceRunStatus
    events_found: int = 0
    events_added: int = 0
    events_updated: int = 0
    events_removed: int = 0
    etag: str | None = None
    last_modified: str | None = None
    content_hash: str | None = None
    error_message: str | None = None
    duration_seconds: float | None = None

    model_config = {"use_enum_values": True}
