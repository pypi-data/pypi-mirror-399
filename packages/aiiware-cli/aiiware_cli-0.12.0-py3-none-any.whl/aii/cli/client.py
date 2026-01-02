# Copyright 2025-present AiiWare.com. All Rights Reserved.
#
# This source code is proprietary and confidential to AiiWare.com.
# Unauthorized copying, modification, distribution, or use is strictly
# prohibited without prior written permission.

"""
CLI client that communicates with Aii Server via WebSocket.

Features:
- Ensure server is running (auto-start if needed)
- Establish WebSocket connection
- Send requests and stream responses
- Handle errors with retry and fail-fast strategy
- Format output for terminal display
"""


import asyncio
import logging
from typing import Optional, Dict, Any
from aii.cli.server_manager import ServerManager
from aii.cli.websocket_client import (
    AiiWebSocketClient,
    create_websocket_client,
    WebSocketConnectionError,
    WebSocketTimeout
)
from aii.cli.debug import debug_print

logger = logging.getLogger(__name__)


class AiiCLIClient:
    """
    CLI client that communicates with Aii Server via WebSocket.

    Responsibilities:
    - Ensure server is running (auto-start if needed)
    - Establish WebSocket connection
    - Send requests and stream responses
    - Handle errors with retry and fail-fast strategy
    """

    def __init__(self, config_manager):
        """
        Initialize CLI client.

        Args:
            config_manager: ConfigManager instance
        """
        self.config = config_manager
        self.server_manager = ServerManager(config_manager)
        self.ws_client: Optional[AiiWebSocketClient] = None
        self.max_retries = config_manager.get("cli.max_retries", 3)
        self.api_url = config_manager.get("api.url", "http://localhost:26169")
        self.api_key = self._get_or_create_api_key()
        debug_print(f"CLIENT: API URL: {self.api_url}, API Key: {self.api_key[:20]}...")

        # Initialize MCP client for client-side MCP operations
        self.mcp_client = self._initialize_mcp_client()

    def _get_or_create_api_key(self) -> str:
        """Get or create API key from config"""
        # Check if get_or_create_api_key method exists
        if hasattr(self.config, 'get_or_create_api_key'):
            return self.config.get_or_create_api_key()

        # Fallback: get from config
        api_keys = self.config.get("api.keys", [])
        if api_keys:
            return api_keys[0]

        # Use default development API key if none exists
        default_key = "aii_sk_7WyvfQ0PRzufJ1G66Qn8Sm4gW9Tealpo6vOWDDUeiv4"
        self.config.set("api.keys", [default_key])
        return default_key

    def _get_llm_credentials(self) -> dict:
        """
        Get LLM provider credentials from config for passing to server.

        v0.12.0: The server is stateless - client passes LLM credentials with each request.
        This allows different clients to use different providers/keys.

        Returns:
            dict with llm_provider and llm_api_key (if configured)
        """
        credentials = {}

        # Get configured LLM provider
        provider = self.config.get("llm.provider")
        if provider:
            credentials["llm_provider"] = provider

            # Get the API key for this provider from secrets
            secret_key = f"{provider}_api_key"
            if hasattr(self.config, 'get_secret'):
                api_key = self.config.get_secret(secret_key)
                if api_key:
                    credentials["llm_api_key"] = api_key

        return credentials

    async def _ensure_config_initialized(self) -> None:
        """
        Ensure CLI configuration is initialized before any operation.

        v0.12.0: Configuration must be set up before server operations.
        If not configured, offers to run setup wizard inline.

        Raises:
            RuntimeError: If configuration is not initialized and user declines setup
        """
        # Check if LLM provider is configured
        provider = self.config.get("llm.provider")
        needs_setup = False
        setup_reason = ""

        if not provider:
            needs_setup = True
            setup_reason = "Aii CLI not configured"
        else:
            # Check if API key is configured for the provider
            secret_key = f"{provider}_api_key"
            api_key = None
            if hasattr(self.config, 'get_secret'):
                api_key = self.config.get_secret(secret_key)

            if not api_key:
                needs_setup = True
                setup_reason = f"API key not configured for {provider}"

        if needs_setup:
            # Offer to run setup wizard inline
            await self._run_inline_setup(setup_reason)

    async def _run_inline_setup(self, reason: str) -> None:
        """
        Run setup wizard inline when config is missing.

        v0.12.0: Seamless onboarding - don't make user run separate command.

        Args:
            reason: Why setup is needed (displayed to user)

        Raises:
            RuntimeError: If user declines or setup fails
        """
        import sys

        print(f"\n⚠️  {reason}.\n")

        # Check if running in interactive mode
        if not sys.stdin.isatty():
            # Non-interactive mode - can't prompt
            raise RuntimeError(
                f"❌ {reason}.\n\n"
                "Please run the setup wizard first:\n"
                "  aii config init\n\n"
                "This will configure your LLM provider and API key."
            )

        # Prompt user
        try:
            response = input("Would you like to run setup now? [Y/n]: ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\n")
            raise RuntimeError("Setup cancelled.")

        if response in ("", "y", "yes"):
            print()  # Blank line before setup
            # Run setup wizard
            from aii.cli.setup import SetupWizard

            wizard = SetupWizard()
            success = await wizard.run()

            if not success:
                raise RuntimeError(
                    "❌ Setup was not completed.\n\n"
                    "Please run 'aii config init' to complete setup."
                )

            print("\n✅ Configuration complete!")
            print("Continuing with your request...\n")

            # Reload config to pick up new settings
            self.config.reload()
        else:
            raise RuntimeError(
                "❌ Setup required.\n\n"
                "Please run 'aii config init' when ready."
            )

    def _initialize_mcp_client(self):
        """
        Initialize MCP client for client-side MCP operations.

        Returns:
            MCPClientManager if MCP servers are configured, None otherwise
        """
        try:
            from aii.data.integrations.mcp.client_manager import MCPClientManager
            from aii.data.integrations.mcp.config_loader import MCPConfigLoader

            # Create config loader and load MCP servers from config
            config_loader = MCPConfigLoader()
            config_loader.load_configurations()

            # Check if any servers are configured
            if not config_loader.servers:
                debug_print("CLIENT: No MCP servers configured")
                return None

            # Create MCP client manager
            mcp_client = MCPClientManager(
                config_loader=config_loader,
                enable_health_monitoring=False,
                suppress_output=True
            )
            debug_print(f"CLIENT: MCP client initialized with {len(config_loader.servers)} servers")
            return mcp_client

        except ImportError:
            logger.warning("MCP integration not available (missing dependencies)")
            return None
        except Exception as e:
            logger.warning(f"Failed to initialize MCP client: {e}")
            return None

    async def execute_command(
        self,
        user_input: str,
        output_mode: Optional[str] = None,
        offline: bool = False,
        model: Optional[str] = None,  # v0.8.0: Model override
        spinner = None,  # Optional spinner to stop when streaming starts
        suppress_streaming: bool = False,  # v0.12.0: Suppress token output for controlled display
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute command via WebSocket API with retry logic.

        Flow:
        1. Ensure server is running (auto-start if needed)
        2. Connect WebSocket (or reuse existing connection)
        3. Send request with streaming
        4. Receive and format response
        5. On error, retry with exponential backoff (fail fast if exhausted)

        Args:
            user_input: User's natural language prompt
            output_mode: Output mode (clean, standard, thinking)
            offline: Whether to run in offline mode
            model: Optional model override (e.g., 'kimi-k2-thinking', 'gpt-4.1-mini')
                   If None, uses configured model from llm.model config
            spinner: Optional spinner instance to stop when streaming starts
            suppress_streaming: If True, don't print tokens as they arrive (for controlled display)
            **kwargs: Additional parameters

        Returns:
            dict: Execution result with metadata

        Raises:
            RuntimeError: If server fails to start or request fails after retries
        """
        # v0.12.0: Step 0 - Ensure config is initialized FIRST
        # Must check before server operations - no point starting server without credentials
        await self._ensure_config_initialized()

        # v0.9.5: Get configured model if not explicitly provided
        # This ensures the user's configured model is sent to the server
        # (important for Aii Server which doesn't share Python config)
        if model is None:
            model = self.config.get("llm.model")

        # Step 1: Ensure server is running
        server_ready = await self._ensure_server_ready()
        if not server_ready:
            # Build helpful error message based on configuration
            host = self.server_manager.host
            port = self.server_manager.port
            is_default = (host in ["127.0.0.1", "localhost"] and port == 26169)

            if is_default:
                # Default config - auto-start failed
                error_msg = (
                    "❌ Failed to start Aii server.\n\n"
                    "Try:\n"
                    "  1. Check if port 26169 is available: lsof -i :26169\n"
                    "  2. Start server manually: aii serve\n"
                    "  3. Check logs: ~/.aii/logs/server.log"
                )
            else:
                # Custom host/port - user must start manually
                # Extract just the command part from user_input (remove "translate hello to french" → "translate hello")
                short_example = " ".join(user_input.split()[:2]) if len(user_input.split()) > 1 else user_input
                error_msg = (
                    f"❌ Could not connect to Aii server at {host}:{port}\n\n"
                    f"Server may not be running. To start:\n"
                    f"  aii serve --host {host} --port {port}\n\n"
                    f"Or use default server (auto-starts):\n"
                    f"  aii {short_example}"
                )

            raise RuntimeError(error_msg)

        # Step 2-4: Execute with retry
        last_error = None
        for attempt in range(self.max_retries):
            try:
                # Connect WebSocket (or reuse)
                if not self.ws_client or not self.ws_client.is_connected():
                    debug_print("CLIENT: Creating WebSocket client...")
                    self.ws_client = create_websocket_client(self.api_url, self.api_key, self.mcp_client)
                    await self.ws_client.connect()
                    debug_print("CLIENT: WebSocket connected!")

                # Send request (v0.6.0 unified format)
                # Pattern 1 (LLM-First): system_prompt=null triggers intent recognition
                request = {
                    "system_prompt": None,  # null = Server performs intent recognition
                    "user_prompt": user_input,  # User's natural language input
                    "output_mode": output_mode,
                    "offline": offline,
                    "streaming": True,  # v0.9.5: Enable streaming for incremental output
                    **kwargs
                }

                # v0.8.0: Add model override if provided
                # v0.9.5: Model is now always read from config if not explicitly provided
                if model:
                    request["model"] = model

                # v0.12.0: Add LLM provider credentials
                # Server is stateless - client passes LLM credentials with each request
                llm_credentials = self._get_llm_credentials()
                request.update(llm_credentials)

                debug_print(f"CLIENT: Sending unified request (LLM-first): model={model}, provider={llm_credentials.get('llm_provider')}, user_prompt={user_input[:50]}...")

                # Track if we've cleared the loading indicator
                loading_cleared = [False]  # Use list to allow modification in lambda

                def on_token_callback(token: str):
                    """Print token and clear loading indicator on first token"""
                    # v0.12.0: When suppress_streaming is True, don't clear spinner or print tokens
                    # The caller will handle stopping the spinner after receiving the full result
                    if suppress_streaming:
                        loading_cleared[0] = True  # Mark that tokens were received
                        return

                    if not loading_cleared[0]:
                        import sys
                        # Stop spinner and CLEAR the line immediately
                        if spinner:
                            # Use stop_sync with clear=True to clear the spinner line
                            spinner.stop_sync(clear=True)

                        loading_cleared[0] = True
                    print(token, end="", flush=True)

                # Stream response tokens
                result = await self.ws_client.execute_request(
                    request,
                    on_token=on_token_callback
                )

                # Add flag to indicate if streaming occurred (tokens were printed)
                result["_streaming_occurred"] = loading_cleared[0]

                return result

            except WebSocketTimeout as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                    logger.warning(f"Request timeout, retrying in {wait_time}s... (attempt {attempt + 1}/{self.max_retries})")
                    await asyncio.sleep(wait_time)
                continue

            except WebSocketConnectionError as e:
                last_error = e
                error_msg = str(e)

                # Check if this is a prerequisite error (config issue) - don't retry
                if "Prerequisites not met" in error_msg or "aii config init" in error_msg:
                    # This is a configuration issue, not a transient error
                    # Extract just the first line for logging (without guidance)
                    log_msg = error_msg.split('\n')[0]
                    logger.error(f"WebSocket execution error: {log_msg}")

                    # Fail immediately with the full guidance
                    raise RuntimeError(f"❌ {error_msg}")

                # For other connection errors, log full message
                logger.error(f"WebSocket connection lost: {error_msg}")

                # Try to reconnect for other connection errors
                self.ws_client = None
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.warning(f"Reconnecting in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                continue

            except Exception as e:
                last_error = e
                logger.error(f"Command execution failed: {e}")
                raise

        # All retries exhausted - fail fast
        raise RuntimeError(
            f"❌ Server timeout after {self.max_retries} attempts.\n\n"
            f"Last error: {last_error}\n\n"
            f"Possible causes:\n"
            f"  • LLM provider is slow or unavailable\n"
            f"  • Server is overloaded\n"
            f"  • Network issues\n\n"
            f"Try:\n"
            f"  1. Retry your command: aii \"{user_input}\"\n"
            f"  2. Check server status: aii serve status\n"
            f"  3. Restart server: aii serve restart\n"
            f"  4. Use faster model: aii config model"
        )

    async def execute_function(
        self,
        function_name: str,
        parameters: Dict[str, Any],
        output_mode: Optional[str] = None,
        model: Optional[str] = None,  # v0.9.5: Model override
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute a specific function directly (bypass intent recognition).

        This method is used by client-side domain operations (v0.6.0) to call
        server functions without going through intent recognition. This ensures
        prompts like "Generate a commit message..." don't get misinterpreted.

        Args:
            function_name: Exact function name (e.g., "universal_generate")
            parameters: Function parameters as dict
            output_mode: Output mode (CLEAN/STANDARD/THINKING)
            model: Optional model override. If None, uses configured model from llm.model config
            **kwargs: Additional parameters

        Returns:
            dict: Execution result with success, result, data, metadata

        Raises:
            RuntimeError: If server fails or request fails
        """
        debug_print(f"CLIENT: execute_function - {function_name}, params: {list(parameters.keys())}")

        # v0.12.0: Ensure config is initialized first
        await self._ensure_config_initialized()

        # v0.9.5: Get configured model if not explicitly provided
        if model is None:
            model = self.config.get("llm.model")

        # Step 1: Ensure server is running
        server_ready = await self._ensure_server_ready()
        if not server_ready:
            raise RuntimeError("❌ Failed to start Aii server")

        # Step 2: Initialize and connect WebSocket client if needed
        if not self.ws_client or not self.ws_client.is_connected():
            debug_print("CLIENT: Creating WebSocket client for execute_function...")
            self.ws_client = create_websocket_client(self.api_url, self.api_key, self.mcp_client)
            await self.ws_client.connect()
            debug_print("CLIENT: WebSocket connected!")

        # Step 3: Call server's execute endpoint with explicit function name
        # This bypasses intent recognition and calls the function directly
        try:
            request = {
                "function": function_name,
                "params": parameters,
                "output_mode": output_mode or "STANDARD",
                "streaming": True  # v0.9.5: Enable streaming for incremental output
            }

            # v0.9.5: Add model if available
            if model:
                request["model"] = model

            # v0.12.0: Add LLM provider credentials
            llm_credentials = self._get_llm_credentials()
            request.update(llm_credentials)

            result = await self.ws_client.execute_request(request)
            debug_print(f"CLIENT: execute_function result - success: {result.get('success')}")
            return result

        except Exception as e:
            debug_print(f"CLIENT: execute_function failed - {e}")
            raise RuntimeError(f"Failed to execute {function_name}: {e}")

    async def execute_with_system_prompt(
        self,
        system_prompt: str,
        user_input: str,
        output_mode: Optional[str] = None,
        spinner = None,
        model: Optional[str] = None,  # v0.9.5: Model override
        silent: bool = False,  # v0.11.2: Suppress output for internal use
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute natural language prompt with system prompt (bypass intent recognition).

        This method is used for natural_language mode prompts (v0.6.1 Prompt Library Refactor).
        Instead of using intent recognition, it sends the system prompt + user input directly
        to the LLM for processing.

        Flow:
        1. Ensure server is running
        2. Connect WebSocket
        3. Send direct_llm_call request with system_prompt + user_prompt
        4. Stream response tokens
        5. Return result

        Args:
            system_prompt: System prompt that defines LLM behavior
            user_input: User's natural language input to be processed
            output_mode: Output mode (CLEAN/STANDARD/THINKING)
            spinner: Optional spinner instance to stop when streaming starts
            model: Optional model override. If None, uses configured model from llm.model config
            silent: If True, suppress token output (for internal API calls)
            **kwargs: Additional parameters (e.g., prompt_name for metadata)

        Returns:
            dict: Execution result with success, result, data, metadata

        Raises:
            RuntimeError: If server fails or request fails

        Example:
            # For word-explanation prompt
            system_prompt = "You are a language expert. Explain the word with pronunciation..."
            result = await client.execute_with_system_prompt(
                system_prompt=system_prompt,
                user_input="prompt",
                output_mode="CLEAN"
            )
        """
        debug_print(f"CLIENT: execute_with_system_prompt - user_input: {user_input[:50]}...")

        # v0.12.0: Ensure config is initialized first
        await self._ensure_config_initialized()

        # v0.9.5: Get configured model if not explicitly provided
        if model is None:
            model = self.config.get("llm.model")

        # Step 1: Ensure server is running
        server_ready = await self._ensure_server_ready()
        if not server_ready:
            raise RuntimeError("❌ Failed to start Aii server")

        # Step 2: Connect WebSocket (or reuse)
        if not self.ws_client or not self.ws_client.is_connected():
            debug_print("CLIENT: Creating WebSocket client for execute_with_system_prompt...")
            self.ws_client = create_websocket_client(self.api_url, self.api_key, self.mcp_client)
            await self.ws_client.connect()
            debug_print("CLIENT: WebSocket connected!")

        # Step 3: Send direct_llm_call request (v0.6.1 unified format)
        # Pattern 2 (Direct LLM Call): system_prompt=string bypasses intent recognition
        request = {
            "system_prompt": system_prompt,  # Non-null = Direct LLM call
            "user_prompt": user_input,       # User's natural language input
            "output_mode": output_mode or "CLEAN",
            **kwargs
        }

        # v0.9.5: Add model if available
        if model:
            request["model"] = model

        # v0.12.0: Add LLM provider credentials
        llm_credentials = self._get_llm_credentials()
        request.update(llm_credentials)

        debug_print(f"CLIENT: Sending direct_llm_call request (bypass intent recognition, model={model}, provider={llm_credentials.get('llm_provider')})")

        # Track if we've cleared the loading indicator
        loading_cleared = [False]

        def on_token_callback(token: str):
            """Print token and clear loading indicator on first token"""
            if not loading_cleared[0]:
                # Stop spinner and clear the line immediately
                if spinner:
                    spinner.stop_sync(clear=True)
                loading_cleared[0] = True
            # v0.11.2: Only print if not in silent mode
            if not silent:
                print(token, end="", flush=True)

        try:
            # Stream response tokens
            result = await self.ws_client.execute_request(
                request,
                on_token=on_token_callback
            )

            # Add flag to indicate if streaming occurred
            result["_streaming_occurred"] = loading_cleared[0]

            return result

        except (WebSocketConnectionError, WebSocketTimeout) as e:
            debug_print(f"CLIENT: execute_with_system_prompt failed - {e}")
            raise RuntimeError(f"❌ Direct LLM call failed: {e}")

    async def recognize_intent(self, user_input: str) -> Dict[str, Any]:
        """
        Recognize intent WITHOUT executing (Phase 1 of two-phase confirmation flow).

        This method analyzes the user's input to determine which function would be called,
        what parameters would be used, and whether confirmation is required, but does NOT
        execute the function.

        Args:
            user_input: Natural language input

        Returns:
            dict: Recognition result with:
                - function: Function name that would be called
                - parameters: Parameters that would be passed
                - safety: Safety level (SAFE, RISKY, DESTRUCTIVE)
                - description: Human-readable description
                - requires_confirmation: Whether confirmation is needed

        Raises:
            RuntimeError: If server fails to start or recognition fails
        """

        # Step 1: Ensure server is running
        server_ready = await self._ensure_server_ready()
        if not server_ready:
            raise RuntimeError(
                "❌ Failed to start Aii server.\n\n"
                "Try:\n"
                "  1. Check if port 26169 is available: lsof -i :26169\n"
                "  2. Start server manually: aii serve\n"
                "  3. Check logs: ~/.aii/logs/server.log"
            )

        # Step 2: Connect WebSocket (or reuse)
        if not self.ws_client or not self.ws_client.is_connected():
            debug_print("CLIENT: Creating WebSocket client...")
            self.ws_client = create_websocket_client(self.api_url, self.api_key, self.mcp_client)
            await self.ws_client.connect()
            debug_print("CLIENT: WebSocket connected!")

        # Step 3: Call recognize_intent on WebSocket client
        try:
            result = await self.ws_client.recognize_intent(user_input)
            debug_print(f"CLIENT: Recognition result - {result.get('function')} (requires_confirmation: {result.get('requires_confirmation')})")
            return result
        except (WebSocketConnectionError, WebSocketTimeout) as e:
            raise RuntimeError(f"❌ Intent recognition failed: {e}")

    async def _ensure_server_ready(self) -> bool:
        """
        Ensure server is running with correct version, start/upgrade if needed.

        v0.12.0: Uses AiiServerManager for Docker-based aii-server.
        Auto-start ONLY happens for default localhost:26169.
        For custom hosts/ports, user must start server manually.

        Returns:
            True if server is ready
        """
        from .aii_server_manager import AiiServerManager

        # v0.12.0: Only auto-start if using default localhost:26169
        # If user specified custom --host, they must start server manually
        is_default_config = (
            self.server_manager.host in ["127.0.0.1", "localhost"] and
            self.server_manager.port == 26169
        )

        # v0.12.0: Use AiiServerManager for Docker-based server
        # This handles both health check AND version check
        aii_server = AiiServerManager(config=self.config, port=self.server_manager.port)

        # Check if Docker is available
        if aii_server.is_docker_available():
            logger.info("Using Docker-based aii-server...")
            # ensure_server_running checks: health, version, and auto-upgrades if needed
            success, message = await aii_server.ensure_server_running(verbose=True)

            # Always update port if a different one was discovered (even if setup had issues)
            # This handles cases where server is running but health check timed out
            if aii_server.port != self.server_manager.port:
                logger.info(f"Updating client port from {self.server_manager.port} to {aii_server.port}")
                self.server_manager.port = aii_server.port
                new_api_url = f"http://{self.server_manager.host}:{aii_server.port}"
                self.api_url = new_api_url

                # Persist the discovered port to config so future runs use it directly
                try:
                    self.config.set("api.url", new_api_url)
                    logger.info(f"Saved api.url to config: {new_api_url}")
                except Exception as e:
                    logger.warning(f"Could not save api.url to config: {e}")

            if success:
                logger.info("Aii server is ready")
                return True
            else:
                # Setup reported failure, but server might still be running
                # Do a final health check before giving up
                logger.warning(f"Server setup reported: {message}")
                logger.info("Performing final health check...")

                if aii_server.is_server_healthy():
                    logger.info(f"Server is actually healthy on port {aii_server.port}, proceeding")
                    return True

                logger.error(f"Failed to ensure aii-server: {message}")
                print(f"\n❌ {message}")
                return False

        # No Docker available - check if server is running (legacy mode)
        if self.server_manager.is_server_running():
            logger.debug("Server already running (non-Docker)")
            return True

        if not is_default_config:
            # Custom host/port - don't auto-start
            logger.error(f"Server not running on {self.server_manager.host}:{self.server_manager.port}")
            return False

        # Fallback: Try legacy server start (aii serve)
        logger.info("Docker not available, trying legacy server start...")
        started = await self.server_manager.start_server(background=True)

        if not started:
            logger.error("Failed to auto-start server")
            return False

        # Wait for server to be ready (max 5 seconds)
        for i in range(50):  # 50 × 100ms = 5s
            await asyncio.sleep(0.1)
            if self.server_manager.is_server_running():
                logger.info(f"Server ready after {(i+1)*100}ms")
                return True

        logger.error("Server started but not responding")
        return False

    async def close(self):
        """Close WebSocket connection"""
        if self.ws_client:
            await self.ws_client.close()
            self.ws_client = None
            logger.debug("CLI client closed")
