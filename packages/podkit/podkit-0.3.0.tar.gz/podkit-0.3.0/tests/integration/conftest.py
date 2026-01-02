"""Pytest fixtures for isopod integration tests."""

import os
import uuid
from pathlib import Path

import docker
import pytest


@pytest.fixture(scope="session")
def test_config():
    """Test configuration from environment variables."""
    return {
        "test_image": os.getenv("TEST_IMAGE", "python:3.11-alpine"),
        "test_workspace": Path(os.getenv("TEST_WORKSPACE", "/test_workspace")),
        "test_workspace_host": Path(os.getenv("TEST_WORKSPACE_HOST", os.getenv("TEST_WORKSPACE", "/test_workspace"))),
        "test_prefix": os.getenv("TEST_CONTAINER_PREFIX", "podkit-test"),
        "test_timeout": int(os.getenv("TEST_TIMEOUT", "300")),
    }


@pytest.fixture(scope="session")
def docker_client():
    """Docker client for test verification."""
    client = docker.from_env()
    client.ping()
    yield client
    client.close()


@pytest.fixture(scope="session")
def test_workspace(test_config):
    """Test workspace directory."""
    workspace = test_config["test_workspace"]
    workspace.mkdir(parents=True, exist_ok=True)
    return workspace


@pytest.fixture(scope="module")
def backend():
    """Create Docker backend for tests."""
    from podkit.backends.docker import DockerBackend

    backend = DockerBackend()
    backend.connect()
    return backend


@pytest.fixture(scope="module")
def container_manager(backend, test_config):
    """Create container manager for tests."""
    from podkit.core.manager import SimpleContainerManager

    manager = SimpleContainerManager(
        backend=backend,
        container_prefix=test_config["test_prefix"],
        workspace_base=test_config["test_workspace"],
        workspace_base_host=test_config["test_workspace_host"],
    )
    yield manager
    # Cleanup after tests
    manager.cleanup_all()


@pytest.fixture(scope="module")
def session_manager(container_manager, test_config):
    """Create session manager for tests."""
    from podkit.core.session import BaseSessionManager

    manager = BaseSessionManager(
        container_manager=container_manager,
        default_image=test_config["test_image"],
    )
    yield manager
    # Cleanup after tests
    manager.cleanup_all()


@pytest.fixture(scope="class")
def test_user():
    """Generate unique test user ID."""
    return f"test-user-{uuid.uuid4().hex[:8]}"


@pytest.fixture(scope="class")
def test_session():
    """Generate unique test session ID."""
    return f"test-session-{uuid.uuid4().hex[:8]}"
