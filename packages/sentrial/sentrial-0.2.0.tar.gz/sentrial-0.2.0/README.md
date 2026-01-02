# Sentrial Python SDK

Complete observability platform for AI agents. Track performance, monitor KPIs, and debug agent workflows with time-travel capabilities.

## Features

- **Performance Monitoring**: Track success rates, costs, duration, and custom KPIs
- **Automatic Tracking**: Capture agent reasoning, tool calls, and state changes
- **AI-Powered Recommendations**: Get optimization suggestions based on KPI gaps
- **Custom Metrics**: Define and track business-specific metrics
- **Time Travel Debugging**: Replay and debug past agent executions
- **Framework Agnostic**: Works with LangChain, custom agents, and more
- **Visual Dashboard**: Beautiful web interface to explore agent behavior

## Installation

### From PyPI

```bash
# Standard installation
pip install sentrial

# With LangChain integration
pip install sentrial[langchain]

# All integrations
pip install sentrial[all]
```

### From GitHub

```bash
pip install git+https://github.com/neelshar/Sentrial.git#subdirectory=packages/python-sdk
```

### Local Development

```bash
cd packages/python-sdk
pip install -e .
```

## Quick Start

### Basic Usage

```python
from sentrial import SentrialClient

# Initialize client
client = SentrialClient(
    api_url="https://api.sentrial.app",  # Or your self-hosted URL
    project_id="your-project-id"
)

# Create a session
session_id = client.create_session(name="Customer Support Agent")

# Track tool calls
client.track_tool_call(
    session_id=session_id,
    tool_name="search_knowledge_base",
    tool_input={"query": "password reset"},
    tool_output={"articles": ["KB-001", "KB-002"]},
    reasoning="Searching for relevant articles"
)

# Track LLM decisions
client.track_decision(
    session_id=session_id,
    reasoning="User already tried KB solutions. Escalating to human support.",
    alternatives=["Try another KB article", "Ask for more info"],
    confidence=0.85
)

# Close session (basic)
client.close_session(session_id)
```

### Performance Monitoring

Track KPIs and custom metrics:

```python
from sentrial import SentrialClient

client = SentrialClient(
    api_url="https://api.sentrial.app",
    api_key="sentrial_live_xxx",  # Get from dashboard
    project_id="your-project-id"
)

# Create session
session_id = client.create_session(
    name="Customer Support #1234",
    agent_name="support_agent"
)

# ... agent does work ...

# Track LLM call with cost
input_tokens = 1500
output_tokens = 300
llm_cost = client.calculate_openai_cost("gpt-4", input_tokens, output_tokens)

# Complete session with performance metrics
client.complete_session(
    session_id=session_id,
    success=True,  # Did agent achieve its goal?
    estimated_cost=llm_cost,  # Total cost in USD
    custom_metrics={
        "customer_satisfaction": 4.5,  # Your custom KPIs
        "order_value": 129.99,
        "items_processed": 7,
        "resolution_time_minutes": 8.5
    }
)
```

**Benefits:**
- ✅ Automatic success rate tracking
- ✅ Cost per session monitoring
- ✅ Custom KPI dashboards
- ✅ AI-powered optimization recommendations
- ✅ Alerts when KPIs are violated

### LangChain Integration

```python
from sentrial import SentrialClient, SentrialCallbackHandler
from langchain.agents import AgentExecutor, create_react_agent

# Initialize Sentrial
client = SentrialClient(api_url="...", project_id="...")
session_id = client.create_session(name="LangChain Agent")

# Create callback handler
handler = SentrialCallbackHandler(client, session_id, verbose=True)

# Use with LangChain - automatic tracking!
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    callbacks=[handler],  # ← That's it!
    verbose=True
)

result = agent_executor.invoke({"input": "Help user with login issue"})
```

The callback handler automatically tracks:
- Agent reasoning (Chain of Thought)
- Tool calls (inputs & outputs)
- Tool errors
- Agent completion

## Examples

- [simple_agent.py](https://github.com/neelshar/Sentrial/blob/main/examples/simple_agent.py) - Basic agent tracking
- [langchain_agent.py](https://github.com/neelshar/Sentrial/blob/main/examples/langchain_agent.py) - Full LangChain integration

## Documentation

- [Getting Started](https://sentrial.app/docs/quickstart)
- [API Reference](https://sentrial.app/docs/api/auth)
- [LangChain Integration](https://sentrial.app/docs/integrations/langchain)

## Support

- Email: support@sentrial.ai
- Discord: [Join our community](https://discord.gg/sentrial)
- Issues: [GitHub Issues](https://github.com/neelshar/Sentrial/issues)

## License

MIT License - see [LICENSE](LICENSE) for details.

