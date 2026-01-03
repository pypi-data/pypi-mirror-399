# Copyright 2025 Tenro.ai
# SPDX-License-Identifier: Apache-2.0

"""Global declared registry for import-time tool registration.

This module provides a module-level singleton that stores declared capabilities.
Tools decorated with @link_tool register here at import time, before any
Construct is active.

Lifecycle notes:
- Per-process state: In pytest-xdist, each worker is a separate process
- Call clear() at pytest session start to avoid stale declarations
"""

from __future__ import annotations

from pydantic import Field

from tenro.capabilities.types import DeclaredHost, DeclaredTool, MCPServer
from tenro.core.model_base import BaseModel


class DeclaredCapabilities(BaseModel):
    """Immutable snapshot of declared capabilities."""

    tools: list[DeclaredTool] = Field(default_factory=list)
    """Declared tools."""

    mcp_servers: list[MCPServer] = Field(default_factory=list)
    """Declared MCP servers."""

    hosts: list[DeclaredHost] = Field(default_factory=list)
    """Declared hosts."""


class GlobalDeclaredRegistry:
    """Module-level singleton for import-time capability registration.

    This registry is populated at import time by @link_tool decorators.
    Construct takes a snapshot when activated, merging global declarations
    with any local declarations made via declare_tool().

    Thread-safety: Class-level dicts are modified during import, which is
    single-threaded in Python. Runtime access is read-only via snapshot().
    """

    _tools: dict[tuple[str, str | None], DeclaredTool] = {}
    _mcp_servers: dict[str, MCPServer] = {}
    _hosts: dict[str, DeclaredHost] = {}

    @classmethod
    def register_tool(cls, tool: DeclaredTool) -> None:
        """Register a declared tool.

        Args:
            tool: Tool to register. Keyed by canonical_id.
        """
        cls._tools[_tool_key(tool)] = tool

    @classmethod
    def register_mcp_server(cls, server: MCPServer) -> None:
        """Register an MCP server with its tools.

        Args:
            server: MCP server to register. Keyed by name.
        """
        cls._mcp_servers[server.name] = server
        for tool in server.tools:
            cls.register_tool(tool)

    @classmethod
    def register_host(cls, host: DeclaredHost) -> None:
        """Register a declared host.

        Args:
            host: Host to register. Keyed by host string.
        """
        cls._hosts[host.host] = host

    @classmethod
    def snapshot(cls) -> DeclaredCapabilities:
        """Return immutable copy of all declarations.

        Returns:
            DeclaredCapabilities with copies of all registered items.
        """
        return DeclaredCapabilities(
            tools=list(cls._tools.values()),
            mcp_servers=list(cls._mcp_servers.values()),
            hosts=list(cls._hosts.values()),
        )

    @classmethod
    def clear(cls) -> None:
        """Reset all declarations.

        Call at pytest session start to avoid stale declarations from
        previous test runs in the same process.
        """
        cls._tools.clear()
        cls._mcp_servers.clear()
        cls._hosts.clear()


def _tool_key(tool: DeclaredTool) -> tuple[str, str | None]:
    """Build unique key for declared tools."""
    return (tool.canonical_id, tool.agent_name)
