# Copyright 2025 Tenro.ai
# SPDX-License-Identifier: Apache-2.0

"""Coverage calculation for declared vs executed comparison.

Computes attack surface coverage (Declared ∖ Executed) and security smells
(Executed ∖ Declared, Hosts ∖ Declared).
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from tenro.capabilities.types import (
    AgentCoverageMetrics,
    DeclaredHost,
    DeclaredTool,
    ExecutedTool,
    ObservedHost,
    SecuritySmells,
)
from tenro.core.model_base import BaseModel

CoverageMode = Literal["strict", "observed-only"]


class GlobalToolsSummary(BaseModel):
    """Summary of global tools (agent_name=None).

    Attributes:
        declared: Declared global tools.
        executed: Executed global tools.
    """

    declared: list[DeclaredTool] = Field(default_factory=list)
    """Declared global tools."""

    executed: list[ExecutedTool] = Field(default_factory=list)
    """Executed global tools."""


class CoverageCalculator:
    """Calculate coverage metrics from declared vs executed capabilities.

    Implements the declared vs executed comparison model:
    - Attack surface coverage = Declared ∖ Executed (untested tools)
    - Security smells = Executed ∖ Declared (undeclared tools)

    Attributes:
        _declared_tools: Declared tools used for calculations.
        _executed_tools: Executed tools used for calculations.
        _declared_hosts: Declared hosts used for calculations.
        _observed_hosts: Observed hosts used for calculations.
    """

    def __init__(
        self,
        *,
        declared_tools: list[DeclaredTool] | None = None,
        executed_tools: list[ExecutedTool] | None = None,
        declared_hosts: list[DeclaredHost] | None = None,
        observed_hosts: list[ObservedHost] | None = None,
    ) -> None:
        """Initialize calculator with capability data.

        Args:
            declared_tools: Tools declared via @link_tool, declare_tool(), etc.
            executed_tools: Tools actually executed during tests.
            declared_hosts: Hosts explicitly allowed.
            observed_hosts: Hosts accessed during tests.
        """
        self._declared_tools = declared_tools or []
        self._executed_tools = executed_tools or []
        self._declared_hosts = declared_hosts or []
        self._observed_hosts = observed_hosts or []

        # Build lookup sets
        self._declared_keys = {
            _tool_key(t.canonical_id, t.agent_name) for t in self._declared_tools
        }
        self._executed_keys = {
            _tool_key(t.canonical_id, t.agent_name) for t in self._executed_tools if t.canonical_id
        }
        self._declared_host_set = {h.host for h in self._declared_hosts}

    def calculate_attack_surface_coverage(self) -> float:
        """Calculate overall attack surface coverage percentage.

        Returns:
            Percentage of declared tools that were executed (0-100).
        """
        if not self._declared_keys:
            return 0.0

        tested_count = len(self._declared_keys & self._executed_keys)
        return (tested_count / len(self._declared_keys)) * 100

    def get_untested_tools(self) -> list[DeclaredTool]:
        """Get declared tools that were never executed.

        Returns:
            List of declared tools not in executed set.
        """
        return [t for t in self._declared_tools if _declared_key(t) not in self._executed_keys]

    def get_undeclared_tools(self) -> list[ExecutedTool]:
        """Get executed tools that were not declared (security smell).

        Returns:
            List of executed tools without matching declaration.
        """
        undeclared: list[ExecutedTool] = []
        for tool in self._executed_tools:
            if tool.canonical_id is None:
                if tool.resolution_error == "ambiguous":
                    continue
                undeclared.append(tool)
                continue
            if _tool_key(tool.canonical_id, tool.agent_name) not in self._declared_keys:
                undeclared.append(tool)
        return undeclared

    def get_undeclared_hosts(self) -> list[ObservedHost]:
        """Get observed hosts that were not declared.

        Returns:
            List of hosts accessed but not in declared allowlist.
        """
        return [
            h
            for h in self._observed_hosts
            if h.kind != "llm_provider" and h.host not in self._declared_host_set
        ]

    def get_agent_coverage_metrics(self) -> list[AgentCoverageMetrics]:
        """Calculate coverage metrics per agent.

        Returns:
            List of metrics for each agent that has declared tools.
        """
        # Group declared tools by agent
        agent_declared: dict[str, list[DeclaredTool]] = {}
        for decl_tool in self._declared_tools:
            if decl_tool.agent_name:
                agent_declared.setdefault(decl_tool.agent_name, []).append(decl_tool)

        # Group executed tools by agent
        agent_executed: dict[str, list[ExecutedTool]] = {}
        for exec_tool in self._executed_tools:
            if exec_tool.agent_name:
                agent_executed.setdefault(exec_tool.agent_name, []).append(exec_tool)

        # Calculate metrics
        metrics: list[AgentCoverageMetrics] = []
        all_agents = set(agent_declared.keys()) | set(agent_executed.keys())

        for agent in sorted(all_agents):
            declared = agent_declared.get(agent, [])
            executed = agent_executed.get(agent, [])

            declared_ids = {t.canonical_id for t in declared}
            executed_ids = {t.canonical_id for t in executed if t.canonical_id}
            tested_ids = declared_ids & executed_ids

            coverage_pct = (len(tested_ids) / len(declared)) * 100 if declared else 0.0
            untested = [t.canonical_id for t in declared if t.canonical_id not in tested_ids]

            metrics.append(
                AgentCoverageMetrics(
                    agent_name=agent,
                    declared_count=len(declared),
                    executed_count=len(tested_ids),
                    attack_surface_coverage_pct=coverage_pct,
                    untested_tools=untested,
                )
            )

        return metrics

    def get_global_tools(self) -> GlobalToolsSummary:
        """Get summary of global tools (agent_name=None).

        Returns:
            Summary of declared and executed global tools.
        """
        global_declared = [t for t in self._declared_tools if t.agent_name is None]
        global_executed = [t for t in self._executed_tools if t.agent_name is None]

        return GlobalToolsSummary(
            declared=global_declared,
            executed=global_executed,
        )

    def get_coverage_mode(self) -> CoverageMode:
        """Determine coverage mode based on declarations.

        Returns:
            'strict' if declarations exist, 'observed-only' otherwise.
        """
        if self._declared_tools or self._declared_hosts:
            return "strict"
        return "observed-only"

    def build_security_smells(self) -> SecuritySmells:
        """Build security smell report from set comparisons.

        Returns:
            SecuritySmells with undeclared tools and hosts.
        """
        undeclared_tools = self.get_undeclared_tools()
        undeclared_hosts = self.get_undeclared_hosts()

        return SecuritySmells(
            executed_not_declared=[t.name for t in undeclared_tools],
            undeclared_hosts=[h.host for h in undeclared_hosts],
        )


def _tool_key(canonical_id: str, agent_name: str | None) -> tuple[str, str | None]:
    """Build a unique key for a tool within an agent context."""
    return (canonical_id, agent_name)


def _declared_key(tool: DeclaredTool) -> tuple[str, str | None]:
    """Build a key for declared tool comparisons."""
    return _tool_key(tool.canonical_id, tool.agent_name)
