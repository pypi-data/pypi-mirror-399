# Copyright 2025 Tenro.ai
# SPDX-License-Identifier: Apache-2.0

"""Helpers for building and merging capability reports."""

from __future__ import annotations

from tenro.capabilities.coverage import CoverageCalculator
from tenro.capabilities.types import (
    CapabilityReport,
    DeclaredHost,
    DeclaredTool,
    ExecutedTool,
    ObservabilityScope,
    ObservedHost,
)


def build_report(
    *,
    observability: ObservabilityScope,
    declared_tools: list[DeclaredTool],
    executed_tools: list[ExecutedTool],
    declared_hosts: list[DeclaredHost],
    observed_hosts: list[ObservedHost],
) -> CapabilityReport:
    """Build a CapabilityReport with computed coverage metrics."""
    calc = CoverageCalculator(
        declared_tools=declared_tools,
        executed_tools=executed_tools,
        declared_hosts=declared_hosts,
        observed_hosts=observed_hosts,
    )

    return CapabilityReport(
        observability=observability,
        declared_tools=declared_tools,
        executed_tools=executed_tools,
        declared_hosts=declared_hosts,
        observed_hosts=observed_hosts,
        agents=calc.get_agent_coverage_metrics(),
        security=calc.build_security_smells(),
    )


def merge_reports(reports: list[CapabilityReport]) -> CapabilityReport:
    """Merge multiple capability reports into one."""
    if not reports:
        return CapabilityReport(observability=ObservabilityScope())

    declared_tools = _merge_declared_tools(reports)
    executed_tools = _merge_executed_tools(reports)
    declared_hosts = _merge_declared_hosts(reports)
    observed_hosts = _merge_observed_hosts(reports)
    observability = _merge_observability(reports)

    return build_report(
        observability=observability,
        declared_tools=declared_tools,
        executed_tools=executed_tools,
        declared_hosts=declared_hosts,
        observed_hosts=observed_hosts,
    )


def _merge_declared_tools(reports: list[CapabilityReport]) -> list[DeclaredTool]:
    """Merge declared tools by canonical ID and agent."""
    merged: dict[tuple[str, str | None], DeclaredTool] = {}
    for report in reports:
        for tool in report.declared_tools:
            merged[(tool.canonical_id, tool.agent_name)] = tool
    return list(merged.values())


def _merge_executed_tools(reports: list[CapabilityReport]) -> list[ExecutedTool]:
    """Merge executed tools, summing invocation counts."""
    merged: dict[tuple[str, str | None], ExecutedTool] = {}
    for report in reports:
        for tool in report.executed_tools:
            key = (tool.canonical_id or tool.name, tool.agent_name)
            if key not in merged:
                merged[key] = tool.model_copy(deep=True)
                continue
            merged[key].invocation_count += tool.invocation_count
            for scenario, count in tool.scenario_counts.items():
                merged[key].scenario_counts[scenario] = (
                    merged[key].scenario_counts.get(scenario, 0) + count
                )
    return list(merged.values())


def _merge_declared_hosts(reports: list[CapabilityReport]) -> list[DeclaredHost]:
    """Merge declared hosts by host and agent."""
    merged: dict[tuple[str, str | None], DeclaredHost] = {}
    for report in reports:
        for host in report.declared_hosts:
            merged[(host.host, host.agent_name)] = host
    return list(merged.values())


def _merge_observed_hosts(reports: list[CapabilityReport]) -> list[ObservedHost]:
    """Merge observed hosts by hostname."""
    merged: dict[str, ObservedHost] = {}
    for report in reports:
        for host in report.observed_hosts:
            if host.host not in merged:
                merged[host.host] = host.model_copy(deep=True)
                continue
            merged[host.host].request_count += host.request_count
            for scenario, count in host.scenario_counts.items():
                merged[host.host].scenario_counts[scenario] = (
                    merged[host.host].scenario_counts.get(scenario, 0) + count
                )
    return list(merged.values())


def _merge_observability(reports: list[CapabilityReport]) -> ObservabilityScope:
    """Merge observability sources and warnings."""
    sources: set[str] = set()
    warnings: list[str] = []
    for report in reports:
        sources.update(report.observability.sources)
        for warning in report.observability.warnings:
            if warning not in warnings:
                warnings.append(warning)
    return ObservabilityScope(sources=sorted(sources), warnings=warnings)


__all__ = ["build_report", "merge_reports"]
