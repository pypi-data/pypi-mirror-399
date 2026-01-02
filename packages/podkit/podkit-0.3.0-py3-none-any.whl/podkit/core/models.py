"""Core data models for isopod container management library."""

from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from podkit.constants import (
    DEFAULT_CONTAINER_LIFETIME_SECONDS,
    DEFAULT_CPU_LIMIT,
    DEFAULT_MEMORY_LIMIT,
    DEFAULT_SESSION_INACTIVITY_TIMEOUT_SECONDS,
    DEFAULT_USER,
    DEFAULT_WORKING_DIR,
)


class ContainerStatus(str, Enum):
    """Status of a container workload."""

    CREATING = "creating"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"


class ContainerConfig(BaseModel):
    """Configuration for a container workload."""

    image: str = Field(description="Container image to use")
    cpu_limit: float = Field(DEFAULT_CPU_LIMIT, description="CPU limit in cores")
    memory_limit: str = Field(DEFAULT_MEMORY_LIMIT, description="Memory limit (e.g., '4g', '512m')")
    container_lifetime_seconds: int = Field(
        DEFAULT_CONTAINER_LIFETIME_SECONDS,
        description="Container lifetime in seconds before auto-exit (default: 60 seconds). "
        "Only applies when entrypoint is None. Ignored when explicit entrypoint is set.",
    )
    environment: dict[str, str] = Field(default_factory=dict, description="Environment variables")
    working_dir: str = Field(DEFAULT_WORKING_DIR, description="Working directory inside the container")
    user: str = Field(DEFAULT_USER, description="User to run commands as")
    entrypoint: list[str] | None = Field(None, description="Override container entrypoint (None = use image default)")


class ProcessResult(BaseModel):
    """Result of a process execution."""

    exit_code: int = Field(description="Process exit code")
    stdout: str = Field(description="Standard output")
    stderr: str = Field(description="Standard error")


class Session(BaseModel):
    """User session information with container association."""

    user_id: str = Field(description="ID of the user")
    session_id: str = Field(description="ID of the session")
    container_id: str | None = Field(None, description="ID of the associated container")
    container_name: str | None = Field(None, description="Name of the associated container")
    status: ContainerStatus = Field(ContainerStatus.CREATING, description="Status of the container")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Time when the session was created",
    )
    last_active_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Time of last activity",
    )
    config: ContainerConfig = Field(description="Container configuration")
    data_dir: str = Field(description="Path to the session data directory")
    session_inactivity_timeout_seconds: int = Field(
        DEFAULT_SESSION_INACTIVITY_TIMEOUT_SECONDS,
        description="Session inactivity timeout in seconds (default: 3600 = 60 minutes)",
    )
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    def is_expired(self, timeout_seconds: int | None = None) -> bool:
        """Check if the session has expired due to inactivity.

        Args:
            timeout_seconds: Inactivity timeout in seconds. If None, use session_inactivity_timeout_seconds.

        Returns:
            True if the session has expired, False otherwise.
        """
        if timeout_seconds is None:
            timeout_seconds = self.session_inactivity_timeout_seconds

        now = datetime.now(UTC)
        elapsed_seconds = (now - self.last_active_at).total_seconds()

        return elapsed_seconds > timeout_seconds

    def update_activity(self) -> None:
        """Update the last activity timestamp to current time."""
        self.last_active_at = datetime.now(UTC)
