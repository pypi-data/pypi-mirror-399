# Copyright 2025-present AiiWare.com. All Rights Reserved.
#
# This source code is proprietary and confidential to AiiWare.com.
# Unauthorized copying, modification, distribution, or use is strictly
# prohibited without prior written permission.

"""
Aii Server management for Pure CLI architecture (v0.12.0).

Features:
- Detect Docker availability
- Check for aii-server container
- Pull/install aii-server image automatically
- Start/stop/restart container
- Health check via HTTP
- First-run setup flow

The aii-server Docker image is the backend that handles all AI/LLM operations.
The CLI is a pure client that communicates with it via HTTP/WebSocket.
"""


import asyncio
import logging
import subprocess
import time
from pathlib import Path
from typing import Optional, Tuple

import httpx

logger = logging.getLogger(__name__)


# Docker image configuration
AII_SERVER_IMAGE = "aiiware/aii-server:latest"
AII_SERVER_CONTAINER = "aii-server"
# Port configuration
# aii-server v0.3.9+ uses port 26169 as the default (both internal and external)
# The install script (aiiware.short.gy/server.sh) sets up 26169:26169 mapping
DEFAULT_PORT = 26169
CONTAINER_INTERNAL_PORT = 26169  # Port the server listens on inside container

# Version requirements
# This is the minimum required aii-server version for CLI v0.12.0
# Update this when new server features are required by the CLI
REQUIRED_SERVER_VERSION = "v0.3.13"

# Installation script URL
INSTALL_SCRIPT_URL = "https://aiiware.short.gy/server.sh"


class AiiServerManager:
    """
    Manage Aii Server running in Docker container.

    This is the primary server manager for v0.12.0 Pure CLI architecture.
    """

    def __init__(self, config=None, port: int = DEFAULT_PORT):
        """
        Initialize Aii server manager.

        Args:
            config: Optional ConfigManager instance
            port: Port to expose (default: 26169)
        """
        self.config = config
        self.port = port
        self.host = "127.0.0.1"
        self.container_name = AII_SERVER_CONTAINER
        self.image = AII_SERVER_IMAGE

        # Config directory for mounting
        self.config_dir = Path.home() / ".aii"

    def is_docker_available(self) -> bool:
        """Check if Docker is installed and running."""
        try:
            result = subprocess.run(
                ["docker", "info"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def is_container_exists(self) -> bool:
        """Check if aii-server container exists (running or stopped)."""
        try:
            result = subprocess.run(
                ["docker", "container", "inspect", self.container_name],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def is_container_running(self) -> bool:
        """Check if aii-server container is running."""
        try:
            result = subprocess.run(
                ["docker", "container", "inspect", "-f", "{{.State.Running}}", self.container_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0 and result.stdout.strip() == "true"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def is_server_healthy(self) -> bool:
        """Check if server is responding to health checks."""
        try:
            url = f"http://{self.host}:{self.port}/health"
            with httpx.Client(trust_env=False) as client:
                response = client.get(url, timeout=2.0)
                return response.status_code == 200
        except Exception:
            return False

    def get_server_version(self) -> Optional[str]:
        """
        Get the running server version from /v0/status endpoint.

        Returns:
            Version string (e.g., "v0.3.9") or None if unavailable
        """
        try:
            # Use /v0/status endpoint (aii-server v0.3.x API)
            url = f"http://{self.host}:{self.port}/v0/status"
            with httpx.Client(trust_env=False) as client:
                response = client.get(url, timeout=2.0)
                if response.status_code == 200:
                    data = response.json()
                    return data.get("version")

            return None
        except Exception:
            return None

    @staticmethod
    def is_version_below(current: str, target: str) -> bool:
        """
        Compare semantic versions - returns True if current < target.
        Handles versions with or without 'v' prefix (e.g., "v0.3.9" or "0.3.9").

        Args:
            current: Current version string
            target: Target version string to compare against

        Returns:
            True if current version is below target
        """
        try:
            # Strip "v" prefix if present
            clean_current = current.lstrip("v") if current else "0.0.0"
            clean_target = target.lstrip("v") if target else "0.0.0"

            current_parts = [int(p) for p in clean_current.split(".")]
            target_parts = [int(p) for p in clean_target.split(".")]

            # Pad shorter version with zeros
            max_len = max(len(current_parts), len(target_parts))
            current_parts.extend([0] * (max_len - len(current_parts)))
            target_parts.extend([0] * (max_len - len(target_parts)))

            for curr, tgt in zip(current_parts, target_parts):
                if curr < tgt:
                    return True
                if curr > tgt:
                    return False

            return False  # Versions are equal
        except (ValueError, AttributeError):
            return False  # Invalid version format, don't trigger upgrade

    def check_version_compatibility(self) -> Tuple[bool, Optional[str], str]:
        """
        Check if the running server version meets requirements.

        Returns:
            Tuple of (is_compatible, current_version, required_version)
        """
        current_version = self.get_server_version()
        required = REQUIRED_SERVER_VERSION

        if current_version is None:
            # Can't determine version, assume compatible
            return True, None, required

        is_compatible = not self.is_version_below(current_version, required)
        return is_compatible, current_version, required

    def is_image_available(self) -> bool:
        """Check if aii-server image is pulled."""
        try:
            result = subprocess.run(
                ["docker", "image", "inspect", self.image],
                capture_output=True,
                timeout=10
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def pull_image(self, verbose: bool = True) -> bool:
        """
        Pull aii-server Docker image.

        Args:
            verbose: Show pull progress

        Returns:
            True if pull successful
        """
        if verbose:
            print(f"📦 Pulling {self.image}...")

        try:
            if verbose:
                # Show progress
                result = subprocess.run(
                    ["docker", "pull", self.image],
                    timeout=300  # 5 minutes
                )
            else:
                result = subprocess.run(
                    ["docker", "pull", self.image],
                    capture_output=True,
                    timeout=300
                )

            if result.returncode == 0:
                if verbose:
                    print("✓ Image pulled successfully")
                return True
            else:
                if verbose:
                    print("✗ Failed to pull image")
                return False

        except subprocess.TimeoutExpired:
            if verbose:
                print("✗ Image pull timed out")
            return False
        except Exception as e:
            logger.error(f"Failed to pull image: {e}")
            return False

    def create_container(self, api_key: Optional[str] = None, provider: str = "anthropic") -> bool:
        """
        Create aii-server container with proper configuration.

        Args:
            api_key: LLM API key to inject
            provider: LLM provider (anthropic, openai, etc.)

        Returns:
            True if container created successfully
        """
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Build docker run command
        # Map host port to container's internal port (26169)
        cmd = [
            "docker", "create",
            "--name", self.container_name,
            "-p", f"{self.port}:{CONTAINER_INTERNAL_PORT}",
            "-v", f"{self.config_dir}:/root/.aii",
            "--restart", "unless-stopped",
        ]

        # Add environment variables for API keys
        if api_key:
            env_var = f"{provider.upper()}_API_KEY"
            cmd.extend(["-e", f"{env_var}={api_key}"])

        # Add image
        cmd.append(self.image)

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                logger.info(f"Container '{self.container_name}' created")
                return True
            else:
                logger.error(f"Failed to create container: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Failed to create container: {e}")
            return False

    def start_container(self) -> bool:
        """Start the aii-server container."""
        try:
            result = subprocess.run(
                ["docker", "start", self.container_name],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                logger.info(f"Container '{self.container_name}' started")
                return True
            else:
                logger.error(f"Failed to start container: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Failed to start container: {e}")
            return False

    def stop_container(self) -> bool:
        """Stop the aii-server container."""
        try:
            result = subprocess.run(
                ["docker", "stop", self.container_name],
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Failed to stop container: {e}")
            return False

    def remove_container(self) -> bool:
        """Remove the aii-server container."""
        try:
            # Stop first if running
            if self.is_container_running():
                self.stop_container()

            result = subprocess.run(
                ["docker", "rm", self.container_name],
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Failed to remove container: {e}")
            return False

    def get_container_logs(self, lines: int = 50) -> str:
        """Get recent container logs."""
        try:
            result = subprocess.run(
                ["docker", "logs", "--tail", str(lines), self.container_name],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.stdout + result.stderr
        except Exception:
            return ""

    def upgrade_server(self, verbose: bool = True) -> bool:
        """
        Upgrade aii-server by stopping/removing old container and running install script.

        This ensures a clean upgrade by:
        1. Stopping the current container
        2. Removing the container (so install script creates fresh one)
        3. Running the install script to pull latest and start

        Args:
            verbose: Show progress messages

        Returns:
            True if upgrade successful
        """
        if verbose:
            print(f"\n⬆️  Upgrading Aii Server to {REQUIRED_SERVER_VERSION}...")

        try:
            # Step 1: Stop and remove old container to force fresh install
            if self.is_container_running():
                if verbose:
                    print("   Stopping old container...")
                self.stop_container()

            if self.is_container_exists():
                if verbose:
                    print("   Removing old container...")
                # Force remove without stop (already stopped above)
                subprocess.run(
                    ["docker", "rm", "-f", self.container_name],
                    capture_output=True,
                    timeout=30
                )

            # Step 2: Run the install script
            if verbose:
                print(f"   Running: curl -fsSL {INSTALL_SCRIPT_URL} | bash\n")

            result = subprocess.run(
                ["bash", "-c", f"curl -fsSL {INSTALL_SCRIPT_URL} | bash"],
                timeout=300,  # 5 minutes
                # Don't capture output - let it stream to terminal
            )

            if result.returncode == 0:
                if verbose:
                    print("\n✅ Aii Server upgraded successfully!")
                return True
            else:
                if verbose:
                    print("\n❌ Upgrade failed. Please try manually:")
                    print(f"   curl -fsSL {INSTALL_SCRIPT_URL} | bash")
                return False

        except subprocess.TimeoutExpired:
            if verbose:
                print("\n❌ Upgrade timed out. Please try manually:")
                print(f"   curl -fsSL {INSTALL_SCRIPT_URL} | bash")
            return False
        except Exception as e:
            logger.error(f"Failed to upgrade server: {e}")
            if verbose:
                print(f"\n❌ Upgrade failed: {e}")
                print(f"   Please try manually: curl -fsSL {INSTALL_SCRIPT_URL} | bash")
            return False

    def _get_container_host_port(self) -> Optional[int]:
        """Get the host port that the container is mapped to."""
        try:
            # Get port mapping from container inspect
            result = subprocess.run(
                ["docker", "container", "inspect", "-f",
                 "{{range $p, $conf := .NetworkSettings.Ports}}{{(index $conf 0).HostPort}}{{end}}",
                 self.container_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                return int(result.stdout.strip())
            return None
        except (FileNotFoundError, subprocess.TimeoutExpired, ValueError):
            return None

    async def wait_for_healthy(self, timeout: float = 30.0) -> bool:
        """
        Wait for server to become healthy.

        Args:
            timeout: Maximum seconds to wait

        Returns:
            True if server became healthy within timeout
        """
        start = time.time()
        while time.time() - start < timeout:
            if self.is_server_healthy():
                return True
            await asyncio.sleep(0.5)
        return False

    def _check_server_at_port(self, port: int) -> Tuple[bool, Optional[str]]:
        """
        Check if a compatible Aii server is running at a specific port.

        Args:
            port: Port to check

        Returns:
            Tuple of (is_compatible, version_string)
            - is_compatible: True if server is healthy and version >= required
            - version_string: The server version, or None if not available
        """
        try:
            # Check health endpoint
            url = f"http://{self.host}:{port}/health"
            with httpx.Client(trust_env=False) as client:
                response = client.get(url, timeout=2.0)
                if response.status_code != 200:
                    return False, None

            # Check version via /v0/status
            url = f"http://{self.host}:{port}/v0/status"
            with httpx.Client(trust_env=False) as client:
                response = client.get(url, timeout=2.0)
                if response.status_code == 200:
                    data = response.json()
                    version = data.get("version")
                    if version:
                        is_compatible = not self.is_version_below(version, REQUIRED_SERVER_VERSION)
                        return is_compatible, version
                    # Version not in response, assume compatible
                    return True, None

            # Server healthy but can't get version - assume compatible
            return True, None

        except Exception:
            return False, None

    async def ensure_server_running(self, verbose: bool = True, auto_upgrade: bool = True) -> Tuple[bool, str]:
        """
        Ensure aii-server is running with correct version, installing/upgrading if necessary.

        This is the main entry point for automatic server setup.

        Detection priority:
        1. Check configured port first (self.port) - may be non-default if user specified
        2. If configured port differs from default, also check default port (26169)
        3. Check Docker container's actual port if running on different port
        4. If no compatible server found, install/upgrade as needed

        Args:
            verbose: Show progress messages
            auto_upgrade: Automatically upgrade if version is outdated (default: True)

        Returns:
            Tuple of (success, message)
        """
        # =========================================================================
        # STEP 1: Check configured port first (respects user's port configuration)
        # =========================================================================
        is_compatible, version = self._check_server_at_port(self.port)
        if is_compatible:
            version_info = f" (version {version})" if version else ""
            logger.info(f"Found compatible Aii server on configured port {self.port}{version_info}")
            return True, f"Aii server is running on port {self.port}"

        # Server found on configured port but version is outdated
        if version is not None and not is_compatible:
            if verbose:
                print(f"\n⚠️  Aii Server version mismatch on port {self.port}!")
                print(f"   Current: {version}")
                print(f"   Required: {REQUIRED_SERVER_VERSION}")

            if auto_upgrade:
                # Check if it's a Docker container we can upgrade
                if self.is_docker_available() and self.is_container_running():
                    if self.upgrade_server(verbose=verbose):
                        if verbose:
                            print("⏳ Waiting for upgraded server to start...")
                        if await self.wait_for_healthy(timeout=60):
                            return True, f"Aii server upgraded to {REQUIRED_SERVER_VERSION}"
                        else:
                            return False, "Server upgraded but not responding"
                    else:
                        return False, f"Server upgrade failed. Please run manually:\n   curl -fsSL {INSTALL_SCRIPT_URL} | bash"
                else:
                    # Native server - user needs to upgrade manually
                    return False, (
                        f"Server version {version} is outdated. Required: {REQUIRED_SERVER_VERSION}\n\n"
                        f"If running aii-server natively, please update it.\n"
                        f"For Docker, run: curl -fsSL {INSTALL_SCRIPT_URL} | bash"
                    )
            else:
                return False, (
                    f"Server version {version} is outdated. Required: {REQUIRED_SERVER_VERSION}\n\n"
                    f"To upgrade, run:\n   curl -fsSL {INSTALL_SCRIPT_URL} | bash"
                )

        # =========================================================================
        # STEP 1b: If configured port differs from default, also check default port
        # =========================================================================
        if self.port != DEFAULT_PORT:
            is_compatible, version = self._check_server_at_port(DEFAULT_PORT)
            if is_compatible:
                # Found compatible server on default port - use it
                self.port = DEFAULT_PORT
                version_info = f" (version {version})" if version else ""
                logger.info(f"Found compatible Aii server on default port {DEFAULT_PORT}{version_info}")
                if verbose:
                    print(f"ℹ️  Using Aii server on default port {DEFAULT_PORT}")
                return True, f"Aii server is running on port {DEFAULT_PORT}"

            # Server found on default port but version is outdated
            if version is not None and not is_compatible:
                if verbose:
                    print(f"\n⚠️  Aii Server version mismatch on default port {DEFAULT_PORT}!")
                    print(f"   Current: {version}")
                    print(f"   Required: {REQUIRED_SERVER_VERSION}")

                if auto_upgrade:
                    if self.is_docker_available() and self.is_container_running():
                        if self.upgrade_server(verbose=verbose):
                            if verbose:
                                print("⏳ Waiting for upgraded server to start...")
                            if await self.wait_for_healthy(timeout=60):
                                return True, f"Aii server upgraded to {REQUIRED_SERVER_VERSION}"
                            else:
                                return False, "Server upgraded but not responding"
                        else:
                            return False, f"Server upgrade failed. Please run manually:\n   curl -fsSL {INSTALL_SCRIPT_URL} | bash"
                    else:
                        return False, (
                            f"Server version {version} is outdated. Required: {REQUIRED_SERVER_VERSION}\n\n"
                            f"If running aii-server natively, please update it.\n"
                            f"For Docker, run: curl -fsSL {INSTALL_SCRIPT_URL} | bash"
                        )
                else:
                    return False, (
                        f"Server version {version} is outdated. Required: {REQUIRED_SERVER_VERSION}\n\n"
                        f"To upgrade, run:\n   curl -fsSL {INSTALL_SCRIPT_URL} | bash"
                    )

        # =========================================================================
        # STEP 2: Check Docker availability and container status
        # =========================================================================
        if not self.is_docker_available():
            return False, "Docker is not installed or not running. Please install Docker first."

        # =========================================================================
        # STEP 3: Check if Docker container is running (possibly on a different port)
        # =========================================================================
        if self.is_container_running():
            container_port = self._get_container_host_port()

            # Use container's actual port for all subsequent checks
            if container_port:
                self.port = container_port
                logger.info(f"Docker container is using port {container_port}")

            # Check if server is healthy on container's port
            is_compatible, version = self._check_server_at_port(self.port)
            if is_compatible:
                version_info = f" (version {version})" if version else ""
                logger.info(f"Found compatible Aii server container on port {self.port}{version_info}")
                if verbose and self.port != DEFAULT_PORT:
                    print(f"ℹ️  Using Aii server on port {self.port} (different from default {DEFAULT_PORT})")
                return True, f"Aii server is running on port {self.port}"

            # Container running but version outdated
            if version is not None:
                if verbose:
                    print(f"\n⚠️  Aii Server version mismatch on port {self.port}!")
                    print(f"   Current: {version}")
                    print(f"   Required: {REQUIRED_SERVER_VERSION}")

                if auto_upgrade:
                    if self.upgrade_server(verbose=verbose):
                        if verbose:
                            print("⏳ Waiting for upgraded server to start...")
                        if await self.wait_for_healthy(timeout=60):
                            return True, f"Aii server upgraded to {REQUIRED_SERVER_VERSION}"
                        else:
                            return False, "Server upgraded but not responding"
                    else:
                        return False, f"Server upgrade failed. Please run manually:\n   curl -fsSL {INSTALL_SCRIPT_URL} | bash"
                else:
                    return False, (
                        f"Server version {version} is outdated. Required: {REQUIRED_SERVER_VERSION}\n\n"
                        f"To upgrade, run:\n   curl -fsSL {INSTALL_SCRIPT_URL} | bash"
                    )

            # Container running but not healthy yet - wait for it
            if verbose:
                print(f"⏳ Waiting for server to become healthy on port {self.port}...")
            if await self.wait_for_healthy(timeout=10):
                # Re-check version after becoming healthy
                is_compatible, version, required = self.check_version_compatibility()
                if not is_compatible and auto_upgrade:
                    if verbose:
                        print(f"\n⚠️  Server version {version} is outdated (requires {required})")
                    if self.upgrade_server(verbose=verbose):
                        if await self.wait_for_healthy(timeout=60):
                            return True, f"Aii server upgraded to {required}"
                        else:
                            return False, "Server upgraded but not responding"
                    else:
                        return False, f"Server upgrade failed"
                return True, f"Aii server is running on port {self.port}"
            else:
                logs = self.get_container_logs(20)
                return False, f"Server container is running but not responding on port {self.port}.\nLogs:\n{logs}"

        # =========================================================================
        # STEP 4: Container exists but stopped - start it
        # =========================================================================
        if self.is_container_exists():
            if verbose:
                print("🔄 Starting aii-server container...")
            if self.start_container():
                if verbose:
                    print("⏳ Waiting for server to start...")
                if await self.wait_for_healthy(timeout=30):
                    # Check version after starting
                    is_compatible, current_version, required_version = self.check_version_compatibility()
                    if not is_compatible and auto_upgrade:
                        if verbose:
                            print(f"\n⚠️  Server version {current_version} is outdated (requires {required_version})")
                        if self.upgrade_server(verbose=verbose):
                            if await self.wait_for_healthy(timeout=60):
                                return True, f"Aii server upgraded to {required_version}"
                            else:
                                return False, "Server upgraded but not responding"
                        else:
                            return False, f"Server upgrade failed"

                    if verbose:
                        print("✓ Aii server started successfully")
                    return True, "Aii server started"
                else:
                    logs = self.get_container_logs(20)
                    return False, f"Server started but not responding.\nLogs:\n{logs}"
            else:
                return False, "Failed to start aii-server container"

        # =========================================================================
        # STEP 5: No container exists - fresh install via install script
        # =========================================================================
        if verbose:
            print("🚀 Setting up Aii server for the first time...")
            print(f"   Running: curl -fsSL {INSTALL_SCRIPT_URL} | bash\n")

        # Use the install script for fresh installations
        # This ensures we get the correct version and proper configuration
        if self.upgrade_server(verbose=verbose):
            if verbose:
                print("⏳ Waiting for server to initialize...")
            if await self.wait_for_healthy(timeout=60):
                if verbose:
                    print("✅ Aii server is ready!")
                return True, "Aii server installed and started successfully"
            else:
                logs = self.get_container_logs(30)
                return False, f"Server installed but not responding after 60s.\nLogs:\n{logs}"
        else:
            return False, f"Failed to install Aii server. Please try manually:\n   curl -fsSL {INSTALL_SCRIPT_URL} | bash"

    def get_status(self) -> dict:
        """
        Get detailed server status including version information.

        Checks for server on both default port and container's actual port.

        Returns:
            dict with status information
        """
        docker_available = self.is_docker_available()
        container_exists = self.is_container_exists() if docker_available else False
        container_running = self.is_container_running() if docker_available else False

        # First check default port
        server_healthy = False
        current_version = None
        version_compatible = True
        active_port = self.port

        is_compatible, version = self._check_server_at_port(DEFAULT_PORT)
        if version is not None:
            # Server found on default port
            server_healthy = True
            current_version = version
            version_compatible = is_compatible
            active_port = DEFAULT_PORT
        elif docker_available and container_running:
            # Check container's actual port if different from default
            container_port = self._get_container_host_port()
            if container_port and container_port != DEFAULT_PORT:
                is_compatible, version = self._check_server_at_port(container_port)
                if version is not None:
                    server_healthy = True
                    current_version = version
                    version_compatible = is_compatible
                    active_port = container_port

        return {
            "docker_available": docker_available,
            "container_exists": container_exists,
            "container_running": container_running,
            "server_healthy": server_healthy,
            "server_version": current_version,
            "required_version": REQUIRED_SERVER_VERSION,
            "version_compatible": version_compatible,
            "container_name": self.container_name,
            "image": self.image,
            "port": active_port,
            "default_port": DEFAULT_PORT,
            "host": self.host,
            "health_endpoint": f"http://{self.host}:{active_port}/health",
        }


def get_docker_install_instructions() -> str:
    """Get platform-specific Docker installation instructions."""
    import platform
    system = platform.system().lower()

    if system == "darwin":
        return """
To install Docker on macOS:
  1. Download Docker Desktop from https://www.docker.com/products/docker-desktop
  2. Install and start Docker Desktop
  3. Run 'aii' again
"""
    elif system == "linux":
        return """
To install Docker on Linux:
  curl -fsSL https://get.docker.com | sh
  sudo systemctl start docker
  sudo usermod -aG docker $USER
  # Log out and back in, then run 'aii' again
"""
    else:
        return """
To install Docker:
  Visit https://www.docker.com/products/docker-desktop
"""


# Convenience function for CLI
async def ensure_aii_server(config=None, verbose: bool = True) -> Tuple[bool, str]:
    """
    Convenience function to ensure aii-server is running.

    Args:
        config: Optional ConfigManager instance
        verbose: Show progress messages

    Returns:
        Tuple of (success, message)
    """
    manager = AiiServerManager(config=config)
    return await manager.ensure_server_running(verbose=verbose)
