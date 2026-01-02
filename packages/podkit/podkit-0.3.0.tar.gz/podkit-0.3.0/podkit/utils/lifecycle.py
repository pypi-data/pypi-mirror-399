"""Optional lifecycle management utilities for convenient session management.

This module provides convenience functions for common use cases. You can still use
the core SessionManager API directly for more control.
"""

import base64
from pathlib import Path
from threading import Lock
from typing import Any

from podkit.backends.docker import DockerBackend
from podkit.constants import (
    CONTAINER_WORKSPACE_PATH,
    DEFAULT_CONTAINER_IMAGE,
    DEFAULT_CONTAINER_LIFETIME_SECONDS,
    DEFAULT_CONTAINER_PREFIX,
    DUMMY_WORKSPACE_PATH,
)
from podkit.core.manager import BaseContainerManager
from podkit.core.models import ContainerConfig, ProcessResult, Session
from podkit.core.session import BaseSessionManager
from podkit.utils.paths import normalize_container_path, write_to_mounted_path

# Global managers cache
_managers_cache: dict[tuple[str, str], tuple[DockerBackend, BaseContainerManager, BaseSessionManager]] = {}
_cache_lock = Lock()


class _NoMountContainerManager(BaseContainerManager):
    """Container manager without filesystem mounts (execution-only)."""

    def get_mounts(self, user_id: str, session_id: str, config: ContainerConfig) -> list[dict[str, Any]]:
        """Return empty mount list - no filesystem sharing."""
        return []

    def write_file(
        self,
        container_id: str,
        container_path: Path | str,
        content: str,
        user_id: str,
        session_id: str,
    ) -> Path:
        """
        Write file inside container using shell command (ephemeral).

        Args:
            container_id: ID of the container.
            container_path: Path inside the container. Can be relative or absolute.
            content: Content to write.
            user_id: User identifier (not used).
            session_id: Session identifier (not used).

        Returns:
            The normalized container path where the file was written.
        """
        path = normalize_container_path(container_path)
        content_b64 = base64.b64encode(content.encode("utf-8")).decode("ascii")
        parent_dir = str(path.parent)
        filename = str(path)
        command = f"mkdir -p {parent_dir} && echo '{content_b64}' | base64 -d > {filename}"
        result = self.execute_command(container_id, ["sh", "-c", command])
        if result.exit_code != 0:
            raise RuntimeError(f"Failed to write file {path}: {result.stderr}")
        return path


class _MountedContainerManager(BaseContainerManager):
    """Container manager with filesystem mounts for file operations."""

    def __init__(
        self,
        backend,
        container_prefix: str,
        workspace_base: Path,
        workspace_host: Path,
    ):
        super().__init__(backend, container_prefix, workspace_base)
        self.workspace_host = workspace_host

    def get_mounts(self, user_id: str, session_id: str, config: ContainerConfig) -> list[dict[str, Any]]:
        """Get volume mounts for containers."""
        from podkit.utils.paths import get_workspace_path

        workspace_path = get_workspace_path(self.workspace_base, user_id, session_id)
        workspace_path.mkdir(parents=True, exist_ok=True)

        relative_path = workspace_path.relative_to(self.workspace_base)
        host_workspace_path = self.workspace_host / relative_path

        return [
            {
                "Type": "bind",
                "Source": str(host_workspace_path),
                "Target": CONTAINER_WORKSPACE_PATH,
            }
        ]

    def write_file(
        self,
        container_id: str,
        container_path: Path | str,
        content: str,
        user_id: str,
        session_id: str,
    ) -> Path:
        """Write file to mounted filesystem (persists).

        Returns:
            The normalized container path where the file was written.
        """
        return write_to_mounted_path(
            container_path,
            content,
            lambda path: self.to_host_path(path, user_id, session_id),
        )


class SessionProxy:
    """
    Convenience wrapper for session operations.

    Remembers user_id and session_id so you don't have to pass them repeatedly.

    Example:
        session = get_docker_session(user_id="bob", session_id="123")
        result = session.execute_command("ls -lah")
        session.write_file(Path("/workspace/test.txt"), "Hello")
        session.close()
    """

    def __init__(self, session_manager: BaseSessionManager, user_id: str, session_id: str):
        """
        Initialize session proxy.

        Args:
            session_manager: The underlying session manager.
            user_id: User identifier.
            session_id: Session identifier.
        """
        self._manager = session_manager
        self._user_id = user_id
        self._session_id = session_id

    @property
    def user_id(self) -> str:
        """Get user ID."""
        return self._user_id

    @property
    def session_id(self) -> str:
        """Get session ID."""
        return self._session_id

    def execute_command(
        self,
        command: str | list[str],
        working_dir: Path | None = None,
        environment: dict[str, str] | None = None,
        timeout: int | None = None,
    ) -> ProcessResult:
        """
        Execute command in this session's container.

        Args:
            command: Command to execute.
            working_dir: Optional working directory.
            environment: Optional environment variables.
            timeout: Optional timeout in seconds.

        Returns:
            ProcessResult with exit code and output.

        Raises:
            RuntimeError: If the session is not found or command execution fails.
        """
        return self._manager.execute_command(
            self._user_id,
            self._session_id,
            command,
            working_dir,
            environment,
            timeout,
        )

    def write_file(self, container_path: Path | str, content: str) -> Path:
        """
        Write a file to this session's container.

        Behavior depends on how session was created:
        - With workspace: File persists on host filesystem
        - Without workspace: File written inside container (ephemeral)

        Args:
            container_path: Path inside the container. Can be:
                - Relative path (e.g., "file.txt") - auto-prepended with /workspace/
                - Absolute path (e.g., "/workspace/file.txt") - used as-is
            content: Content to write.

        Returns:
            The normalized container path where the file was written.

        Raises:
            RuntimeError: If the session is not found or file write fails.
        """
        # Delegate to session manager - it will pass to container manager for normalization
        return self._manager.write_file(
            self._user_id,
            self._session_id,
            container_path,
            content,
        )

    def close(self) -> None:
        """
        Close this session and cleanup resources.

        Raises:
            RuntimeError: If the session is not found.
        """
        self._manager.close_session(self._user_id, self._session_id)

    def get_info(self) -> Session | None:
        """
        Get information about this session.

        Returns:
            Session object or None if not found.
        """
        return self._manager.get_session(self._user_id, self._session_id)

    def __enter__(self):
        """Support context manager protocol."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Auto-close on context manager exit."""
        try:
            self.close()
        except Exception:  # pylint: disable=broad-except
            pass  # Best-effort cleanup


def get_docker_session(
    *,
    user_id: str,
    session_id: str,
    config: ContainerConfig | None = None,
    workspace: Path | str | None = None,
    workspace_host: Path | str | None = None,
    container_prefix: str = DEFAULT_CONTAINER_PREFIX,
    default_image: str = DEFAULT_CONTAINER_IMAGE,
) -> SessionProxy:
    """
    Get or create a Docker session with automatic manager setup.

    This is a convenience function that handles manager lifecycle internally.
    If you need more control, use BaseSessionManager directly.

    Usage Pattern 1 - No mounts (ephemeral files):
        session = get_docker_session(user_id="bob", session_id="123")
        result = session.execute_command("ls -lah")
        session.write_file(Path("/tmp/test.txt"), "content")  # Lost when container removed
        session.close()

    Usage Pattern 2 - With mounts (persistent files):
        session = get_docker_session(
            user_id="bob",
            session_id="123",
            workspace="/app/data/workspace",
            workspace_host="./data/workspace"
        )
        session.write_file(Path("/workspace/test.txt"), "content")  # Persists on host
        session.close()

    Usage Pattern 3 - Context manager (auto-cleanup):
        with get_docker_session(user_id="bob", session_id="123") as session:
            result = session.execute_command("ls -lah")
            # Automatically closed on exit

    Args:
        user_id: User identifier.
        session_id: Session identifier.
        config: Optional ContainerConfig. If None, creates with defaults:
               - image: from default_image parameter
               - entrypoint: None (uses auto-shutdown via sleep)
               - container_lifetime_seconds: from DEFAULT_CONTAINER_LIFETIME_SECONDS constant (60 seconds)
        workspace: Optional workspace path. If None, no mounts (ephemeral files).
        workspace_host: Host workspace path for Docker mounts.
                Required if workspace provided (for Docker-in-Docker).
        container_prefix: Container name prefix (default: "podkit").
        default_image: Default image if config not provided (default: "python:3.14-alpine").

    Returns:
        SessionProxy for convenient operations.

    Raises:
        RuntimeError: If Docker is not available or session creation fails.
        ValueError: If workspace provided but workspace_host is not.

    Example (no mounts):
        session = get_docker_session(user_id="bob", session_id="123")
        session.write_file(Path("/tmp/script.py"), "print('Hello')")
        result = session.execute_command("python /tmp/script.py")
        session.close()

    Example (with mounts):
        session = get_docker_session(
            user_id="bob",
            session_id="123",
            workspace="/app/data/tasks",
            workspace_host="./data/tasks"
        )
        session.write_file(Path("/workspace/script.py"), "print('Hello')")
        result = session.execute_command("python /workspace/script.py")
        session.close()
    """
    # Validate workspace parameters
    has_mounts = workspace is not None
    if has_mounts and workspace_host is None:
        raise ValueError("workspace_host is required when workspace is provided")

    # Determine cache key
    if has_mounts:
        cache_key = (f"mounted:{workspace}", container_prefix)
    else:
        cache_key = ("no-mounts", container_prefix)

    with _cache_lock:
        if cache_key not in _managers_cache:
            # Create new manager set
            backend = DockerBackend()
            backend.connect()

            if has_mounts:
                # Create manager with mounts
                container_manager = _MountedContainerManager(
                    backend=backend,
                    container_prefix=container_prefix,
                    workspace_base=Path(workspace),
                    workspace_host=Path(workspace_host),
                )
            else:
                # Create manager without mounts
                container_manager = _NoMountContainerManager(
                    backend=backend,
                    container_prefix=container_prefix,
                    workspace_base=Path(DUMMY_WORKSPACE_PATH),
                )

            session_manager = BaseSessionManager(
                container_manager=container_manager,
                default_image=default_image,
            )

            _managers_cache[cache_key] = (backend, container_manager, session_manager)

        _, _, session_manager = _managers_cache[cache_key]

    # Get existing session or create new one
    existing_session = session_manager.get_session(user_id, session_id)

    if existing_session is None:
        # Create new session with provided config or defaults
        if config is None:
            config = ContainerConfig(
                image=default_image,
                # entrypoint=None means use container_lifetime_seconds for auto-shutdown
                container_lifetime_seconds=DEFAULT_CONTAINER_LIFETIME_SECONDS,
            )

        session_manager.create_session(
            user_id=user_id,
            session_id=session_id,
            config=config,
        )

    return SessionProxy(session_manager, user_id, session_id)


def reset_lifecycle_cache() -> None:
    """
    Reset the internal manager cache.

    Useful for testing or when you need to recreate managers.
    Cleanup all sessions before calling this.
    """
    with _cache_lock:
        # Cleanup all sessions in all managers
        for _, _, session_manager in _managers_cache.values():
            try:
                session_manager.cleanup_all()
            except Exception:  # pylint: disable=broad-except
                pass

        _managers_cache.clear()
