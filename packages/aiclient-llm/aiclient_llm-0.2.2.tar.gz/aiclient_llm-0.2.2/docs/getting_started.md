# Getting Started with aiclient-llm

`aiclient-llm` is a unified, minimalist Python client for modern LLMs. It standardizes interactions across OpenAI, Anthropic, Google Gemini, xAI, and local models (Ollama).

## Installation

```bash
pip install aiclient-llm
```

## Configuration

The client automatically loads API keys from environment variables or a `.env` file in your working directory.

### 1. Create `.env`

```ini
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=AI...
XAI_API_KEY=xai-...
```

### 2. Instantiate Client

```python
from aiclient import Client

# Loads from .env automatically
client = Client()

# Or pass keys explicitly
client = Client(openai_api_key="your-key")
```

## Basic Usage

### Text Generation

```python
# OpenAI
print(client.chat("gpt-4o").generate("Hello!").text)

# Claude
print(client.chat("claude-3-opus-20240229").generate("Hello!").text)

# Gemini
print(client.chat("gemini-1.5-pro").generate("Hello!").text)
```

### Streaming

Stream responses for a better user experience:

```python
for chunk in client.chat("gpt-4o").stream("Write a long story"):
    print(chunk.text, end="", flush=True)
```

### Async Support

For high-performance applications (like FastAPI), use `_async` methods:

```python
import asyncio

async def main():
    response = await client.chat("gpt-4o").generate_async("Hello")
    print(response.text)

asyncio.run(main())
```
