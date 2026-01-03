# Copyright 2025 Tenro.ai
# SPDX-License-Identifier: Apache-2.0

"""Provider endpoint registry for LLM simulation.

Provides a central registry for provider configurations, compatibility families,
and endpoint contracts. Supports plugin discovery via entry points.
"""

from __future__ import annotations

from tenro.construct.http.registry.builtin import register_builtin_providers
from tenro.construct.http.registry.exceptions import (
    ContractValidationError,
    DeprecatedVersionWarning,
    PresetNotFoundError,
    ProviderError,
    UnsupportedEndpointError,
    UnsupportedProviderError,
)
from tenro.construct.http.registry.plugins import PluginLoadWarning, discover_provider_plugins
from tenro.construct.http.registry.registry import ProviderRegistry
from tenro.construct.http.registry.types import (
    Capability,
    CompatibilityFamily,
    EndpointContract,
    PresetSpec,
    ProviderConfig,
    ResponseTransformer,
)

register_builtin_providers()

__all__ = [
    "Capability",
    "CompatibilityFamily",
    "ContractValidationError",
    "DeprecatedVersionWarning",
    "EndpointContract",
    "PluginLoadWarning",
    "PresetNotFoundError",
    "PresetSpec",
    "ProviderConfig",
    "ProviderError",
    "ProviderRegistry",
    "ResponseTransformer",
    "UnsupportedEndpointError",
    "UnsupportedProviderError",
    "discover_provider_plugins",
    "register_builtin_providers",
]
