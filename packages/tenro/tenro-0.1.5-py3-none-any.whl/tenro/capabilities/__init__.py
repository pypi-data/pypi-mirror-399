# Copyright 2025 Tenro.ai
# SPDX-License-Identifier: Apache-2.0

"""Agent capability tracking and coverage visualization.

This module provides:
- Declared capability registry (what agents are configured to access)
- Executed capability tracking (what actually ran during tests)
- Coverage calculation (declared vs executed comparison)
- Security smell detection (undeclared capabilities)
- Console rendering and JSON export

Capability categories:
- Declared: Static capabilities from @link_tool, declare_tool(), declare_mcp_server()
- Presented: Tools sent to the LLM in request body
- Executed: Tools actually invoked (from ToolCall spans)
"""

from __future__ import annotations

from tenro.capabilities.types import (
    AgentCoverageMetrics,
    CapabilityReport,
    DeclaredHost,
    DeclaredSource,
    DeclaredTool,
    ExecutedTool,
    HostClassifier,
    HostKind,
    MCPServer,
    ObservabilityScope,
    ObservedHost,
    PresentedTool,
    ResolutionError,
    SecuritySmells,
    compute_schema_hash,
)

__all__ = [
    # Types
    "AgentCoverageMetrics",
    "DeclaredHost",
    "DeclaredSource",
    "DeclaredTool",
    "ExecutedTool",
    "HostClassifier",
    "HostKind",
    "MCPServer",
    "ObservabilityScope",
    "ObservedHost",
    "PresentedTool",
    "ResolutionError",
    "SecuritySmells",
    "CapabilityReport",
    # Functions
    "compute_schema_hash",
]
