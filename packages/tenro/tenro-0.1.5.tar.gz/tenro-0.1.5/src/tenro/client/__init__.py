# Copyright 2025 Tenro.ai
# SPDX-License-Identifier: Apache-2.0

"""Testing module for Tenro SDK.

This module provides:
- Core testing functionality (init, client, tracing)
- Pytest plugin integration (auto-loaded via pytest11 entry point)
- Pytest fixtures (construct)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from tenro.client._client import Tenro
from tenro.client.init import init

# Pytest plugin components are lazy-loaded to avoid requiring pytest at import time.
# They are auto-loaded by pytest via the pytest11 entry point when running tests.
if TYPE_CHECKING:
    from tenro.pytest_plugin.fixtures import construct as construct
    from tenro.pytest_plugin.marks import tenro as tenro

__all__ = [
    # Core testing API
    "init",
    "Tenro",
    # Pytest fixtures (auto-loaded by pytest, exported for convenience)
    "construct",
    # Pytest marker (optional, for explicit imports)
    "tenro",
]


def __getattr__(name: str) -> object:
    """Lazy load pytest plugin components to avoid requiring pytest at import time."""
    if name == "construct":
        from tenro.pytest_plugin.fixtures import construct

        return construct
    if name == "tenro":
        from tenro.pytest_plugin.marks import tenro

        return tenro
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
