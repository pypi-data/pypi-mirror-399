# Copyright 2025 Tenro.ai
# SPDX-License-Identifier: Apache-2.0

"""Pytest plugin entry points for Tenro.

Auto-loads with pytest and stays dormant unless enabled via --tenro
or TENRO_ENABLED.
"""

from __future__ import annotations

import json
import os
import warnings
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from _pytest.config import Config
from _pytest.config.argparsing import Parser

# Import fixtures so pytest can discover them
from tenro.pytest_plugin.fixtures import construct

if TYPE_CHECKING:
    from tenro.capabilities.types import CapabilityReport
    from tenro.construct.construct import Construct

# Module-level state
_plugin_enabled = False
_trace_enabled = False
_export_enabled = False
_undeclared_mode: str = "ignore"

# Re-export fixtures for pytest discovery
__all__ = ["construct"]


def _build_report_from_constructs(constructs: list[Construct]) -> CapabilityReport:
    """Build a merged capability report from session constructs."""
    from tenro.capabilities.global_registry import GlobalDeclaredRegistry
    from tenro.capabilities.reporting import build_report, merge_reports

    snapshot = GlobalDeclaredRegistry.snapshot()
    reports = [construct.build_coverage_report() for construct in constructs]
    merged_report = merge_reports(reports)
    return build_report(
        observability=merged_report.observability,
        declared_tools=snapshot.tools,
        executed_tools=merged_report.executed_tools,
        declared_hosts=snapshot.hosts,
        observed_hosts=merged_report.observed_hosts,
    )


def _load_report(path: Path) -> CapabilityReport:
    """Load a capability report from a JSON artifact."""
    from tenro.capabilities.types import CapabilityReport

    data = json.loads(path.read_text())
    data.pop("timestamp", None)
    return CapabilityReport.model_validate(data)


def _merge_worker_reports(output_dir: Path) -> CapabilityReport | None:
    """Merge worker capability artifacts when running as controller."""
    paths = sorted(output_dir.glob("capabilities.gw*.json"))
    if not paths:
        return None
    from tenro.capabilities.reporting import merge_reports

    reports = [_load_report(path) for path in paths]
    return merge_reports(reports)


def _collect_report(worker_id: str | None) -> CapabilityReport | None:
    """Collect a report from constructs or merged worker artifacts."""
    from tenro.capabilities.exporter import ArtifactExporter
    from tenro.pytest_plugin.construct_registry import get_constructs

    constructs = get_constructs()
    if constructs:
        return _build_report_from_constructs(constructs)
    if worker_id is None:
        return _merge_worker_reports(Path(ArtifactExporter.DEFAULT_OUTPUT_DIR))
    return None


def _export_report(report: CapabilityReport, worker_id: str | None) -> None:
    """Export capability and coverage artifacts for a report."""
    from tenro.capabilities.exporter import ArtifactExporter

    exporter = ArtifactExporter(worker_id=worker_id)
    exporter.export_capabilities(report)
    exporter.export_coverage(report)


def _handle_undeclared(report: CapabilityReport, session: pytest.Session) -> None:
    """Emit warnings or failures for undeclared capability usage."""
    if not report.security.has_undeclared():
        return
    if _undeclared_mode == "warn":
        warnings.warn(
            "Tenro: undeclared capabilities detected during test run.",
            stacklevel=2,
        )
        return
    if _undeclared_mode == "fail":
        session.exitstatus = 1


def pytest_addoption(parser: Parser) -> None:
    """Add Tenro CLI options to pytest.

    Args:
        parser: Pytest argument parser.
    """
    group = parser.getgroup("tenro")
    group.addoption(
        "--tenro",
        action="store_true",
        default=False,
        help="Enable Tenro tracing and constructing for agent tests",
    )
    group.addoption(
        "--tenro-trace",
        action="store_true",
        default=False,
        help="Print trace visualization after each test",
    )
    group.addoption(
        "--tenro-export",
        action="store_true",
        default=False,
        dest="tenro_export",
        help="Export capability coverage artifacts to .tenro/artifacts/",
    )
    group.addoption(
        "--tenro-undeclared",
        type=str,
        default="ignore",
        choices=["ignore", "warn", "fail"],
        dest="tenro_undeclared",
        help="How to handle undeclared capabilities: ignore, warn, fail",
    )


def pytest_configure(config: Config) -> None:
    """Configure Tenro plugin when pytest starts.

    Registers markers and toggles plugin state based on --tenro or
    TENRO_ENABLED. Trace output is enabled via --tenro-trace or TENRO_TRACE.

    Args:
        config: Pytest configuration object.
    """
    global _plugin_enabled, _trace_enabled, _export_enabled, _undeclared_mode

    # Register custom marker
    config.addinivalue_line(
        "markers",
        "tenro: Mark test for Tenro tracing and constructing",
    )

    truthy_values = ("true", "1", "yes")

    # Check if plugin should be enabled
    _plugin_enabled = (
        config.getoption("--tenro", default=False)
        or os.getenv("TENRO_ENABLED", "").lower() in truthy_values
    )

    # Check if trace output should be enabled
    _trace_enabled = (
        config.getoption("--tenro-trace", default=False)
        or os.getenv("TENRO_TRACE", "").lower() in truthy_values
    )

    # Check if export is enabled
    _export_enabled = (
        config.getoption("tenro_export", default=False)
        or os.getenv("TENRO_EXPORT", "").lower() in truthy_values
    )

    # Check undeclared mode
    _undeclared_mode = config.getoption("tenro_undeclared", default="ignore")
    env_mode = os.getenv("TENRO_UNDECLARED", "").lower()
    if env_mode in ("ignore", "warn", "fail"):
        _undeclared_mode = env_mode


def pytest_collection_modifyitems(config: Config, items: list[pytest.Item]) -> None:
    """Collection hook for selective tracing.

    Args:
        config: Pytest configuration.
        items: Collected test items.
    """
    if not _plugin_enabled:
        return

    pass


def pytest_runtest_setup(item: pytest.Item) -> None:
    """Setup hook called before each test runs.

    Args:
        item: Test item about to run.
    """
    if not _plugin_enabled:
        return

    if "tenro" in item.keywords or _plugin_enabled:
        pass


def pytest_runtest_call(item: pytest.Item) -> None:
    """Hook called when test is executed.

    Args:
        item: Test item being executed.
    """
    if not _plugin_enabled:
        return

    pass


def pytest_runtest_teardown(item: pytest.Item) -> None:
    """Teardown hook called after each test.

    Renders trace visualization if --tenro-trace is enabled and the test
    used the construct fixture.

    Args:
        item: Test item that just ran.
    """
    if not _trace_enabled:
        return

    # Check if this test used the construct fixture
    construct = getattr(item, "_tenro_construct", None)
    if construct is None:
        return

    # Render trace if there are any agent runs
    agents = construct.agent_runs
    if not agents:
        return

    from tenro.debug import TraceConfig, TraceRenderer

    config = TraceConfig(enabled=True)
    renderer = TraceRenderer(config=config)
    renderer.render(agents, test_name=item.name)


def pytest_sessionstart(session: pytest.Session) -> None:
    """Called at session start before collection.

    Clears GlobalDeclaredRegistry to ensure fresh state for this test run.

    Args:
        session: Pytest session object (unused).
    """
    del session  # unused but required by pytest hook signature
    from tenro.capabilities.global_registry import GlobalDeclaredRegistry
    from tenro.pytest_plugin.construct_registry import clear_constructs

    GlobalDeclaredRegistry.clear()
    clear_constructs()


def pytest_sessionfinish(
    session: pytest.Session,
    exitstatus: int,
) -> None:
    """Called at session end after all tests.

    Exports capability coverage artifacts if --tenro-export is enabled.
    Handles pytest-xdist worker suffixing and controller merging.

    Args:
        session: Pytest session object.
        exitstatus: Exit status of the test run (unused).
    """
    if not _export_enabled:
        return
    del exitstatus

    worker_id = os.getenv("PYTEST_XDIST_WORKER") or None
    report = _collect_report(worker_id)
    if report is None:
        return

    _export_report(report, worker_id)
    _handle_undeclared(report, session)
