
# 🐪 Camel-py

A lightweight Python client for [Ollama](https://ollama.ai/) with built-in agentic capabilities and tool calling support.

---

## 🚀 Installation

```bash
pip install camel-py
```


## ⚡ Quickstart

### Basic Chat
```python
from camel import CamelClient

with CamelClient(model="llama3") as client:
    resp = client.chat("Hello, who are you?")
    print(resp.text)
    
    # Streaming
    print("Assistant: ", end="")
    client.stream("Tell me a joke about camels")
```

### AI Agent with Tool Calling
```python
from camel import CamelClient, Agent, Tool

def get_weather(location: str) -> str:
    return f"Weather in {location}: 72°F, sunny"

weather_tool = Tool(
    name="get_weather",
    description="Gets current weather for any location",
    schema={
        "type": "object",
        "properties": {
            "location": {"type": "string", "description": "City name"}
        },
        "required": ["location"]
    },
    function=get_weather
)

client = CamelClient(model="llama3")
agent = Agent(client, tools=[weather_tool])

result = agent.run("What's the weather in Paris?")
print(result)
```

## 🔧 Features

- **AI Agents**: Built-in tool calling via FunctionGemma (auto-installed)
- **Dual-model architecture**: Specialized tool detection + your choice for responses
- **Streaming**: Real-time token streaming
- **Context management**: Save/load/clear conversation history
- **Model management**: List, pull, delete Ollama models
- **Embeddings**: Generate text embeddings

## 📂 Examples

- [examples/agent.py](examples/agent.py) → AI agent with tool calling
- [examples/adv_chat.py](examples/adv_chat.py) → Context persistence

## 🛠️ How It Works

The Agent uses a two-model approach:
1. **FunctionGemma** detects when tools are needed
2. **Your chosen model** generates natural responses

This provides reliable tool calling while maintaining conversation quality.

## 📦 Requirements

- Python ≥3.12
- Ollama running locally
