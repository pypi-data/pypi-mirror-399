# Copyright 2025 Tenro.ai
# SPDX-License-Identifier: Apache-2.0

"""Data models for capability tracking.

Declared: Static developer whitelist
Presented: Runtime tools sent to the LLM in a request
Executed: Runtime tools actually invoked
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, ClassVar, Literal

from pydantic import Field

from tenro.core.model_base import BaseModel

# =============================================================================
# Helper Functions
# =============================================================================


def compute_schema_hash(schema: dict[str, Any]) -> str:
    """Compute SHA256 hash of JSON schema for change detection.

    Args:
        schema: JSON Schema dict to hash.

    Returns:
        Hash string prefixed with 'sha256:'.
    """
    # Sort keys for deterministic output
    json_str = json.dumps(schema, sort_keys=True, separators=(",", ":"))
    hash_bytes = hashlib.sha256(json_str.encode()).hexdigest()[:16]
    return f"sha256:{hash_bytes}"


# =============================================================================
# Declared (Static - developer whitelist)
# =============================================================================

DeclaredSource = Literal["decorator", "mcp", "manual"]


class DeclaredTool(BaseModel):
    """A tool explicitly whitelisted by the developer.

    Canonical ID formats:
    - py://module:function - For @link_tool decorated functions
    - mcp://server/tool - For MCP server tools
    - manual://name - For declare_tool() without source

    Attributes:
        canonical_id: Unique identifier for the declared tool.
        name: Display name shown in reports.
        aliases: Alternative names for matching presented tools.
        agent_name: Agent this tool belongs to. None means global tool.
        description: Human-readable description.
        source: How tool was declared.
        module_path: Python module path for decorator-linked tools.
        input_schema: JSON Schema for input parameters.
        schema_hash: Hash of the input schema for change detection.
        schema_errors: Errors encountered during schema extraction.
    """

    canonical_id: str
    """Unique identifier: py://module:func, mcp://server/tool, manual://name."""

    name: str
    """Display name shown in reports."""

    aliases: list[str] = Field(default_factory=list)
    """Alternative names for matching presented tools."""

    agent_name: str | None = None
    """Agent this tool belongs to. None = global tool."""

    description: str | None = None
    """Human-readable description."""

    source: DeclaredSource = "manual"
    """How tool was declared: decorator, mcp, or manual."""

    module_path: str | None = None
    """Python module path for decorator-linked tools."""

    input_schema: dict[str, Any] | None = None
    """JSON Schema for input parameters."""

    schema_hash: str | None = None
    """SHA256 of sorted JSON schema for change detection."""

    schema_errors: list[str] | None = None
    """Errors encountered during schema extraction."""


class DeclaredHost(BaseModel):
    """A host explicitly allowed by the developer.

    Attributes:
        host: Hostname (e.g., "api.example.com").
        agent_name: Agent expected to access this host.
    """

    host: str
    """Hostname (e.g., 'api.example.com')."""

    agent_name: str | None = None
    """Agent expected to access this host."""


class MCPServer(BaseModel):
    """An MCP server providing tools.

    Attributes:
        name: MCP server name.
        transport: MCP transport type.
        tools: Tools provided by this server.
    """

    name: str
    """MCP server name."""

    transport: Literal["stdio", "http", "sse"] = "stdio"
    """MCP transport type."""

    tools: list[DeclaredTool] = Field(default_factory=list)
    """Tools provided by this server."""


# =============================================================================
# Presented (Runtime - sent to the LLM in request)
# =============================================================================

ResolutionError = Literal["ambiguous", "not_found"] | None


class PresentedTool(BaseModel):
    """A tool advertised to the LLM in a request.

    Attributes:
        name: Name as sent to the LLM.
        canonical_id: Resolved from declared tools, if matched.
        resolution_error: Resolution status if tool could not be resolved.
        input_schema: Schema as sent to the LLM.
        schema_hash: Hash for schema comparison.
        provider: LLM provider name.
        scenario_counts: Invocation count per scenario.
    """

    name: str
    """Name as sent to LLM."""

    canonical_id: str | None = None
    """Resolved from declared, if matched."""

    resolution_error: ResolutionError = None
    """'ambiguous' if multiple matches, 'not_found' if no match."""

    input_schema: dict[str, Any] | None = None
    """Schema as sent to LLM."""

    schema_hash: str | None = None
    """Hash for comparison."""

    provider: str = ""
    """LLM provider (openai, anthropic, etc.)."""

    scenario_counts: dict[str, int] = Field(default_factory=dict)
    """Invocation count per scenario."""


# =============================================================================
# Executed (Runtime - actually invoked)
# =============================================================================


class ExecutedTool(BaseModel):
    """A tool actually executed.

    Attributes:
        name: Name from the execution span.
        canonical_id: Resolved from declared tools, if matched.
        resolution_error: Resolution status if tool could not be resolved.
        agent_name: Agent that executed this tool.
        invocation_count: Number of times executed.
        scenario_counts: Invocation count per scenario.
    """

    name: str
    """Name from span."""

    canonical_id: str | None = None
    """Resolved from declared, if matched."""

    resolution_error: ResolutionError = None
    """'ambiguous' if multiple matches."""

    agent_name: str | None = None
    """Agent that executed this tool."""

    invocation_count: int = 0
    """Number of times executed."""

    scenario_counts: dict[str, int] = Field(default_factory=dict)
    """Invocation count per scenario."""


HostKind = Literal["llm_provider", "external_api", "unknown"]


class ObservedHost(BaseModel):
    """An HTTP host observed during runtime.

    Attributes:
        host: Hostname.
        kind: Classification for the host.
        agent_name: Agent that accessed this host.
        request_count: Number of requests made.
        scenario_counts: Request count per scenario.
    """

    host: str
    """Hostname."""

    kind: HostKind = "unknown"
    """Classification: llm_provider, external_api, or unknown."""

    agent_name: str | None = None
    """Agent that accessed this host."""

    request_count: int = 0
    """Number of requests made."""

    scenario_counts: dict[str, int] = Field(default_factory=dict)
    """Request count per scenario."""


class HostClassifier:
    """Classify hosts as LLM provider vs external API vs unknown.

    Attributes:
        DEFAULT_LLM_PATTERNS: Default patterns for LLM provider hosts.
        _llm_patterns: Effective patterns for LLM provider hosts.
        _external_patterns: Patterns for known external APIs.
    """

    DEFAULT_LLM_PATTERNS: ClassVar[list[str]] = [
        "api.openai.com",
        "*.openai.azure.com",
        "api.anthropic.com",
        "generativelanguage.googleapis.com",
        "api.groq.com",
        "api.together.xyz",
        "openrouter.ai",
    ]

    def __init__(
        self,
        llm_patterns: list[str] | None = None,
        external_patterns: list[str] | None = None,
    ) -> None:
        """Initialize classifier with patterns.

        Args:
            llm_patterns: Patterns for LLM provider hosts. None = use defaults.
            external_patterns: Patterns for known external APIs.
        """
        self._llm_patterns = llm_patterns if llm_patterns is not None else self.DEFAULT_LLM_PATTERNS
        self._external_patterns = external_patterns or []

    def classify(self, host: str) -> HostKind:
        """Classify host. Returns 'unknown' if no pattern matches.

        Args:
            host: Hostname to classify.

        Returns:
            HostKind: 'llm_provider', 'external_api', or 'unknown'.
        """
        if self._matches_any(host, self._llm_patterns):
            return "llm_provider"
        if self._matches_any(host, self._external_patterns):
            return "external_api"
        return "unknown"

    def _matches_any(self, host: str, patterns: list[str]) -> bool:
        """Check if host matches any pattern."""
        for pattern in patterns:
            if pattern.startswith("*."):
                # Wildcard suffix match
                if host.endswith(pattern[1:]):
                    return True
            elif host == pattern:
                return True
        return False


# =============================================================================
# COVERAGE & SECURITY METRICS (Declared vs Executed)
# =============================================================================


class AgentCoverageMetrics(BaseModel):
    """Coverage metrics for a single agent.

    Attributes:
        agent_name: Agent identifier.
        declared_count: Number of declared tools.
        presented_count: Number of presented tools.
        executed_count: Number of executed tools.
        attack_surface_coverage_pct: Percentage of declared tools executed.
        untested_tools: Canonical IDs of declared but not executed tools.
    """

    agent_name: str
    """Agent identifier."""

    declared_count: int = 0
    """Number of declared tools."""

    presented_count: int = 0
    """Number of presented tools."""

    executed_count: int = 0
    """Number of executed tools."""

    attack_surface_coverage_pct: float = 0.0
    """Percentage of declared tools that were executed."""

    untested_tools: list[str] = Field(default_factory=list)
    """Canonical IDs of declared but not executed tools."""


class SecuritySmells(BaseModel):
    """Security-relevant findings from declared vs executed comparison.

    Attributes:
        executed_not_declared: Tools executed but not declared.
        presented_not_declared: Tools sent to the LLM but not declared.
        undeclared_hosts: Hosts accessed but not declared.
        smell_agents: Mapping of agent names to smell descriptions.
    """

    executed_not_declared: list[str] = Field(default_factory=list)
    """Tools executed but not declared (security risk)."""

    presented_not_declared: list[str] = Field(default_factory=list)
    """Tools sent to LLM but not declared."""

    undeclared_hosts: list[str] = Field(default_factory=list)
    """Hosts accessed but not declared."""

    smell_agents: dict[str, list[str]] = Field(default_factory=dict)
    """Agent -> list of smell descriptions."""

    def has_undeclared(self) -> bool:
        """Check if any undeclared capabilities were detected.

        Returns:
            True if any security smell exists.
        """
        return bool(
            self.executed_not_declared or self.presented_not_declared or self.undeclared_hosts
        )


class ObservabilityScope(BaseModel):
    """What instrumentation sources contributed to this report.

    Attributes:
        sources: Instrumentation sources for the report.
        warnings: Observability gap warnings.
    """

    sources: list[str] = Field(default_factory=list)
    """Instrumentation sources (e.g., 'httpx/respx', 'spans')."""

    warnings: list[str] = Field(default_factory=list)
    """Observability gap warnings."""


class CapabilityReport(BaseModel):
    """Full capability coverage report.

    Attributes:
        observability: Observability scope and warnings.
        declared_tools: Declared tools.
        presented_tools: Tools presented to the LLM.
        executed_tools: Tools that executed during tests.
        declared_hosts: Declared hosts.
        observed_hosts: Observed hosts.
        agents: Per-agent coverage metrics.
        security: Security smell findings.
    """

    observability: ObservabilityScope = Field(default_factory=ObservabilityScope)
    """Observability scope and warnings."""

    declared_tools: list[DeclaredTool] = Field(default_factory=list)
    """Declared tools."""

    presented_tools: list[PresentedTool] = Field(default_factory=list)
    """Presented tools."""

    executed_tools: list[ExecutedTool] = Field(default_factory=list)
    """Executed tools."""

    declared_hosts: list[DeclaredHost] = Field(default_factory=list)
    """Declared hosts."""

    observed_hosts: list[ObservedHost] = Field(default_factory=list)
    """Observed hosts."""

    agents: list[AgentCoverageMetrics] = Field(default_factory=list)
    """Per-agent coverage metrics."""

    security: SecuritySmells = Field(default_factory=SecuritySmells)
    """Security smell findings."""
