"""
Remote Runtime for Esprit CLI.

Connects to the hosted Esprit backend service instead of local Docker.
This allows users to run scans without needing Docker installed locally.
"""

from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass
from typing import Any

import httpx

from esprit.auth.credentials import get_auth_token, get_credentials, is_authenticated


# Configuration
API_BASE_URL = os.getenv("ESPRIT_API_URL", "https://api.esprit.dev")


@dataclass
class SandboxInfo:
    """Information about a remote sandbox."""

    sandbox_id: str
    status: str
    tool_server_url: str | None
    public_ip: str | None


class RemoteRuntime:
    """
    Runtime that connects to hosted sandbox service.

    Instead of running Docker locally, this runtime:
    1. Creates a sandbox on AWS ECS via the backend API
    2. Forwards tool calls to the remote sandbox
    3. Proxies LLM requests through the backend (no API key needed)
    """

    def __init__(self, api_url: str = API_BASE_URL) -> None:
        self.api_url = api_url.rstrip("/")
        self.auth_token = get_auth_token()
        self.client = httpx.AsyncClient(
            base_url=self.api_url,
            headers=self._get_headers(),
            timeout=60.0,
        )
        self.sandbox_id: str | None = None
        self.tool_server_url: str | None = None

    def _get_headers(self) -> dict[str, str]:
        """Get request headers with auth token."""
        headers = {"Content-Type": "application/json"}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers

    async def check_quota(self) -> dict[str, Any]:
        """Check if user has remaining quota."""
        response = await self.client.get("/api/v1/user/quota")
        response.raise_for_status()
        return response.json()

    async def create_sandbox(
        self,
        scan_id: str,
        target: str,
        target_type: str = "url",
        scan_type: str = "deep",
    ) -> SandboxInfo:
        """
        Create a new sandbox on the remote service.

        Args:
            scan_id: Unique identifier for this scan
            target: Target URL or repository
            target_type: "url" or "repository"
            scan_type: "deep", "quick", or "compliance"

        Returns:
            SandboxInfo with connection details
        """
        response = await self.client.post(
            "/api/v1/sandbox",
            json={
                "scan_id": scan_id,
                "target": target,
                "target_type": target_type,
                "scan_type": scan_type,
            },
        )
        response.raise_for_status()
        data = response.json()

        self.sandbox_id = data["sandbox_id"]

        return SandboxInfo(
            sandbox_id=data["sandbox_id"],
            status=data["status"],
            tool_server_url=data.get("tool_server_url"),
            public_ip=None,
        )

    async def wait_for_sandbox_ready(
        self,
        sandbox_id: str,
        timeout: int = 300,
        poll_interval: int = 5,
    ) -> SandboxInfo:
        """
        Wait for sandbox to be ready and return connection info.

        Args:
            sandbox_id: ID of the sandbox to wait for
            timeout: Maximum time to wait in seconds
            poll_interval: Time between status checks

        Returns:
            SandboxInfo with tool_server_url when ready
        """
        elapsed = 0
        while elapsed < timeout:
            response = await self.client.get(f"/api/v1/sandbox/{sandbox_id}")
            response.raise_for_status()
            data = response.json()

            if data["status"] == "running" and data.get("tool_server_url"):
                self.tool_server_url = data["tool_server_url"]
                return SandboxInfo(
                    sandbox_id=sandbox_id,
                    status="running",
                    tool_server_url=data["tool_server_url"],
                    public_ip=data.get("public_ip"),
                )

            if data["status"] == "failed":
                raise RuntimeError(f"Sandbox failed to start: {sandbox_id}")

            await asyncio.sleep(poll_interval)
            elapsed += poll_interval

        raise TimeoutError(f"Sandbox {sandbox_id} did not become ready within {timeout}s")

    async def destroy_sandbox(self, sandbox_id: str | None = None) -> bool:
        """
        Stop and clean up a sandbox.

        Args:
            sandbox_id: ID of sandbox to destroy. Uses current if not provided.

        Returns:
            True if successfully destroyed
        """
        sandbox_id = sandbox_id or self.sandbox_id
        if not sandbox_id:
            return False

        try:
            response = await self.client.delete(f"/api/v1/sandbox/{sandbox_id}")
            response.raise_for_status()
            self.sandbox_id = None
            self.tool_server_url = None
            return True
        except httpx.HTTPError:
            return False

    async def execute_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Execute a tool on the remote sandbox.

        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments

        Returns:
            Tool execution result
        """
        if not self.tool_server_url:
            raise RuntimeError("No sandbox connected. Create a sandbox first.")

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.tool_server_url}/execute",
                json={
                    "tool": tool_name,
                    "arguments": arguments,
                },
            )
            response.raise_for_status()
            return response.json()

    async def generate_llm_response(
        self,
        messages: list[dict],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        scan_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Generate LLM response through the backend proxy.

        Users don't need their own API keys - the backend provides the LLM.

        Args:
            messages: Chat messages
            model: Optional model override
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            scan_id: Optional scan ID for usage tracking

        Returns:
            LLM response with content and token usage
        """
        response = await self.client.post(
            "/api/v1/llm/generate",
            json={
                "messages": messages,
                "model": model,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "scan_id": scan_id,
            },
        )
        response.raise_for_status()
        return response.json()

    async def get_usage(self) -> dict[str, Any]:
        """Get current usage stats."""
        response = await self.client.get("/api/v1/user/usage")
        response.raise_for_status()
        return response.json()

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()


def get_runtime() -> RemoteRuntime | None:
    """
    Get the appropriate runtime based on authentication status.

    Returns:
        RemoteRuntime if authenticated, None otherwise
    """
    if is_authenticated():
        return RemoteRuntime()
    return None
