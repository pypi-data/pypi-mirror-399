# Tenro Examples

Runnable examples showing how to test AI agents with Tenro.

## API Keys

> ⚠️ Some frameworks validate API keys at import. Set the key for your provider before running:
> `export OPENAI_API_KEY={YOUR_KEY}` or `export ANTHROPIC_API_KEY={YOUR_KEY}`
>
> Tests use simulated responses—any non-empty value works. Never commit real keys.

## Running Examples

**SDK users** (pip install tenro):
```bash
# Install your framework
pip install tenro crewai  # or langchain, pydantic-ai, etc.

# Copy an example and run
python examples/crewai/test_crewai_customer_support.py
```

**Development** (this repo):
```bash
uv sync --group examples
uv run pytest examples/
```

## Structure

| Section | Purpose | User Question |
|---------|---------|---------------|
| **langchain/** | LangChain chains/agents | "How do I test my LangChain agent?" |
| **langgraph/** | LangGraph stateful workflows | "How do I test my LangGraph?" |
| **pydantic_ai/** | Pydantic AI agents | "How do I test Pydantic AI?" |
| **crewai/** | CrewAI multi-agent crews | "How do I test my CrewAI crew?" |
| **autogen/** | AutoGen conversations | "How do I test AutoGen agents?" |
| **llamaindex/** | LlamaIndex RAG pipelines | "How do I test LlamaIndex?" |
| **patterns/** | API feature demos | "How do I inject errors?" |
| **custom/** | Raw agent code (no framework) | "I built my own agent" |

---

## langchain/

LangChain integration examples.

- **test_simple_chain.py** — Basic chain with prompt template + LLM
- **test_rag_chain.py** — Retrieval-augmented generation with document search

---

## langgraph/

LangGraph stateful workflow examples.

- **test_simple_graph.py** — Basic stateful graph with one node
- **test_multistep_workflow.py** — Multi-step workflow with conditional routing

---

## pydantic_ai/

Pydantic AI integration examples.

- **test_simple_agent.py** — Basic Pydantic AI agent
- **test_agent_with_tools.py** — Agent with tool calling

---

## crewai/

CrewAI multi-agent examples.

- **test_simple_crew.py** — Single agent crew
- **test_multi_agent_crew.py** — Researcher + writer collaboration

---

## autogen/

AutoGen conversation examples.

- **test_simple_agent.py** — Basic assistant agent
- **test_conversation.py** — Multi-turn conversation

---

## llamaindex/

LlamaIndex RAG examples.

- **test_simple_query.py** — Basic query engine
- **test_rag_pipeline.py** — RAG pipeline with document fetching

---

## patterns/

API feature demonstrations - learn what Tenro can do.

- **test_simulating_responses.py** — Control tool/LLM returns with `result=`, `results=[]`, `responses=[]`
- **test_injecting_errors.py** — Test error handling with exceptions in results
- **test_verifying_calls.py** — Assert call counts with `times=`, `min=`, `max=`, `count=`
- **test_verifying_content.py** — Check LLM responses with `output_contains=`, `call_index=`
- **test_verifying_never_called.py** — Ensure operations didn't happen with `verify_*_never()`
- **test_verifying_call_sequence.py** — Verify execution order with `verify_*_sequence()`
- **test_optional_simulations.py** — Handle conditional branches with `optional=True`
- **test_dynamic_behavior.py** — Input-dependent responses with `side_effect=`
- **test_tool_call_formats.py** — Simplified, medium, and full tool call formats

---

## custom/

Raw agent examples without frameworks - for custom agent implementations.

- **test_customer_support_agent.py** — Knowledge base search + LLM response
- **test_email_summarizer_agent.py** — Fetch emails + summarize
- **test_research_assistant_agent.py** — Web search + synthesize findings
- **test_sales_outreach_agent.py** — CRM lookup + pricing + generate pitch
- **test_code_review_agent.py** — Fetch PR diff + analyze + post comment
- **test_meeting_notes_agent.py** — Transcribe + extract action items
- **test_voice_call_agent.py** — Speech-to-text + LLM + text-to-speech
- **test_rag_document_agent.py** — Vector search + retrieval + summarize
- **test_recruitment_agent.py** — Screen candidates + schedule interviews
