# deepseek-free

<p>
  <a href="https://t.me/pythontodayz">
    <img src="https://img.shields.io/badge/Telegram-pythontodayz-2CA5E0?logo=telegram&logoColor=white&style=for-the-badge" alt="Telegram Channel"/>
  </a>
  <img src="https://img.shields.io/pypi/v/deepseek-free?style=for-the-badge" alt="PyPI Version"/>
  <img src="https://img.shields.io/pypi/pyversions/deepseek-free?style=for-the-badge" alt="Python Versions"/>
  <img src="https://img.shields.io/github/license/addy/deepseek-free?style=for-the-badge" alt="License"/>
</p>

Unofficial Python client for DeepSeek. Supports default and expert models with thinking and web search — no special API needed, just your DeepSeek auth token.

---

## Installation

```bash
pip install deepseek-free
```

---

## Getting Your API Key

1. Open [chat.deepseek.com](https://chat.deepseek.com) in your browser
2. Open **DevTools** → **Network** tab
3. Send any message and find a request to `chat.deepseek.com`
4. Copy the `authorization` header value (starts with `Bearer ...`)

---

## Quick Start

```python
from deepseek import DeepSeekClient

client = DeepSeekClient(api_key="Bearer YOUR_TOKEN_HERE")

response = client.chat("What is the capital of France?")
print(response.response)
```

---

## Models

| Model | Description |
|-------|-------------|
| `default` | Standard DeepSeek model — fast, general purpose |
| `expert` | Expert model — deeper reasoning, more detailed answers |

---

## Feature Flags

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `model` | `str` | `"default"` | Model to use: `"default"` or `"expert"` |
| `thinking` | `bool` | `False` | Enable chain-of-thought reasoning |
| `search` | `bool` | `False` | Enable live web search |
| `session_id` | `str` | `None` | Reuse an existing chat session |

---

## Usage Examples

### Basic — default model

```python
from deepseek import DeepSeekClient

client = DeepSeekClient(api_key="Bearer YOUR_TOKEN_HERE")

response = client.chat("Explain quantum computing")
print(response.response)
```

### Expert model

```python
response = client.chat(
    "Solve this integral: ∫x²dx",
    model="expert"
)
print(response.response)
```

### Thinking enabled

```python
response = client.chat(
    "What is 17 * 23?",
    thinking=True
)
print(response.response)

if response.thinking_content:
    print("\n--- Thinking ---")
    print(response.thinking_content)
```

### Web search enabled

```python
response = client.chat(
    "What happened in the news today?",
    search=True
)
print(response.response)
```

### Expert + thinking

```python
response = client.chat(
    "Prove that sqrt(2) is irrational",
    model="expert",
    thinking=True
)
print(response.response)
```

### Expert + web search

```python
response = client.chat(
    "Latest AI research papers in 2025",
    model="expert",
    search=True
)
print(response.response)
```

### Default + thinking + web search

```python
response = client.chat(
    "What is today's weather in Mumbai?",
    thinking=True,
    search=True
)
print(response.response)
```

### Expert + thinking + web search (all enabled)

```python
response = client.chat(
    "Analyze the current state of AI regulation globally",
    model="expert",
    thinking=True,
    search=True
)
print(response.response)

if response.thinking_content:
    print("\n--- Thinking Process ---")
    print(response.thinking_content)
```

### Continue a conversation (reuse session)

```python
response1 = client.chat("My name is Alex")
session_id = response1.session_id

response2 = client.chat("What is my name?", session_id=session_id)
print(response2.response)
```

---

## Response Object

Every `client.chat()` call returns a `ChatResponse`:

| Field | Type | Description |
|-------|------|-------------|
| `response` | `str` | The model's reply (clean plain text) |
| `thinking_content` | `str \| None` | Chain-of-thought (only when `thinking=True`) |
| `session_id` | `str` | Session ID — use to continue conversations |
| `message_id` | `int` | Message ID in the session |
| `model_type` | `str` | Model used (`default` or `expert`) |
| `thinking_enabled` | `bool` | Whether thinking was enabled |
| `search_enabled` | `bool` | Whether web search was enabled |
| `status` | `str` | Response status from DeepSeek |

---

## Notes

- Your auth token expires periodically — refresh it from DevTools if you get auth errors
- Web search adds live data but may slightly increase response time
- Thinking mode shows the model's internal reasoning process
- Responses are automatically cleaned — no HTML tags or citation markers

---

## License

MIT — made by [addy](https://t.me/pythontodayz)
