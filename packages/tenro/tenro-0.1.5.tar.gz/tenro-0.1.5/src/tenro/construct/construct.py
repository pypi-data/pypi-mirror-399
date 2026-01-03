# Copyright 2025 Tenro.ai
# SPDX-License-Identifier: Apache-2.0

"""Active construct for simulating agent tool calls and tracking lifecycle spans.

Provides lifecycle tracking, simulation helpers, provider-aware LLM simulation,
and verification APIs for tests.
"""

from __future__ import annotations

from collections.abc import Callable
from contextlib import AbstractContextManager
from typing import TYPE_CHECKING, Any

from tenro.construct.http import HttpInterceptor
from tenro.construct.in_memory_store import EventStore
from tenro.construct.lifecycle import SpanAccessor, SpanLinker
from tenro.construct.simulate.orchestrator import SimulationOrchestrator
from tenro.construct.verify import ConstructVerifications
from tenro.core.lifecycle_manager import LifecycleManager
from tenro.core.spans import AgentRun, LLMCall, ToolCall

if TYPE_CHECKING:
    from tenro.capabilities.types import DeclaredTool, ExecutedTool, ObservedHost, ResolutionError


class Construct:
    """Active construct for simulating tools and tracking operation lifecycle.

    Tracks LLM calls and tool calls as mutable span objects that update in
    real-time, providing a simple API for testing.

    Features:
        - Simulate tool calls with smart defaults
        - Track LLM and tool calls as mutable span objects
        - Provider helpers for OpenAI, Anthropic, and Gemini
        - Expressive assertion API for readable tests

    Examples:
        >>> # Pytest usage (recommended)
        >>> def test_my_agent(construct):  # Auto-activated by fixture!
        ...     construct.simulate_tool("search", returns=["doc1", "doc2"])
        ...     result = my_agent.run()
        ...     construct.verify_tool("search", times=1)
        >>>
        >>> # LLM simulation
        >>> def test_llm_agent(construct):
        ...     construct.simulate_llm(
        ...         "openai.chat.completions.create",
        ...         responses="Hello! How can I help?"
        ...     )
        ...     result = my_agent.run()
        ...     assert construct.llm_calls[0].response == "Hello! How can I help?"
        >>>
        >>> # Manual activation (non-pytest or multi-step tests)
        >>> construct = Construct()
        >>> construct.simulate_tool("search", returns=["doc1"])
        >>> with construct:
        ...     result = my_agent.run()
        >>> construct.verify_tool("search", times=1)
    """

    def __init__(
        self,
        blocked_llm_domains: list[str] | None = None,
        allow_real_llm_calls: bool = False,
    ) -> None:
        """Initialize construct for event-based tracking and simulation.

        The construct wraps user code via context manager to track LLM and
        tool calls. User code runs inside the `with construct:` block.

        Args:
            blocked_llm_domains: Domains that raise `UnexpectedLLMCallError` if
                accessed without a simulation. Defaults to OpenAI, Anthropic,
                and Gemini. Pass custom list to block different providers, or
                empty list `[]` to disable blocking.
            allow_real_llm_calls: Allow HTTP requests to LLM providers without
                simulations. When False (default), requests to blocked LLM
                domains without matching simulations raise `UnexpectedLLMCallError`,
                preventing accidental real API calls that cost money or leak
                credentials. Set to True for integration tests that intentionally
                call real APIs. Equivalent to `blocked_llm_domains=[]`.

        Example:
            ```python
            # Default: blocks real LLM calls
            construct = Construct()

            # Allow real API calls (integration tests)
            construct = Construct(allow_real_llm_calls=True)

            # Custom blocklist
            construct = Construct(blocked_llm_domains=["api.cohere.ai"])
            ```
        """
        self._event_store = EventStore()
        self._trace_id: str | None = None

        effective_domains = [] if allow_real_llm_calls else blocked_llm_domains

        self._lifecycle = LifecycleManager(event_store=self._event_store)
        self._http_interceptor = HttpInterceptor(
            on_call=self._handle_http_call,
            blocked_llm_domains=effective_domains,
        )

        self._orchestrator = SimulationOrchestrator(
            lifecycle=self._lifecycle,
            http_interceptor=self._http_interceptor,
        )
        self._linker = SpanLinker(lifecycle=self._lifecycle)
        self._span_accessor = SpanAccessor(event_store=self._event_store)

        self._verifications: ConstructVerifications | None = None

    @property
    def agent_runs(self) -> list[AgentRun]:
        """Get all agent runs as a flat list (reconstructed from events).

        Returns:
            Flat list of all agent runs (includes nested agents).

        Examples:
            >>> agents = construct.agent_runs
            >>> assert len(agents) == 3  # Manager, Researcher, Writer
            >>> assert agents[0].name == "Manager"
            >>> assert agents[1].parent_agent_id == agents[0].id
        """
        return self._span_accessor.get_all_agent_runs()

    def _get_root_agent_runs(self) -> list[AgentRun]:
        """Get root agent runs with populated spans."""
        return self._span_accessor.get_root_agent_runs()

    @property
    def llm_calls(self) -> list[LLMCall]:
        """Get LLM calls across all agents and orphan calls.

        Returns:
            Flat list of LLM calls (includes orphan calls without agent parent).

        Examples:
            >>> llm_calls = construct.llm_calls
            >>> assert len(llm_calls) == 3
        """
        return self._span_accessor.get_llm_calls()

    @property
    def tool_calls(self) -> list[ToolCall]:
        """Get tool calls across all agents and orphan calls.

        Returns:
            Flat list of tool calls (includes orphan calls without agent parent).

        Examples:
            >>> tool_calls = construct.tool_calls
            >>> assert len(tool_calls) == 2
        """
        return self._span_accessor.get_tool_calls()

    def _check_unused_llm_simulations(self) -> None:
        """Check for unused simulations and raise errors immediately."""
        from tenro.construct.http.interceptor import get_supported_providers

        try:
            self._orchestrator.simulation_tracker.validate(
                llm_calls=self.llm_calls,
                supported_providers=list(get_supported_providers()),
                llm_scopes=self._span_accessor.get_llm_scopes(),
            )
        finally:
            self._orchestrator.simulation_tracker.reset()

    def link_agent(
        self, name: str, input_data: Any = None, **kwargs: Any
    ) -> AbstractContextManager[AgentRun]:
        """Link an agent execution with automatic lifecycle management.

        Creates an AgentRun span with automatic parent tracking, latency
        calculation, and stack-safe cleanup.

        Args:
            name: Agent name.
            input_data: Input data for the agent.
            **kwargs: Additional keyword arguments passed to the agent.

        Returns:
            Context manager yielding mutable AgentRun span.

        Examples:
            >>> with construct.link_agent("Manager", input_data="task") as agent:
            ...     # Nested operations automatically get Manager as parent
            ...     agent.output_data = "completed"
            >>> with construct.link_agent("RiskAgent", threshold=0.8) as agent:
            ...     # Agent called with threshold parameter
            ...     agent.output_data = "low risk"
        """
        return self._linker.link_agent(name, input_data, **kwargs)

    def link_tool(
        self, tool_name: str, *args: Any, **kwargs: Any
    ) -> AbstractContextManager[ToolCall]:
        """Link a tool call with automatic lifecycle management.

        Creates a ToolCall span with automatic parent tracking, latency
        calculation, and stack-safe cleanup.

        Args:
            tool_name: Name of the tool being called.
            *args: Positional arguments passed to the tool.
            **kwargs: Keyword arguments passed to the tool.

        Returns:
            Context manager yielding mutable ToolCall span.

        Examples:
            >>> with construct.link_tool("search") as tool:
            ...     tool.result = ["doc1", "doc2"]
            >>> with construct.link_tool("search", "query", limit=10) as tool:
            ...     tool.result = ["doc1", "doc2"]
            >>> with construct.link_tool("api_call", "POST", timeout=30) as tool:
            ...     tool.result = {"status": 200}
        """
        return self._linker.link_tool(tool_name, *args, **kwargs)

    def simulate_tool(
        self,
        target: str | Callable[..., Any],
        result: Any = None,
        results: list[Any] | None = None,
        side_effect: Callable[..., Any] | None = None,
    ) -> None:
        """Simulate an agent tool with lifecycle tracking.

        Automatically creates ToolCall spans for tracking.

        Args:
            target: Tool module path (e.g., "myapp.tools.search") or function object.
            result: Single static value to return (most common case).
            results: List of values for sequential calls. Can include Exception
                objects which will be raised when reached.
            side_effect: Callable for dynamic behavior. Receives tool arguments.

        Raises:
            ValueError: If multiple result parameters are provided.

        Examples:
            >>> # Single result (most common)
            >>> construct.simulate_tool("myapp.tools.search", result="doc1")
            >>>
            >>> # Sequential results with exceptions
            >>> construct.simulate_tool(
            ...     "myapp.tools.api_call",
            ...     results=[{"status": "ok"}, TimeoutError("Connection lost"), {"status": "ok"}],
            ... )
            >>>
            >>> # Dynamic behavior
            >>> def weather_logic(city: str):
            ...     return {"temp": 72 if city == "SF" else 65}
            >>> construct.simulate_tool("myapp.tools.get_weather", side_effect=weather_logic)
            >>>
            >>> # Function object (refactor-safe)
            >>> from myapp.tools import search
            >>> construct.simulate_tool(search, result="doc1")
        """
        self._orchestrator.simulate_tool(target, result, results, side_effect)

    def simulate_agent(
        self,
        target: str | Callable[..., Any],
        result: Any = None,
        results: list[Any] | None = None,
        side_effect: Callable[..., Any] | None = None,
    ) -> None:
        """Simulate an agent with lifecycle tracking.

        Agents are high-level workflows that orchestrate tools and LLMs.
        This method allows testing agent behavior in isolation.

        Args:
            target: Agent module path (e.g., "myapp.agents.planner") or function object.
            result: Single static value to return (most common case).
            results: List of values for sequential calls. Can include Exception
                objects which will be raised when reached.
            side_effect: Callable for dynamic behavior. Receives agent arguments.

        Raises:
            ValueError: If multiple result parameters are provided.

        Examples:
            >>> # Single result (most common)
            >>> construct.simulate_agent("myapp.agents.planner", result={"plan": "step1"})
            >>>
            >>> # Sequential results with exceptions
            >>> construct.simulate_agent(
            ...     "myapp.agents.researcher",
            ...     results=[
            ...         {"findings": "data1"},
            ...         TimeoutError("Research timeout"),
            ...         {"findings": "retry_data"},
            ...     ],
            ... )
            >>>
            >>> # Dynamic behavior
            >>> def agent_logic(query: str):
            ...     return {"result": f"processed_{query}"}
            >>> construct.simulate_agent("myapp.agents.processor", side_effect=agent_logic)
            >>>
            >>> # Function object (refactor-safe)
            >>> from myapp.agents import planner
            >>> construct.simulate_agent(planner, result={"plan": "step1"})
        """
        self._orchestrator.simulate_agent(target, result, results, side_effect)

    def __enter__(self) -> Construct:
        """Activate simulations and start HTTP interception.

        Registers this construct as the active construct for decorator access.
        After activation, subsequent simulate_* calls apply patches immediately.
        """
        from tenro.linking.decorators import _set_active_construct

        _set_active_construct(self)
        self._orchestrator.activate()
        return self

    def __exit__(
        self,
        _exc_type: type[BaseException] | None,
        _exc_value: BaseException | None,
        _exc_traceback: Any,
    ) -> None:
        """Restore original functions/methods and cleanup state.

        Harness errors (e.g., unused simulations) are raised immediately.

        Note:
            Never suppresses incoming exceptions from test body.
        """
        from tenro.linking.decorators import _set_active_construct

        _set_active_construct(None)
        try:
            self._check_unused_llm_simulations()
        finally:
            self._orchestrator.deactivate()

    def _get_verifications(self) -> ConstructVerifications:
        """Get verifications instance with reconstructed spans."""
        return ConstructVerifications(
            agent_runs=self._get_root_agent_runs(),
            llm_calls=self.llm_calls,
            tool_calls=self.tool_calls,
        )

    def verify_tool(
        self,
        target: str | Callable[..., Any],
        called_with: dict[str, Any] | None = None,
        *,
        times: int | None = None,
        output: Any = None,
        output_contains: str | None = None,
        output_exact: Any = None,
        call_index: int | None = 0,
        **kwargs: Any,
    ) -> None:
        """Verify tool was called with optional argument and output matching.

        Args:
            target: Name, path, or function object of the tool.
            called_with: Dict of expected arguments. Use when a key conflicts
                with a verification parameter like "times".
            times: Expected number of calls (None = at least once).
            output: Expected output (dict=subset match, scalar=exact).
            output_contains: Expected substring in output.
            output_exact: Expected output (strict deep equality).
            call_index: Which call to check (0=first, -1=last, None=any).
            **kwargs: Expected keyword arguments.

        Raises:
            AssertionError: If verification fails.

        Examples:
            >>> construct.verify_tool("fetch_data")  # at least once
            >>> construct.verify_tool(fetch_data, times=1)  # pass function object
            >>> construct.verify_tool("get_weather", output={"temp": 72})
        """
        from tenro.construct.simulate.target_resolution import (
            resolve_target_for_verification,
        )

        resolved_target = resolve_target_for_verification(target)
        self._get_verifications().verify_tool(
            resolved_target,
            called_with,
            times=times,
            output=output,
            output_contains=output_contains,
            output_exact=output_exact,
            call_index=call_index,
            **kwargs,
        )

    def verify_tool_never(self, target: str | Callable[..., Any]) -> None:
        """Verify tool was never called.

        Args:
            target: Name, path, or function object of the tool.

        Raises:
            AssertionError: If tool was called.

        Examples:
            >>> construct.verify_tool_never("dangerous_operation")
            >>> construct.verify_tool_never(dangerous_operation)
        """
        from tenro.construct.simulate.target_resolution import (
            resolve_target_for_verification,
        )

        resolved_target = resolve_target_for_verification(target)
        self._get_verifications().verify_tool_never(resolved_target)

    def verify_tool_sequence(self, expected_sequence: list[str]) -> None:
        """Verify tools were called in a specific order.

        Args:
            expected_sequence: Expected sequence of tool names.

        Raises:
            AssertionError: If sequence doesn't match.

        Examples:
            >>> construct.verify_tool_sequence(["search", "summarize", "format"])
        """
        self._get_verifications().verify_tool_sequence(expected_sequence)

    def verify_tools(
        self,
        count: int | None = None,
        min: int | None = None,
        max: int | None = None,
        target: str | None = None,
    ) -> None:
        """Verify tool calls with optional count/range and name filter.

        Args:
            count: Expected exact number of calls (mutually exclusive with min/max).
            min: Minimum number of calls (inclusive).
            max: Maximum number of calls (inclusive).
            target: Optional tool name filter.

        Raises:
            AssertionError: If verification fails.
            ValueError: If count and min/max are both specified.

        Examples:
            >>> construct.verify_tools()  # at least one tool call
            >>> construct.verify_tools(count=3)  # exactly 3 tool calls
            >>> construct.verify_tools(min=2, max=4)  # between 2 and 4 calls
        """
        self._get_verifications().verify_tools(count=count, min=min, max=max, target=target)

    def verify_agent(
        self,
        target: str | Callable[..., Any],
        called_with: dict[str, Any] | None = None,
        *,
        times: int | None = None,
        output: Any = None,
        output_contains: str | None = None,
        output_exact: Any = None,
        call_index: int | None = 0,
        **kwargs: Any,
    ) -> None:
        """Verify agent was called with optional argument and output matching.

        Args:
            target: Name, path, or function object of the agent.
            called_with: Dict of expected arguments. Use when a key conflicts
                with a verification parameter like "times".
            times: Expected number of calls (None = at least once).
            output: Expected output (dict=subset match, scalar=exact).
            output_contains: Expected substring in output.
            output_exact: Expected output (strict deep equality).
            call_index: Which call to check (0=first, -1=last, None=any).
            **kwargs: Expected keyword arguments.

        Raises:
            AssertionError: If verification fails.

        Examples:
            >>> construct.verify_agent("RiskAgent")  # at least once
            >>> construct.verify_agent(risk_agent, times=1)  # pass function object
            >>> construct.verify_agent("RiskAgent", threshold=0.8)  # with arg
        """
        from tenro.construct.simulate.target_resolution import (
            resolve_target_for_verification,
        )

        resolved_target = resolve_target_for_verification(target)
        self._get_verifications().verify_agent(
            resolved_target,
            called_with,
            times=times,
            output=output,
            output_contains=output_contains,
            output_exact=output_exact,
            call_index=call_index,
            **kwargs,
        )

    def verify_agent_never(self, target: str | Callable[..., Any]) -> None:
        """Verify agent was never called.

        Args:
            target: Name, path, or function object of the agent.

        Raises:
            AssertionError: If agent was called.

        Examples:
            >>> construct.verify_agent_never("FallbackAgent")
            >>> construct.verify_agent_never(fallback_agent)
        """
        from tenro.construct.simulate.target_resolution import (
            resolve_target_for_verification,
        )

        resolved_target = resolve_target_for_verification(target)
        self._get_verifications().verify_agent_never(resolved_target)

    def verify_agent_sequence(self, expected_sequence: list[str]) -> None:
        """Verify agents were called in a specific order.

        Args:
            expected_sequence: Expected sequence of agent names.

        Raises:
            AssertionError: If sequence doesn't match.

        Examples:
            >>> construct.verify_agent_sequence(["Planner", "Executor", "Reviewer"])
        """
        self._get_verifications().verify_agent_sequence(expected_sequence)

    def verify_agents(
        self,
        count: int | None = None,
        min: int | None = None,
        max: int | None = None,
        target: str | None = None,
    ) -> None:
        """Verify agent calls with optional count/range and name filter.

        Args:
            count: Expected exact number of calls (mutually exclusive with min/max).
            min: Minimum number of calls (inclusive).
            max: Maximum number of calls (inclusive).
            target: Optional agent name filter.

        Raises:
            AssertionError: If verification fails.
            ValueError: If count and min/max are both specified.

        Examples:
            >>> construct.verify_agents()  # at least one agent call
            >>> construct.verify_agents(count=2)  # exactly 2 agent calls
        """
        self._get_verifications().verify_agents(count=count, min=min, max=max, target=target)

    def verify_llm(
        self,
        target: str | None = None,
        provider: str | None = None,
        *,
        times: int | None = None,
        output: Any = None,
        output_contains: str | None = None,
        output_exact: Any = None,
        where: str | None = None,
        call_index: int | None = None,
    ) -> None:
        """Verify LLM was called with optional output checking.

        Args:
            target: Optional target filter (e.g., "openai.chat.completions.create").
            provider: Optional provider filter (e.g., "openai", "anthropic").
            times: Expected number of calls (None = at least once).
            output: Expected output (dict=subset match, scalar=exact).
            output_contains: Expected substring in response text.
            output_exact: Expected output (strict deep equality).
            where: Output location to check (None=response, "json"=parsed JSON).
            call_index: Which call to check (0=first, -1=last, None=any).

        Raises:
            AssertionError: If verification fails.

        Examples:
            >>> construct.verify_llm()  # at least one LLM call
            >>> construct.verify_llm(provider="openai", times=1)
            >>> construct.verify_llm(output_contains="weather")
        """
        self._get_verifications().verify_llm(
            target,
            provider,
            times=times,
            output=output,
            output_contains=output_contains,
            output_exact=output_exact,
            where=where,
            call_index=call_index,
        )

    def verify_llm_never(self, target: str | None = None, provider: str | None = None) -> None:
        """Verify LLM was never called.

        Args:
            target: Optional target filter (e.g., "openai.chat.completions.create").
            provider: Optional provider filter (e.g., "openai", "anthropic").

        Raises:
            AssertionError: If LLM was called.

        Examples:
            >>> construct.verify_llm_never()  # no LLM calls at all
            >>> construct.verify_llm_never(provider="anthropic")  # no Anthropic calls
        """
        self._get_verifications().verify_llm_never(target, provider)

    def verify_llms(
        self,
        count: int | None = None,
        min: int | None = None,
        max: int | None = None,
        target: str | None = None,
        provider: str | None = None,
    ) -> None:
        """Verify LLM calls with optional count/range and filters.

        Args:
            count: Expected exact number of calls (mutually exclusive with min/max).
            min: Minimum number of calls (inclusive).
            max: Maximum number of calls (inclusive).
            target: Optional target path filter.
            provider: Optional provider filter.

        Raises:
            AssertionError: If verification fails.
            ValueError: If count and min/max are both specified.

        Examples:
            >>> construct.verify_llms()  # at least one LLM call
            >>> construct.verify_llms(count=3)  # exactly 3 LLM calls
            >>> construct.verify_llms(provider="anthropic")  # only Anthropic calls
        """
        self._get_verifications().verify_llms(
            count=count, min=min, max=max, target=target, provider=provider
        )

    def simulate_llm(
        self,
        target: str | Callable[..., Any] | None = None,
        provider: str | None = None,
        *,
        response: str | None = None,
        responses: str | list[str | Exception] | None = None,
        model: str | None = None,
        tools: list[str | dict[str, Any]] | None = None,
        use_http: bool | None = None,
        optional: bool = False,
        **response_kwargs: Any,
    ) -> None:
        """Simulate LLM calls with smart provider detection and lifecycle tracking.

        This method keeps the API simple while preserving provider-accurate
        responses when possible:
        - Accepts plain text responses
        - Auto-detects known provider SDK targets
        - Uses HTTP interception for known providers (default without custom target)
        - Falls back to setattr patching for custom wrappers
        - Creates LLMCall spans for lifecycle tracking

        HTTP interception ensures the provider SDK parses JSON and yields
        real SDK types (e.g., `TextBlock`, `ChatCompletion`).

        Supports text generation APIs only. Supported targets include:
        - OpenAI Chat Completions (`openai.chat.completions.create`)
        - Anthropic Messages (`anthropic.resources.messages.Messages.create`)
        - Gemini GenerateContent (`google.genai.models.Models.generate_content`)

        For other provider APIs (embeddings, audio, images, assistants),
        register a custom provider schema or use a custom target.

        Args:
            target: Optional Python function path to simulate (e.g.,
                "openai.chat.completions.create"). If not provided, uses the
                default target for the specified provider. When target is
                provided, setattr patching is used (not HTTP interception).
            provider: LLM provider ("openai", "anthropic", "gemini", "custom").
                Auto-detected from target if not provided. Required when
                target is not provided.
            response: Single string response (most common case).
            responses: List of responses for sequential calls. Can include
                Exception objects which will be raised when reached.
            model: Model identifier (e.g., "gpt-4", "claude-3-opus").
                Overrides provider default model name.
            tools: Tool calls to include in the response. Use simplified or
                full format:
                - Simplified (no args): ["tool_name_1", "tool_name_2"]
                - With arguments: [{"name": "tool1", "arguments": {"key": "value"}}]
                - Full spec: [{"id": "call_123", "type": "function", "function": {...}}]
                This generates the LLM's decision to call these tools.
            use_http: Force HTTP interception (True) or setattr patching (False).
                Defaults to True for known providers when no custom target is
                specified.
            optional: If True, this simulation won't cause UnusedSimulationError
                if unused. Use for branch coverage or optional paths. Defaults
                to False.
            **response_kwargs: Provider-specific options:
                - token_usage: Dict with token counts (e.g., {"total_tokens": 50})
                - finish_reason: Override finish reason ("stop", "length", "tool_calls")
                - stop_reason: Anthropic-specific stop reason
                - safety_ratings: Gemini-specific safety ratings
                - (Other provider-specific parameters)

        Raises:
            ValueError: If both `response` and `responses` are provided.

        Examples:
            >>> # Single response (most common, uses HTTP interception)
            >>> construct.simulate_llm(provider="anthropic", response="Hello!")
            >>>
            >>> # Multi-turn conversation
            >>> construct.simulate_llm(
            ...     provider="anthropic",
            ...     responses=["Turn 1", "Turn 2", "Turn 3"],
            ... )
            >>>
            >>> # Custom target (uses setattr patching)
            >>> construct.simulate_llm(
            ...     target="myapp.llm_wrapper.call",
            ...     provider="anthropic",
            ...     response="Hello!",
            ... )
            >>>
            >>> # Force setattr patching (returns dicts, not SDK types)
            >>> construct.simulate_llm(
            ...     provider="anthropic",
            ...     response="Hello!",
            ...     use_http=False,
            ... )
            >>>
            >>> # Optional simulation for branch coverage
            >>> construct.simulate_llm(
            ...     provider="openai",
            ...     response="Fallback response",
            ...     optional=True,
            ... )
        """
        self._orchestrator.simulate_llm(
            target=target,
            provider=provider,
            response=response,
            responses=responses,
            model=model,
            tools=tools,
            use_http=use_http,
            optional=optional,
            **response_kwargs,
        )

    def _handle_http_call(
        self,
        provider: str,
        messages: list[dict[str, Any]],
        model: str | None,
        response_text: str,
        agent: str | None,
    ) -> None:
        """Callback for HTTP interception - delegates to orchestrator."""
        self._orchestrator.handle_http_call(provider, messages, model, response_text, agent)

    # ==========================================================================
    # Capability Tracking API
    # ==========================================================================

    def declare_tool(
        self,
        name: str,
        *,
        description: str | None = None,
        agent_name: str | None = None,
        input_schema: dict[str, Any] | None = None,
    ) -> None:
        """Declare an expected tool for attack surface tracking.

        Register tools that your agent is expected to use. Used for coverage
        calculation and security smell detection.

        Args:
            name: Tool name.
            description: Human-readable description.
            agent_name: Agent this tool belongs to. None = global tool.
            input_schema: JSON Schema for input parameters.

        Examples:
            >>> construct.declare_tool("search", description="Search the web")
            >>> construct.declare_tool("fetch", agent_name="ResearchAgent")
        """
        from tenro.capabilities.global_registry import GlobalDeclaredRegistry
        from tenro.capabilities.types import DeclaredTool, compute_schema_hash

        canonical_id = f"manual://{name}"
        schema_hash = compute_schema_hash(input_schema) if input_schema else None

        tool = DeclaredTool(
            canonical_id=canonical_id,
            name=name,
            description=description,
            agent_name=agent_name,
            source="manual",
            input_schema=input_schema,
            schema_hash=schema_hash,
        )
        GlobalDeclaredRegistry.register_tool(tool)

    def declare_mcp_server(
        self,
        name: str,
        *,
        tools: list[str],
        transport: str = "stdio",
    ) -> None:
        """Declare an MCP server with its tools.

        Args:
            name: MCP server name.
            tools: List of tool names provided by this server.
            transport: MCP transport type (stdio, http, sse).

        Examples:
            >>> construct.declare_mcp_server(
            ...     name="filesystem-server",
            ...     tools=["read_file", "write_file", "list_directory"],
            ... )
        """
        from tenro.capabilities.global_registry import GlobalDeclaredRegistry
        from tenro.capabilities.types import DeclaredTool, MCPServer

        mcp_tools = [
            DeclaredTool(
                canonical_id=f"mcp://{name}/{tool_name}",
                name=tool_name,
                source="mcp",
            )
            for tool_name in tools
        ]

        server = MCPServer(
            name=name,
            transport=transport,  # type: ignore[arg-type]
            tools=mcp_tools,
        )
        GlobalDeclaredRegistry.register_mcp_server(server)

    def declare_host(
        self,
        host: str,
        *,
        agent_name: str | None = None,
    ) -> None:
        """Declare an expected external host.

        Register hosts your agent is expected to access. Used for security
        smell detection (undeclared host access).

        Args:
            host: Hostname (e.g., "api.weather.com").
            agent_name: Agent expected to access this host.

        Examples:
            >>> construct.declare_host("api.weather.com", agent_name="WeatherAgent")
        """
        from tenro.capabilities.global_registry import GlobalDeclaredRegistry
        from tenro.capabilities.types import DeclaredHost

        declared_host = DeclaredHost(host=host, agent_name=agent_name)
        GlobalDeclaredRegistry.register_host(declared_host)

    def scenario(self, name: str) -> AbstractContextManager[None]:
        """Context manager for test scenario attribution.

        Groups tool calls under a named scenario for coverage reporting.

        Args:
            name: Scenario name.

        Returns:
            Context manager.

        Examples:
            >>> with construct.scenario("happy_path"):
            ...     construct.simulate_tool("search", result="found")
            ...     agent.run()
        """
        from tenro.capabilities.scenario import scenario as scenario_ctx

        return scenario_ctx(name)

    def build_coverage_report(self) -> Any:
        """Build CapabilityReport from current state.

        Returns:
            CapabilityReport with declared, executed, and security data.
        """
        from tenro.capabilities.global_registry import GlobalDeclaredRegistry
        from tenro.capabilities.reporting import build_report
        from tenro.capabilities.types import ObservabilityScope

        snapshot = GlobalDeclaredRegistry.snapshot()

        executed_tools = self._collect_executed_tools(snapshot.tools)
        observed_hosts = self._collect_observed_hosts()

        return build_report(
            observability=ObservabilityScope(sources=["spans"]),
            declared_tools=snapshot.tools,
            executed_tools=executed_tools,
            declared_hosts=snapshot.hosts,
            observed_hosts=observed_hosts,
        )

    def _collect_executed_tools(self, declared_tools: list[DeclaredTool]) -> list[ExecutedTool]:
        """Collect executed tools from ToolCall spans."""
        from tenro.capabilities.executed_collector import ExecutedCollector

        collector = ExecutedCollector()
        agent_names = self._build_agent_name_map()

        for tool_call in self.tool_calls:
            agent_name = (
                agent_names.get(tool_call.agent_id) if tool_call.agent_id is not None else None
            )
            declared_tool, resolution_error = self._resolve_tool(
                tool_call.tool_name, agent_name, declared_tools
            )
            canonical_id = declared_tool.canonical_id if declared_tool else None
            effective_agent = declared_tool.agent_name if declared_tool else agent_name
            scenario_path = self._get_span_scenario_path(tool_call)
            collector.record_tool_execution(
                name=tool_call.tool_name,
                canonical_id=canonical_id,
                agent_name=effective_agent,
                scenario_path=scenario_path,
                resolution_error=resolution_error,
            )

        return collector.get_executed_tools()

    def _collect_observed_hosts(self) -> list[ObservedHost]:
        """Collect observed hosts from LLM calls."""
        from urllib.parse import urlparse

        from tenro.capabilities.types import HostClassifier, ObservedHost
        from tenro.construct.http.interceptor import get_provider_endpoints

        classifier = HostClassifier()
        endpoints = get_provider_endpoints()
        observed: dict[str, ObservedHost] = {}

        for call in self.llm_calls:
            endpoint = endpoints.get(call.provider)
            if not endpoint:
                continue
            host = urlparse(endpoint).netloc
            if not host:
                continue
            if host not in observed:
                observed[host] = ObservedHost(host=host, kind=classifier.classify(host))
            observed[host].request_count += 1

        return list(observed.values())

    def _build_agent_name_map(self) -> dict[str, str]:
        """Map agent span IDs to agent names."""
        return {agent.id: agent.name for agent in self.agent_runs}

    def _resolve_tool(
        self,
        name: str,
        agent_name: str | None,
        declared_tools: list[DeclaredTool],
    ) -> tuple[DeclaredTool | None, ResolutionError]:
        """Resolve a tool name to a declared tool."""
        matches = [tool for tool in declared_tools if tool.name == name or name in tool.aliases]
        if agent_name:
            agent_matches = [tool for tool in matches if tool.agent_name == agent_name]
            matches = agent_matches or [tool for tool in matches if tool.agent_name is None]
        else:
            matches = [tool for tool in matches if tool.agent_name is None]

        if not matches:
            return None, "not_found"
        if len(matches) > 1:
            return None, "ambiguous"
        return matches[0], None

    def _get_span_scenario_path(self, span: ToolCall) -> list[str] | None:
        """Extract scenario path from span metadata."""
        raw = span.metadata.get("scenario_path")
        if isinstance(raw, list) and all(isinstance(item, str) for item in raw):
            return raw
        return None

    def print_coverage(self) -> None:
        """Print coverage report to console.

        Shows declared vs executed tools with coverage percentages.
        """
        from tenro.capabilities.renderer import CapabilityRenderer

        report = self.build_coverage_report()
        renderer = CapabilityRenderer()
        renderer.render(report)

    def _get_exporter(self, output_dir: Any | None, worker_id: str | None) -> tuple[Any, Any]:
        """Build report and exporter for capability export."""
        from pathlib import Path

        from tenro.capabilities.exporter import ArtifactExporter

        report = self.build_coverage_report()
        exporter = ArtifactExporter(
            output_dir=Path(output_dir) if output_dir else None,
            worker_id=worker_id,
        )
        return report, exporter

    def export_capabilities(
        self,
        output_dir: Any | None = None,
        worker_id: str | None = None,
    ) -> Any:
        """Export capability report to JSON file.

        Args:
            output_dir: Directory for output. Default: .tenro/artifacts/
            worker_id: pytest-xdist worker ID for suffixing.

        Returns:
            Path to exported file.
        """
        report, exporter = self._get_exporter(output_dir, worker_id)
        return exporter.export_capabilities(report)

    def export_coverage(
        self,
        output_dir: Any | None = None,
        worker_id: str | None = None,
    ) -> Any:
        """Export coverage report to JSON file.

        Args:
            output_dir: Directory for output. Default: .tenro/artifacts/
            worker_id: pytest-xdist worker ID for suffixing.

        Returns:
            Path to exported file.
        """
        report, exporter = self._get_exporter(output_dir, worker_id)
        return exporter.export_coverage(report)
