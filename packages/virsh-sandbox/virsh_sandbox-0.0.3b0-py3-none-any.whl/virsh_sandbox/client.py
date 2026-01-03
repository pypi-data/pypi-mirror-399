# coding: utf-8

"""
Unified VirshSandbox Client

This module provides a unified client wrapper for the virsh-sandbox SDK,
offering a cleaner interface compared to using individual API classes directly.

Example:
    from virsh_sandbox import VirshSandbox

    # Create a client
    client = VirshSandbox(host="http://localhost:8080", tmux_host="http://localhost:8081")

    # Use the APIs through namespaced properties
    await client.sandboxes.start_sandbox(request)
    await client.commands.run_command(request)
    await client.files.read_file(request)
"""

from typing import Optional

from virsh_sandbox.api.ansible_api import AnsibleApi
from virsh_sandbox.api.audit_api import AuditApi
from virsh_sandbox.api.command_api import CommandApi
from virsh_sandbox.api.file_api import FileApi
from virsh_sandbox.api.health_api import HealthApi
from virsh_sandbox.api.human_api import HumanApi
from virsh_sandbox.api.plan_api import PlanApi
from virsh_sandbox.api.sandbox_api import SandboxApi
from virsh_sandbox.api.tmux_api import TmuxApi
from virsh_sandbox.api.vms_api import VMsApi
from virsh_sandbox.api_client import ApiClient
from virsh_sandbox.configuration import Configuration


class VirshSandbox:
    """Unified client for the virsh-sandbox API.

    This class provides a single entry point for all virsh-sandbox API operations,
    with support for separate hosts for the main API and tmux API.

    Args:
        host: Base URL for the main virsh-sandbox API (default: "http://localhost:8080")
        tmux_host: Base URL for the tmux API (default: same as host)
        api_key: Optional API key for authentication
        access_token: Optional access token for OAuth/Bearer authentication
        username: Optional username for HTTP basic authentication
        password: Optional password for HTTP basic authentication
        verify_ssl: Whether to verify SSL certificates (default: True)
        ssl_ca_cert: Path to a file of concatenated CA certificates in PEM format
        retries: Number of retries for API requests

    Attributes:
        ansible: Access AnsibleApi operations
        audit: Access AuditApi operations
        command: Access CommandApi operations
        file: Access FileApi operations
        health: Access HealthApi operations
        human: Access HumanApi operations
        plan: Access PlanApi operations
        sandbox: Access SandboxApi operations
        tmux: Access TmuxApi operations
        vms: Access VMsApi operations

    Example:
        >>> from virsh_sandbox import VirshSandbox
        >>> client = VirshSandbox(host="http://localhost:8080")
        >>> # Use API methods
        >>> await client.sandbox.start_sandbox(request)
    """

    def __init__(
        self,
        host: str = "http://localhost:8080",
        tmux_host: Optional[str] = None,
        api_key: Optional[str] = None,
        access_token: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        verify_ssl: bool = True,
        ssl_ca_cert: Optional[str] = None,
        retries: Optional[int] = None,
    ) -> None:
        """Initialize the VirshSandbox client."""
        # Create configuration for main API
        self._main_config = Configuration(
            host=host,
            api_key={"Authorization": api_key} if api_key else None,
            access_token=access_token,
            username=username,
            password=password,
            ssl_ca_cert=ssl_ca_cert,
            retries=retries,
        )
        self._main_config.verify_ssl = verify_ssl

        # Create API client for main API
        self._main_api_client = ApiClient(configuration=self._main_config)

        # Create configuration and client for tmux API (may be on different host)
        tmux_host = tmux_host or host
        if tmux_host != host:
            self._tmux_config = Configuration(
                host=tmux_host,
                api_key={"Authorization": api_key} if api_key else None,
                access_token=access_token,
                username=username,
                password=password,
                ssl_ca_cert=ssl_ca_cert,
                retries=retries,
            )
            self._tmux_config.verify_ssl = verify_ssl
            self._tmux_api_client = ApiClient(configuration=self._tmux_config)
        else:
            self._tmux_config = self._main_config
            self._tmux_api_client = self._main_api_client

        # Initialize API instances lazily
        self._ansible: Optional[AnsibleApi] = None
        self._audit: Optional[AuditApi] = None
        self._command: Optional[CommandApi] = None
        self._file: Optional[FileApi] = None
        self._health: Optional[HealthApi] = None
        self._human: Optional[HumanApi] = None
        self._plan: Optional[PlanApi] = None
        self._sandbox: Optional[SandboxApi] = None
        self._tmux: Optional[TmuxApi] = None
        self._vms: Optional[VMsApi] = None

    @property
    def ansible(self) -> AnsibleApi:
        """Access AnsibleApi operations."""
        if self._ansible is None:
            self._ansible = AnsibleApi(api_client=self._main_api_client)
        return self._ansible

    @property
    def audit(self) -> AuditApi:
        """Access AuditApi operations."""
        if self._audit is None:
            self._audit = AuditApi(api_client=self._tmux_api_client)
        return self._audit

    @property
    def command(self) -> CommandApi:
        """Access CommandApi operations."""
        if self._command is None:
            self._command = CommandApi(api_client=self._tmux_api_client)
        return self._command

    @property
    def file(self) -> FileApi:
        """Access FileApi operations."""
        if self._file is None:
            self._file = FileApi(api_client=self._tmux_api_client)
        return self._file

    @property
    def health(self) -> HealthApi:
        """Access HealthApi operations."""
        if self._health is None:
            self._health = HealthApi(api_client=self._tmux_api_client)
        return self._health

    @property
    def human(self) -> HumanApi:
        """Access HumanApi operations."""
        if self._human is None:
            self._human = HumanApi(api_client=self._tmux_api_client)
        return self._human

    @property
    def plan(self) -> PlanApi:
        """Access PlanApi operations."""
        if self._plan is None:
            self._plan = PlanApi(api_client=self._tmux_api_client)
        return self._plan

    @property
    def sandbox(self) -> SandboxApi:
        """Access SandboxApi operations."""
        if self._sandbox is None:
            self._sandbox = SandboxApi(api_client=self._main_api_client)
        return self._sandbox

    @property
    def tmux(self) -> TmuxApi:
        """Access TmuxApi operations."""
        if self._tmux is None:
            self._tmux = TmuxApi(api_client=self._tmux_api_client)
        return self._tmux

    @property
    def vms(self) -> VMsApi:
        """Access VMsApi operations."""
        if self._vms is None:
            self._vms = VMsApi(api_client=self._main_api_client)
        return self._vms

    @property
    def configuration(self) -> Configuration:
        """Get the main API configuration object."""
        return self._main_config

    @property
    def tmux_configuration(self) -> Configuration:
        """Get the tmux API configuration object."""
        return self._tmux_config

    def set_debug(self, debug: bool) -> None:
        """Enable or disable debug mode for all API clients.

        Args:
            debug: Whether to enable debug mode
        """
        self._main_config.debug = debug
        if self._tmux_config is not self._main_config:
            self._tmux_config.debug = debug

    async def close(self) -> None:
        """Close the API client connections.

        Call this method when you're done using the client to clean up resources.
        """
        # Clean up REST clients if they have close methods
        if hasattr(self._main_api_client.rest_client, "close"):
            await self._main_api_client.rest_client.close()
        if self._tmux_api_client is not self._main_api_client:
            if hasattr(self._tmux_api_client.rest_client, "close"):
                await self._tmux_api_client.rest_client.close()

    async def __aenter__(self) -> "VirshSandbox":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()
