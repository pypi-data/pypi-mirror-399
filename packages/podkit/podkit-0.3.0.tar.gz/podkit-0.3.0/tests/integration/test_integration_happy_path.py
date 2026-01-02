"""Integration test for podkit library happy path workflow.

This test validates the entire workflow using ONE container:
1. Initialize backend and managers
2. Create session (creates container)
3. Execute commands in container
4. Perform file operations
5. Verify resource limits
6. Clean up session and container

NOTE: Tests are numbered to ensure execution order.
"""

import time
from pathlib import Path

import docker
import pytest

from podkit import get_docker_session, reset_lifecycle_cache
from podkit.core.manager import SimpleContainerManager
from podkit.core.models import ContainerConfig
from podkit.core.session import BaseSessionManager


@pytest.mark.integration
class TestPodkitIntegrationHappyPath:
    """Integration test for complete podkit library workflow."""

    @pytest.fixture(scope="class")
    def shared_session(self, session_manager, test_user, test_session):
        """Create one session for all tests in this class."""
        session = session_manager.create_session(
            user_id=test_user,
            session_id=test_session,
        )
        yield session
        # Cleanup after all tests (only if session still exists)
        # test_14 might have already closed it
        if session_manager.get_session(test_user, test_session):
            session_manager.close_session(test_user, test_session)

    def test_01_backend_initialized(self, backend):
        """Verify backend is initialized and connected."""
        assert backend is not None
        assert backend.client is not None
        # Verify Docker is accessible
        backend.client.ping()

    def test_02_session_created(self, shared_session, docker_client, test_config):
        """Verify session and container were created."""
        assert shared_session is not None
        assert shared_session.container_id is not None
        assert shared_session.status == "running"

        # Verify container exists in Docker
        container = docker_client.containers.get(shared_session.container_id)
        assert container is not None
        assert container.status == "running"
        assert container.name.startswith(test_config["test_prefix"])

    def test_03_execute_simple_command(self, shared_session, container_manager):
        """Execute simple command and verify output."""
        result = container_manager.execute_command(
            container_id=shared_session.container_id,
            command=["echo", "hello world"],
        )

        assert result.exit_code == 0
        assert "hello world" in result.stdout
        assert result.stderr == ""

    def test_04_execute_command_with_working_directory(self, shared_session, container_manager):
        """Execute command in custom working directory."""
        result = container_manager.execute_command(
            container_id=shared_session.container_id,
            command=["pwd"],
            working_dir=Path("/tmp"),
        )

        assert result.exit_code == 0
        assert "/tmp" in result.stdout

    def test_05_execute_command_with_environment(self, shared_session, container_manager):
        """Execute command with environment variables."""
        result = container_manager.execute_command(
            container_id=shared_session.container_id,
            command=["sh", "-c", "echo $TEST_VAR"],
            environment={"TEST_VAR": "test_value"},
        )

        assert result.exit_code == 0
        assert "test_value" in result.stdout

    def test_06_execute_shell_command(self, shared_session, container_manager):
        """Execute shell command with pipes and redirects."""
        result = container_manager.execute_command(
            container_id=shared_session.container_id,
            command=["sh", "-c", "echo 'line1' && echo 'line2'"],
        )

        assert result.exit_code == 0
        assert "line1" in result.stdout
        assert "line2" in result.stdout

    def test_07_write_file_via_session_manager(
        self, shared_session, session_manager, container_manager, test_user, test_session
    ):
        """Write file to container workspace using SessionManager API."""
        content = "This is test content\nLine 2\nLine 3"
        container_path = Path("/workspace/test_file.txt")

        # Write file using session manager (cleaner API)
        session_manager.write_file(
            user_id=test_user,
            session_id=test_session,
            container_path=container_path,
            content=content,
        )

        # Verify file exists and has correct content
        result = container_manager.execute_command(
            container_id=shared_session.container_id,
            command=["cat", str(container_path)],
        )

        assert result.exit_code == 0
        assert result.stdout.strip() == content

    def test_08_read_file_from_container(self, shared_session, container_manager):
        """Read file from container workspace."""
        # Create a file via shell command
        content = "Created by shell"
        result = container_manager.execute_command(
            container_id=shared_session.container_id,
            command=["sh", "-c", f"echo '{content}' > /workspace/shell_file.txt"],
        )
        assert result.exit_code == 0

        # Read it back
        result = container_manager.execute_command(
            container_id=shared_session.container_id,
            command=["cat", "/workspace/shell_file.txt"],
        )

        assert result.exit_code == 0
        assert content in result.stdout

    def test_09_path_translation(self, container_manager, test_user, test_session, test_workspace):
        """Test path translation between host and container."""
        container_path = Path("/workspace/test.txt")

        # Convert container path to host path
        host_path = container_manager.to_host_path(container_path, test_user, test_session)

        assert host_path is not None
        assert test_workspace in host_path.parents

        # Convert back to container path
        converted_path = container_manager.to_container_path(host_path, test_user, test_session)

        assert converted_path == container_path

    def test_10_container_resource_limits(self, shared_session, docker_client):
        """Verify container has resource limits applied."""
        container = docker_client.containers.get(shared_session.container_id)
        host_config = container.attrs["HostConfig"]

        # Verify memory limit (default 4g)
        memory_limit = host_config.get("Memory")
        assert memory_limit is not None
        assert memory_limit > 0

        # Verify CPU limit
        cpu_quota = host_config.get("CpuQuota")
        assert cpu_quota is not None
        assert cpu_quota > 0

    def test_11_session_activity_tracking(self, shared_session, session_manager, test_user, test_session):
        """Verify session activity is tracked."""
        initial_activity = shared_session.last_active_at

        # Sleep briefly
        time.sleep(0.1)

        # Update activity
        session_manager.update_session_activity(test_user, test_session)

        # Verify activity was updated
        updated_session = session_manager.get_session(test_user, test_session)
        assert updated_session.last_active_at > initial_activity

    def test_12_session_not_expired(self, shared_session):
        """Verify session is not expired."""
        assert not shared_session.is_expired()

    def test_13_container_status_tracking(self, shared_session, container_manager):
        """Verify container status is tracked correctly."""
        status = container_manager.get_container_status(shared_session.container_id)
        assert status == "running"

    def test_14_cleanup_verification(
        self, shared_session, session_manager, container_manager, docker_client, test_user, test_session
    ):
        """Verify cleanup removes container and session."""
        container_id = shared_session.container_id

        # Close session (should remove container)
        session_manager.close_session(test_user, test_session)

        # Verify session removed
        session = session_manager.get_session(test_user, test_session)
        assert session is None

        # Verify container removed from Docker
        with pytest.raises(docker.errors.NotFound):
            docker_client.containers.get(container_id)

        # Verify container removed from manager tracking
        assert container_id not in container_manager.containers

    def test_15_session_recovery_after_manager_restart(
        self, backend, test_config, test_workspace, docker_client, test_user
    ):
        """Test that sessions reconnect to existing containers after manager restart.

        Verifies:
        1. Container survives manager destruction
        2. New manager discovers existing container
        3. Session reconnects automatically
        """
        recovery_session_id = f"recovery-{test_user}"
        test_content = "Data survives manager restart"

        # Phase 1: Create session with first manager
        manager1 = SimpleContainerManager(
            backend=backend,
            container_prefix=f"{test_config['test_prefix']}-recovery",
            workspace_base=test_config["test_workspace"],
            workspace_base_host=test_config["test_workspace_host"],
        )

        session_manager1 = BaseSessionManager(
            container_manager=manager1,
            default_image=test_config["test_image"],
        )

        session1 = session_manager1.create_session(user_id=test_user, session_id=recovery_session_id)
        container_id = session1.container_id

        session_manager1.write_file(
            user_id=test_user,
            session_id=recovery_session_id,
            container_path=Path("/workspace/persistent.txt"),
            content=test_content,
        )

        # Verify container is running
        container = docker_client.containers.get(container_id)
        assert container.status == "running"

        # Phase 2: Destroy managers (simulates restart)
        del session_manager1
        del manager1

        # Phase 3: Create new managers - should auto-recover session
        manager2 = SimpleContainerManager(
            backend=backend,
            container_prefix=f"{test_config['test_prefix']}-recovery",
            workspace_base=test_config["test_workspace"],
            workspace_base_host=test_config["test_workspace_host"],
        )

        session_manager2 = BaseSessionManager(
            container_manager=manager2,
            default_image=test_config["test_image"],
        )

        # Verify session was recovered
        recovered_session = session_manager2.get_session(test_user, recovery_session_id)
        assert recovered_session is not None
        assert recovered_session.container_id == container_id

        # Verify data is still accessible
        result = session_manager2.execute_command(
            user_id=test_user,
            session_id=recovery_session_id,
            command=["cat", "/workspace/persistent.txt"],
        )

        assert result.exit_code == 0
        assert test_content in result.stdout

        # Cleanup
        session_manager2.close_session(test_user, recovery_session_id)
        manager2.cleanup_all()

    def test_16_container_auto_restart_after_timeout(self, backend, test_config, docker_client, test_user):
        """Test that containers auto-restart when they've exited due to timeout."""
        timeout_session_id = f"timeout-{test_user}"

        manager = SimpleContainerManager(
            backend=backend,
            container_prefix=f"{test_config['test_prefix']}-timeout",
            workspace_base=test_config["test_workspace"],
            workspace_base_host=test_config["test_workspace_host"],
        )

        # Create config with very short container lifetime
        short_timeout_config = ContainerConfig(
            image=test_config["test_image"],
            container_lifetime_seconds=2,  # Container exits after 2 seconds
        )

        session_manager = BaseSessionManager(
            container_manager=manager,
            default_image=test_config["test_image"],
        )

        session = session_manager.create_session(
            user_id=test_user,
            session_id=timeout_session_id,
            config=short_timeout_config,
        )

        container_id = session.container_id

        # Execute command before timeout
        result = session_manager.execute_command(
            user_id=test_user,
            session_id=timeout_session_id,
            command=["echo", "before timeout"],
        )
        assert result.exit_code == 0

        # Wait for timeout
        time.sleep(3)

        # Verify container stopped
        container = docker_client.containers.get(container_id)
        container.reload()
        assert container.status != "running"

        # Execute command again - should auto-restart
        result = session_manager.execute_command(
            user_id=test_user,
            session_id=timeout_session_id,
            command=["echo", "after auto-restart"],
        )

        assert result.exit_code == 0
        assert "after auto-restart" in result.stdout

        # Verify container is running again
        container.reload()
        assert container.status == "running"

        # Cleanup
        session_manager.close_session(test_user, timeout_session_id)
        manager.cleanup_all()

    def test_17_get_docker_session_no_mounts(self, test_user):
        """Test get_docker_session() - README Example 1 (no mounts)."""
        simple_session_id = f"simple-{test_user}"

        try:
            # Example 1 from README
            result = get_docker_session(user_id=test_user, session_id=simple_session_id).execute_command("pwd")

            assert result.exit_code == 0
            assert "/workspace" in result.stdout

            # Verify session reuse
            result2 = get_docker_session(user_id=test_user, session_id=simple_session_id).execute_command(
                "echo 'hello'"
            )
            assert result2.exit_code == 0
            assert "hello" in result2.stdout

        finally:
            session = get_docker_session(user_id=test_user, session_id=simple_session_id)
            session.close()
            reset_lifecycle_cache()

    def test_18_get_docker_session_with_mounts(self, test_config, test_user):
        """Test get_docker_session() - README Example 3 (with mounts)."""
        mounted_session_id = f"mounted-{test_user}"
        test_file = "data.txt"
        test_content = "persistent data"

        try:
            # Example 3 from README
            session = get_docker_session(
                user_id=test_user,
                session_id=mounted_session_id,
                workspace=str(test_config["test_workspace"]),
                workspace_host=str(test_config["test_workspace_host"]),
            )

            # Write file using relative path (auto-prepended with /workspace/)
            returned_path = session.write_file(test_file, test_content)
            assert returned_path == Path(f"/workspace/{test_file}")

            # Verify file can be read from container
            result = session.execute_command(["cat", str(returned_path)])
            assert result.exit_code == 0
            assert result.stdout.strip() == test_content

            # Get session info to find actual host path
            session_info = session.get_info()
            session_data_dir = Path(session_info.data_dir)
            expected_host_file = session_data_dir / test_file

            # Verify file persists on host
            assert expected_host_file.exists(), f"Expected file at {expected_host_file}"
            assert expected_host_file.read_text() == test_content

            session.close()

            # File should persist after container removal
            assert expected_host_file.exists(), "File should persist after container removal"

            # Cleanup host file
            expected_host_file.unlink()

        finally:
            reset_lifecycle_cache()

    def test_19_context_manager_auto_cleanup(self, test_user, docker_client):
        """Test that context manager automatically cleans up resources."""
        ctx_session_id = f"ctx-{test_user}"

        try:
            container_id = None
            with get_docker_session(user_id=test_user, session_id=ctx_session_id) as session:
                container_id = session.get_info().container_id

                result = session.execute_command("echo 'test'")
                assert result.exit_code == 0

                # Container exists during context
                container = docker_client.containers.get(container_id)
                assert container.status == "running"

            # Container should be removed after context
            time.sleep(0.5)
            with pytest.raises(docker.errors.NotFound):
                docker_client.containers.get(container_id)

        finally:
            reset_lifecycle_cache()

    def test_20_entrypoint_controls_container_lifetime(self, backend, test_config, docker_client, test_user):
        """Test that entrypoint setting controls container lifetime behavior."""
        entrypoint_session_id = f"entrypoint-test-{test_user}"

        manager = SimpleContainerManager(
            backend=backend,
            container_prefix=f"{test_config['test_prefix']}-entrypoint",
            workspace_base=test_config["test_workspace"],
            workspace_base_host=test_config["test_workspace_host"],
        )

        session_manager = BaseSessionManager(
            container_manager=manager,
            default_image=test_config["test_image"],
        )

        # Test 1: entrypoint=None (default) - uses sleep <container_lifetime_seconds>
        config_with_timeout = ContainerConfig(
            image=test_config["test_image"],
            container_lifetime_seconds=3,  # 3 second lifetime
        )

        session1 = session_manager.create_session(
            user_id=test_user,
            session_id=f"{entrypoint_session_id}-timeout",
            config=config_with_timeout,
        )

        # Verify container is running
        container1 = docker_client.containers.get(session1.container_id)
        assert container1.status == "running"

        # Check that command is sleep with timeout
        container1.reload()
        container_attrs = container1.attrs
        cmd = container_attrs.get("Config", {}).get("Cmd", [])
        assert "sleep" in cmd
        assert "3" in cmd or 3 in cmd

        # Wait for container to auto-exit
        time.sleep(4)
        container1.reload()
        assert container1.status != "running", "Container should have exited after timeout"

        # Test 2: entrypoint=[] - uses sleep infinity (runs indefinitely)
        config_no_timeout = ContainerConfig(
            image=test_config["test_image"],
            entrypoint=[],  # Explicit entrypoint disables auto-timeout
            container_lifetime_seconds=3,  # Should be ignored
        )

        session2 = session_manager.create_session(
            user_id=test_user,
            session_id=f"{entrypoint_session_id}-notimeout",
            config=config_no_timeout,
        )

        # Verify container is running
        container2 = docker_client.containers.get(session2.container_id)
        assert container2.status == "running"

        # Check that command is sleep infinity
        container2.reload()
        container_attrs = container2.attrs
        cmd = container_attrs.get("Config", {}).get("Cmd", [])
        assert "sleep" in cmd
        assert "infinity" in cmd

        # Wait the same time period - container should still be running
        time.sleep(4)
        container2.reload()
        assert container2.status == "running", "Container should still be running (sleep infinity)"

        # Cleanup
        session_manager.close_session(test_user, f"{entrypoint_session_id}-timeout")
        session_manager.close_session(test_user, f"{entrypoint_session_id}-notimeout")
        manager.cleanup_all()
