# Copyright 2025 Tenro.ai
# SPDX-License-Identifier: Apache-2.0

"""Executed capability collector (runtime).

Collects executed tools from ToolCall spans and observed hosts from HTTP
requests during test execution.
"""

from __future__ import annotations

from tenro.capabilities.types import ExecutedTool, HostKind, ObservedHost, ResolutionError


class ExecutedCollector:
    """Collects executed capabilities during test runs.

    Aggregates tool executions and host accesses from spans and HTTP
    interception, tracking invocation counts and scenario attribution.

    Attributes:
        _tools: Internal map of executed tools keyed by identifier and agent.
        _hosts: Internal map of observed hosts keyed by hostname.
        _scenario_totals: Scenario path counts across executions.
    """

    def __init__(self) -> None:
        """Initialize empty collector."""
        self._tools: dict[tuple[str, str | None], ExecutedTool] = {}
        self._hosts: dict[str, ObservedHost] = {}
        self._scenario_totals: dict[str, int] = {}

    def record_tool_execution(
        self,
        name: str,
        *,
        canonical_id: str | None = None,
        agent_name: str | None = None,
        scenario_path: list[str] | None = None,
        resolution_error: ResolutionError = None,
    ) -> None:
        """Record a tool execution from a ToolCall span.

        Args:
            name: Tool name from span.
            canonical_id: Resolved canonical ID if matched to declared tool.
            agent_name: Name of agent that executed the tool.
            scenario_path: Current scenario path for attribution.
            resolution_error: Resolution status if tool could not be resolved.
        """
        key = (canonical_id or name, agent_name)

        if key not in self._tools:
            self._tools[key] = ExecutedTool(
                name=name,
                canonical_id=canonical_id,
                agent_name=agent_name,
                resolution_error=resolution_error,
            )

        tool = self._tools[key]
        tool.invocation_count += 1

        # Track scenario attribution
        if scenario_path:
            scenario_key = "/".join(scenario_path)
            tool.scenario_counts[scenario_key] = tool.scenario_counts.get(scenario_key, 0) + 1
            self._scenario_totals[scenario_key] = self._scenario_totals.get(scenario_key, 0) + 1

    def record_host_access(
        self,
        host: str,
        *,
        kind: HostKind = "unknown",
        agent_name: str | None = None,
        scenario_path: list[str] | None = None,
    ) -> None:
        """Record an HTTP host access.

        Args:
            host: Hostname accessed.
            kind: Classification (llm_provider, external_api, unknown).
            agent_name: Name of agent that made the request.
            scenario_path: Current scenario path for attribution.
        """
        if host not in self._hosts:
            self._hosts[host] = ObservedHost(
                host=host,
                kind=kind,
                agent_name=agent_name,
            )

        observed = self._hosts[host]
        if agent_name and observed.agent_name not in (None, agent_name):
            observed.agent_name = None
        observed.request_count += 1

        # Track scenario attribution
        if scenario_path:
            scenario_key = "/".join(scenario_path)
            observed.scenario_counts[scenario_key] = (
                observed.scenario_counts.get(scenario_key, 0) + 1
            )

    def get_executed_tools(self) -> list[ExecutedTool]:
        """Get all executed tools.

        Returns:
            List of executed tools with invocation counts.
        """
        return list(self._tools.values())

    def get_observed_hosts(self) -> list[ObservedHost]:
        """Get all observed hosts.

        Returns:
            List of observed hosts with request counts.
        """
        return list(self._hosts.values())

    def get_scenario_summary(self) -> dict[str, int]:
        """Get summary of scenario usage.

        Returns:
            Dict mapping scenario path to total invocation count.
        """
        return dict(self._scenario_totals)

    def reset(self) -> None:
        """Clear all collected data."""
        self._tools.clear()
        self._hosts.clear()
        self._scenario_totals.clear()
