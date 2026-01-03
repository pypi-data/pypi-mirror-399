# Copyright 2025 Tenro.ai
# SPDX-License-Identifier: Apache-2.0

"""Console rendering for capability reports.

Follows patterns from debug/renderer.py for consistent console output.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import TypeVar

from tenro.capabilities.coverage import CoverageCalculator
from tenro.capabilities.types import CapabilityReport, DeclaredTool, ObservedHost
from tenro.debug.icons import BRANCH, LAST

# Icons for capability status
CHECK = "[green]✓[/green]"
CROSS = "[red]✗[/red]"
WARNING = "[yellow]⚠[/yellow]"

T = TypeVar("T")


def _with_connectors(items: list[T]) -> Iterator[tuple[str, T]]:
    """Yield (connector, item) pairs with LAST for final item."""
    for i, item in enumerate(items):
        yield (LAST if i == len(items) - 1 else BRANCH, item)


class CapabilityRenderer:
    """Renders capability reports to console.

    Produces tree-view output showing declared vs executed tools,
    coverage percentages, and security warnings.
    """

    def render(self, report: CapabilityReport) -> None:
        """Render report to console.

        Args:
            report: CapabilityReport to render.
        """
        from rich.console import Console

        console = Console()
        output = self.render_to_string(report)
        console.print(output)

    def render_to_string(self, report: CapabilityReport) -> str:
        """Render report to string for testing.

        Args:
            report: CapabilityReport to render.

        Returns:
            Formatted string output.
        """
        lines: list[str] = []

        # Header
        lines.extend(self._build_header(report))

        # Coverage mode indicator
        calc = CoverageCalculator(
            declared_tools=report.declared_tools,
            declared_hosts=report.declared_hosts,
        )
        if calc.get_coverage_mode() == "observed-only":
            lines.append("Coverage mode: [yellow]observed-only[/yellow] (no declared baseline)")
            lines.append("")

        # Per-agent section
        if report.agents:
            lines.extend(self._build_agent_section(report))

        # Global tools section
        global_tools = [t for t in report.declared_tools if t.agent_name is None]
        if global_tools:
            lines.extend(self._build_global_tools_section(report, global_tools))

        # Observed tools (when no declarations)
        if not report.declared_tools and report.executed_tools:
            lines.extend(self._build_observed_tools_section(report))

        # Observed hosts
        if report.observed_hosts:
            llm_hosts = [host for host in report.observed_hosts if host.kind == "llm_provider"]
            external_hosts = [host for host in report.observed_hosts if host.kind != "llm_provider"]
            if llm_hosts:
                lines.extend(self._build_llm_hosts_section(llm_hosts))
            if external_hosts:
                lines.extend(self._build_hosts_section(report, external_hosts))

        # Security warnings
        if report.security.has_undeclared():
            lines.extend(self._build_security_section(report))

        # Summary footer
        lines.extend(self._build_footer(report))

        return "\n".join(lines)

    def _build_header(self, report: CapabilityReport) -> list[str]:
        """Build header section."""
        lines: list[str] = []
        lines.append("")
        lines.append("[bold]Agent Attack Surface Report[/bold]")
        lines.append("[dim]" + "─" * 64 + "[/dim]")

        if report.observability.sources:
            sources = ", ".join(report.observability.sources)
            lines.append(f"[dim]Observed via: {sources}[/dim]")

        if report.observability.warnings:
            for warning in report.observability.warnings:
                lines.append(f"[yellow]{WARNING} {warning}[/yellow]")

        lines.append("")
        return lines

    def _build_agent_section(self, report: CapabilityReport) -> list[str]:
        """Build per-agent coverage section."""
        lines: list[str] = []
        lines.append("[bold]Per-Agent Tools[/bold]")
        lines.append("[dim]───────────────[/dim]")

        for agent_metric in report.agents:
            coverage = agent_metric.attack_surface_coverage_pct
            lines.append(f"{agent_metric.agent_name} ([cyan]{coverage:.0f}%[/cyan] coverage)")

            # Get tools for this agent
            agent_declared = {
                t.canonical_id: t
                for t in report.declared_tools
                if t.agent_name == agent_metric.agent_name
            }
            agent_executed = {
                t.canonical_id: t
                for t in report.executed_tools
                if t.canonical_id and t.agent_name == agent_metric.agent_name
            }

            tool_items = list(agent_declared.items())
            for connector, (canonical_id, tool) in _with_connectors(tool_items):
                if canonical_id in agent_executed:
                    count = agent_executed[canonical_id].invocation_count
                    lines.append(f"{connector} [{CHECK}] {tool.name} (called {count}x)")
                else:
                    lines.append(f"{connector} [{CROSS}] {tool.name} (declared, never called)")

            lines.append("")

        return lines

    def _build_global_tools_section(
        self, report: CapabilityReport, global_tools: list[DeclaredTool]
    ) -> list[str]:
        """Build global tools section."""
        lines: list[str] = []
        lines.append("[bold]Global Tools[/bold] (shared across agents)")
        lines.append("[dim]─────────────────────────────────────[/dim]")

        executed_map = {t.canonical_id: t for t in report.executed_tools if t.canonical_id}

        for connector, tool in _with_connectors(global_tools):
            if tool.canonical_id in executed_map:
                count = executed_map[tool.canonical_id].invocation_count
                lines.append(f"{connector} [{CHECK}] {tool.name} (called {count}x)")
            else:
                lines.append(f"{connector} [{CROSS}] {tool.name} (declared, never called)")

        lines.append("")
        return lines

    def _build_observed_tools_section(self, report: CapabilityReport) -> list[str]:
        """Build observed tools section (for observed-only mode)."""
        lines: list[str] = []
        lines.append("[bold]Observed Tools[/bold]")
        lines.append("[dim]──────────────[/dim]")

        for connector, tool in _with_connectors(report.executed_tools):
            lines.append(f"{connector} {tool.name} (called {tool.invocation_count}x)")

        lines.append("")
        return lines

    def _build_hosts_section(
        self, report: CapabilityReport, observed_hosts: list[ObservedHost]
    ) -> list[str]:
        """Build hosts section."""
        lines: list[str] = []
        lines.append("[bold]External Data Sources[/bold]")
        lines.append("[dim]─────────────────────[/dim]")

        declared_hosts = {h.host for h in report.declared_hosts}

        for connector, host in _with_connectors(observed_hosts):
            if host.host in declared_hosts:
                lines.append(f"{connector} [{CHECK}] {host.host} ({host.request_count} requests)")
            else:
                lines.append(f"{connector} [{WARNING}] {host.host} (undeclared)")

        lines.append("")
        return lines

    def _build_llm_hosts_section(self, llm_hosts: list[ObservedHost]) -> list[str]:
        """Build LLM provider hosts section."""
        lines: list[str] = []
        lines.append("[bold]LLM Providers[/bold]")
        lines.append("[dim]─────────────[/dim]")

        for connector, host in _with_connectors(llm_hosts):
            lines.append(f"{connector} {host.host} ({host.request_count} requests)")

        lines.append("")
        return lines

    def _build_security_section(self, report: CapabilityReport) -> list[str]:
        """Build security warnings section."""
        lines: list[str] = []
        lines.append("[bold red]Security Warnings[/bold red]")
        lines.append("[dim]─────────────────[/dim]")

        if report.security.executed_not_declared:
            lines.append(f"{WARNING} [red]UNDECLARED TOOLS DETECTED[/red]")
            for tool in report.security.executed_not_declared:
                lines.append(f"   • {tool}")

        if report.security.undeclared_hosts:
            lines.append(f"{WARNING} [red]UNDECLARED HOSTS ACCESSED[/red]")
            for host in report.security.undeclared_hosts:
                lines.append(f"   • {host}")

        lines.append("")
        return lines

    def _build_footer(self, report: CapabilityReport) -> list[str]:
        """Build footer with summary."""
        lines: list[str] = []
        lines.append("[dim]" + "─" * 64 + "[/dim]")

        parts: list[str] = []

        if report.agents:
            parts.append(f"{len(report.agents)} agents")

        total_declared = len(report.declared_tools)
        total_executed = len(report.executed_tools)

        if total_declared > 0:
            tested = len({t.canonical_id for t in report.executed_tools if t.canonical_id})
            coverage = (tested / total_declared) * 100 if total_declared else 0
            parts.append(f"{tested}/{total_declared} tools ({coverage:.0f}%)")
        elif total_executed > 0:
            parts.append(f"{total_executed} tools observed")

        if report.security.has_undeclared():
            smells = len(report.security.executed_not_declared) + len(
                report.security.undeclared_hosts
            )
            parts.append(f"[red]{smells} security warnings[/red]")

        if parts:
            lines.append(f"[dim]Summary: {' | '.join(parts)}[/dim]")

        lines.append("")
        return lines
