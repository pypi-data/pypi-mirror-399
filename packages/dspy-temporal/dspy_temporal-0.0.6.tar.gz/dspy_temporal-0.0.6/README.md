# DSPy-Temporal

**Durable execution for DSPy programs using Temporal workflows**

[![PyPI version](https://img.shields.io/pypi/v/dspy-temporal.svg)](https://pypi.org/project/dspy-temporal/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## What is This?

DSPy-Temporal enables **durable, fault-tolerant execution** of [DSPy](https://github.com/stanfordnlp/dspy) AI programs using [Temporal](https://temporal.io). When your long-running AI workflows fail midway, they automatically resume from the last checkpoint—saving time, money, and computational resources.

### The Problem

Without durable execution, DSPy programs that make LLM calls are vulnerable to failures:

- **All progress is lost** when a failure occurs partway through
- **Expensive LLM calls must be repeated** from scratch
- **No automatic recovery** from network issues, rate limits, or API outages

### The Solution

Wrap your DSPy modules with `TemporalModule` to get:

- ✅ **Automatic checkpointing** after each LLM call
- ✅ **Fault tolerance** - workflows resume from last successful step
- ✅ **Automatic retries** with exponential backoff
- ✅ **Observability** through Temporal's built-in monitoring

## Related Technologies

- **[Pydantic AI Temporal Integration](https://ai.pydantic.dev/durable_execution/temporal/)** - Similar integration for Pydantic AI (inspiration for this library)
- **[LangGraph Durable Execution](https://langchain-ai.github.io/langgraph/concepts/persistence/)** - LangGraph's approach to durable execution

## Installation

```bash
# Install from PyPI
pip install dspy-temporal

# Or with uv
uv add dspy-temporal
```

### Development Installation

```bash
# Install from source
git clone https://github.com/bdsaglam/dspy-temporal.git
cd dspy-temporal
uv sync --dev
```

### Requirements

- Python 3.11+
- A running [Temporal server](https://docs.temporal.io/cli/#start-dev-server)

```bash
# Quick start with Docker Compose
docker-compose up -d
```

## Quick Start

### 1. Define Tools

```python
import os
import dspy
from tavily import TavilyClient

def search_web(query: str) -> str:
    """Search the web using Tavily API."""
    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    response = client.search(query=query, max_results=3)
    results = response.get("results", [])

    passages = []
    for r in results:
        passages.append(f"{r['title']}\n{r['content']}\nSource: {r['url']}")
    return "\n\n".join(passages)

def evaluate_math(expression: str) -> str:
    """Safely evaluate a math expression."""
    return str(eval(expression, {"__builtins__": {}}, {}))
```

### 2. Create ReAct Agent

```python
from dspy_temporal import TemporalModule

# Create agent with tools
react_agent = dspy.ReAct(
    "question -> answer",
    tools=[evaluate_math, search_web],
)

# Wrap for Temporal (tools are automatically wrapped as activities)
temporal_agent = TemporalModule(react_agent, name="react_agent")
```

### 3. Define Workflow

```python
from temporalio import workflow

@workflow.defn
class ReActWorkflow:
    @workflow.run
    async def run(self, question: str) -> str:
        result = await temporal_agent.run(question=question)
        return result.answer
```

### 4. Execute

```python
import asyncio
from temporalio.client import Client
from temporalio.worker import Worker
from dspy_temporal import DSPyPlugin
from dspy_temporal.sandbox import get_default_sandbox_runner

async def main():
    # Configure DSPy
    dspy.configure(lm=dspy.LM("openai/gpt-5-mini"))

    # Connect to Temporal
    client = await Client.connect("localhost:7233")

    # Run worker with workflow
    async with Worker(
        client,
        task_queue="react-queue",
        workflows=[ReActWorkflow],
        plugins=[DSPyPlugin(temporal_agent)],
        workflow_runner=get_default_sandbox_runner(),
    ):
        result = await client.execute_workflow(
            ReActWorkflow.run,
            args=["What is the population of Tokyo and how much to buy coffee for everyone at $3.50?"],
            id="react-001",
            task_queue="react-queue",
        )
        print(result)

asyncio.run(main())
```

**What happens:**
1. Agent searches web for population data → **Temporal Activity** (checkpointed)
2. Agent calculates cost (population × price) → **Temporal Activity** (checkpointed)
3. Agent synthesizes final answer → **Temporal Activity** (checkpointed)

If the workflow fails at any point, Temporal automatically resumes from the last completed activity—no repeated API costs or lost progress.

### Temporal Dashboard View

Here's what the execution looks like in the Temporal UI, showing each LLM call and tool execution as separate activities with automatic checkpointing:

![ReAct Agent Execution Timeline](docs/images/react-agent.png)

Each activity (`dspy__react_agent__react__lm_call` for reasoning, `dspy__tool__search_web` for web search) is:
- ✅ **Automatically retried** on failure
- ✅ **Checkpointed** after completion
- ✅ **Observable** in the Temporal UI
- ✅ **Recoverable** if the workflow crashes

## Production Usage

In production environments, you typically run a dedicated worker process that continuously polls for workflow tasks, while your application (web server, CLI, etc.) starts workflows as needed.

### Worker Process (`worker.py`)

The worker runs continuously and executes workflows and activities:

```python
"""
Temporal worker for DSPy workflows.
Run this process continuously in production to execute workflows.
"""
import asyncio
import logging
import dspy
from temporalio.client import Client
from temporalio.worker import Worker
from dspy_temporal import TemporalModule, DSPyPlugin
from dspy_temporal.sandbox import get_default_sandbox_runner

from myapp.workflows import RAGWorkflow, AgentWorkflow
from myapp.modules import create_rag_module, create_agent_module

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Start the Temporal worker."""
    # Configure DSPy with your LM
    dspy.configure(lm=dspy.LM("openai/gpt-5-mini"))

    # Create and wrap your DSPy modules
    rag_module = create_rag_module()
    agent_module = create_agent_module()

    temporal_rag = TemporalModule(rag_module, name="rag")
    temporal_agent = TemporalModule(agent_module, name="agent")

    # Connect to Temporal server
    client = await Client.connect("localhost:7233")

    # Create worker with all workflows and activities
    worker = Worker(
        client,
        task_queue="dspy-queue",
        workflows=[RAGWorkflow, AgentWorkflow],
        plugins=[DSPyPlugin(temporal_rag, temporal_agent)],  # Single plugin with all modules
        workflow_runner=get_default_sandbox_runner(),
        max_concurrent_activities=20,
        max_concurrent_workflow_tasks=10,
    )

    logger.info("🚀 Starting DSPy Temporal worker")
    logger.info("📋 Task queue: dspy-queue")
    logger.info(f"🔄 Workflows: {len(worker._workflows)}")

    # Run worker (blocks until interrupted)
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
```

Start the worker:

```bash
python worker.py
```

### Application Process (`app.py`)

Your application starts workflows when needed:

```python
"""
Application that starts DSPy workflows via Temporal.
This could be a web server, CLI tool, or any other application.
"""
import asyncio
from temporalio.client import Client

async def process_query(question: str) -> str:
    """Process a user query using the RAG workflow."""
    # Connect to Temporal
    client = await Client.connect("localhost:7233")

    # Start workflow execution
    result = await client.execute_workflow(
        "RAGWorkflow",  # Workflow name
        args=[question],
        id=f"rag-{question[:20]}",
        task_queue="dspy-queue",
    )

    return result

async def main():
    # Example: Process multiple queries
    questions = [
        "What is durable execution?",
        "How does Temporal work?",
        "What are DSPy modules?"
    ]

    for question in questions:
        answer = await process_query(question)
        print(f"Q: {question}")
        print(f"A: {answer}\n")

if __name__ == "__main__":
    asyncio.run(main())
```

### Architecture Overview

```
┌─────────────────────┐         ┌──────────────────────┐
│   Application       │         │   Temporal Server    │
│   (app.py)          │────────▶│   (localhost:7233)   │
│                     │ Start   │                      │
│ - Web Server        │ Workflow│                      │
│ - CLI Tool          │         │                      │
│ - Background Job    │         │                      │
└─────────────────────┘         └──────────────────────┘
                                          │
                                          │ Task Queue
                                          │ "dspy-queue"
                                          ▼
                                ┌──────────────────────┐
                                │   Worker Process     │
                                │   (worker.py)        │
                                │                      │
                                │ - Executes Workflows │
                                │ - Runs Activities    │
                                │ - Handles Retries    │
                                └──────────────────────┘
```

**Key Points:**

- **Worker Process**: Runs continuously, polls for tasks, executes workflows/activities
- **Application Process**: Starts workflows on-demand, doesn't block on execution
- **Temporal Server**: Coordinates between application and worker, stores workflow state
- **Task Queue**: Named channel that routes workflow tasks to appropriate workers

### Deployment Considerations

1. **Worker Scaling**: Run multiple worker instances for higher throughput
2. **Health Checks**: Monitor worker health and restart if needed
3. **Graceful Shutdown**: Handle SIGTERM to finish in-flight activities
4. **Resource Limits**: Configure `max_concurrent_activities` based on your infrastructure
5. **Observability**: Use Temporal UI to monitor workflows and debug issues

For a complete production example with health checks and proper error handling, see [examples/production/](examples/production/).

## Examples

See the [examples/](examples/) directory for complete working examples:

- **[react_agent.py](examples/react_agent.py)** - ⭐ **Featured**: ReAct agent with real web search (Tavily) and math tools
- **[simple_rag.py](examples/simple_rag.py)** - RAG pipeline with web search retrieval
- **[multihop_rag.py](examples/multihop_rag.py)** - Multi-hop retrieval with iterative search
- **[multitool_agent.py](examples/multitool_agent.py)** - Agent orchestrating multiple specialized tools

Each example includes setup instructions and demonstrates different DSPy patterns. The **react_agent.py** example is featured in the Quick Start above.

## How It Works

DSPy-Temporal intercepts LLM calls and tool executions, routing them through Temporal Activities:

1. `TemporalModule` wraps your DSPy module
2. During workflow execution, LLM calls become Temporal Activities
3. Each activity result is checkpointed by Temporal
4. On failure, the workflow replays and skips already-completed activities
5. Execution resumes from the last successful checkpoint

See [docs/architecture.md](docs/architecture.md) for implementation details.

## Key Features

- **Minimal Code Changes** - Wrap existing modules with 1-2 lines
- **Per-Predictor Activity Naming** - Each predictor gets its own activity for better observability
- **Automatic Tool Wrapping** - Agent tools (ReAct, CodeAct, Avatar) become durable activities
- **Type-Safe** - Full type hints and IDE support
- **Production-Ready** - Configurable timeouts, retries, and error handling
- **Observable** - Monitor workflows through Temporal UI with clear activity names
- **Async-First** - Supports modern async Python patterns

## Important Notes

### Workflow Sandbox Requirements

⚠️ **HTTP Libraries in Passthrough**: This library requires HTTP libraries (`httpx`, `urllib3`, `openai`, `litellm`) in the Temporal workflow sandbox passthrough list due to DSPy's import structure.

**What this means:**
- These libraries are available but **must not be used** in workflow code
- All HTTP calls happen in activities (enforced by design)
- Using HTTP libraries in workflows causes non-deterministic behavior

**Why is this necessary?**

DSPy eagerly imports HTTP libraries during initialization (`dspy/__init__.py` → `dspy/utils/__init__.py` → `import requests` → `import urllib3`), even though actual LLM calls execute in activities outside the sandbox.

**Current status:**
- ✅ Safe: All HTTP calls happen in Temporal activities (outside sandbox)
- ⚠️ Limitation: HTTP libraries must be in passthrough to allow DSPy imports
- 🔄 Tracking: [DSPy Issue #8597](https://github.com/stanfordnlp/dspy/issues/8597) for upstream fix

**Proposed fix for DSPy:**

Move HTTP imports to lazy loading:
```python
# Instead of (in dspy/utils/__init__.py):
import requests

# Use lazy imports:
def download():
    import requests  # Only import when actually needed
    ...
```

This would allow DSPy to work in sandboxed environments (Temporal, Ray, Dask) without compromising safety.

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/bdsaglam/dspy-temporal.git
cd dspy-temporal

# Install with development dependencies
uv sync --dev

# Start local Temporal server
docker-compose up -d
```

### Running Tests

```bash
# Linting and formatting
just lint-check
just format-check

# Run tests
just test-unit
just test-integration
```

### Project Structure

```
dspy-temporal/
├── src/dspy_temporal/     # Library source
│   ├── module.py          # TemporalModule wrapper
│   ├── lm.py              # TemporalLM for activity-based LLM calls
│   ├── tool.py            # TemporalTool for durable tool execution
│   └── plugin.py          # DSPyPlugin for Temporal integration
├── examples/              # Usage examples
├── tests/                 # Test suite
└── docs/                  # Documentation
    ├── architecture.md    # Architecture decisions
    ├── development/       # Development documentation
```

## Contributing

Contributions are welcome! See [docs](docs/) for implementation details and guidance on contributing.

## Acknowledgments

- Inspired by [Pydantic AI's Temporal integration](https://ai.pydantic.dev/durable_execution/temporal/)
- Built on [DSPy](https://github.com/stanfordnlp/dspy) and [Temporal](https://temporal.io)
- Community request from [DSPy Issue #8597](https://github.com/stanfordnlp/dspy/issues/8597)

## License

MIT License - see [LICENSE](LICENSE) for details.

---

**Status:** Alpha - Available on [PyPI](https://pypi.org/project/dspy-temporal/). API may change. Production use at your own risk.

**Feedback:** [Open an issue](https://github.com/bdsaglam/dspy-temporal/issues)
