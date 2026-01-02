# miu-core

Core framework library for miu AI agent.

## Installation

```bash
uv add miu-core
```

With LLM providers:

```bash
uv add miu-core[anthropic]  # Anthropic Claude
uv add miu-core[openai]     # OpenAI
uv add miu-core[google]     # Google Gemini
uv add miu-core[all]        # All providers
```

## Usage

```python
from miu_core.providers import AnthropicProvider
from miu_core.agents import ReActAgent

provider = AnthropicProvider()
agent = ReActAgent(provider=provider)
response = await agent.run("Hello!")
```
