"""Constants and default values for podkit library."""

# Container configuration defaults
DEFAULT_CONTAINER_IMAGE = "python:3.14-alpine"
DEFAULT_CPU_LIMIT = 1.0
DEFAULT_MEMORY_LIMIT = "512m"
DEFAULT_CONTAINER_LIFETIME_SECONDS = 60  # How long container runs before auto-exit
DEFAULT_SESSION_INACTIVITY_TIMEOUT_SECONDS = 3600  # How long session stays valid without activity
DEFAULT_WORKING_DIR = "/workspace"
DEFAULT_USER = "root"

# Path constants
CONTAINER_WORKSPACE_PATH = "/workspace"
DUMMY_WORKSPACE_PATH = "/tmp/podkit_dummy"

# Container management
DEFAULT_CONTAINER_PREFIX = "podkit"

# Docker-specific constants
DOCKER_CPU_QUOTA_MULTIPLIER = 100000  # Microseconds per second
DOCKER_STOP_TIMEOUT = 1  # Seconds to wait before force-stopping container
