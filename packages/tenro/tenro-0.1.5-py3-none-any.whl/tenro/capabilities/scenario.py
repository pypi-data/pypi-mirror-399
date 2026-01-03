# Copyright 2025 Tenro.ai
# SPDX-License-Identifier: Apache-2.0

"""Scenario context for capability tracking.

Provides push/pop scenario stack using contextvars for test scenario
attribution in capability reports.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar, Token

# Scenario stack as contextvar for async safety
_scenario_stack: ContextVar[tuple[str, ...]] = ContextVar("scenario_stack", default=())


def push_scenario(name: str) -> Token[tuple[str, ...]]:
    """Push a scenario onto the stack.

    Args:
        name: Scenario name.

    Returns:
        Token for resetting to previous state.
    """
    current = _scenario_stack.get()
    return _scenario_stack.set(current + (name,))


def pop_scenario(token: Token[tuple[str, ...]]) -> None:
    """Pop scenario by resetting to token.

    Args:
        token: Token from push_scenario.
    """
    import contextlib

    with contextlib.suppress(ValueError):
        _scenario_stack.reset(token)


def get_current_scenarios() -> list[str]:
    """Get current scenario path as list.

    Returns:
        Copy of scenario stack as list.
    """
    return list(_scenario_stack.get())


def reset_scenarios() -> None:
    """Reset scenario stack to empty.

    Used for test cleanup.
    """
    _scenario_stack.set(())


@contextmanager
def scenario(name: str) -> Iterator[None]:
    """Context manager for scenario scope.

    Args:
        name: Scenario name.

    Yields:
        None.

    Example:
        >>> with scenario("happy_path"):
        ...     construct.simulate_tool("search", result="found")
        ...     agent.run()
    """
    token = push_scenario(name)
    try:
        yield
    finally:
        pop_scenario(token)


__all__ = [
    "get_current_scenarios",
    "pop_scenario",
    "push_scenario",
    "reset_scenarios",
    "scenario",
]
