# p2d-deepseek

<p>
  <a href="https://t.me/pythontodayz">
    <img src="https://img.shields.io/badge/Telegram-pythontodayz-2CA5E0?logo=telegram&logoColor=white&style=for-the-badge" alt="Telegram Channel"/>
  </a>
  <img src="https://img.shields.io/pypi/v/p2d-deepseek?style=for-the-badge" alt="PyPI Version"/>
  <img src="https://img.shields.io/pypi/pyversions/p2d-deepseek?style=for-the-badge" alt="Python Versions"/>
  <img src="https://img.shields.io/github/license/pooraddyy/deepseek-free?style=for-the-badge" alt="License"/>
</p>

Unofficial Python client for DeepSeek. Supports default and expert models with thinking and web search — no special API needed, just your DeepSeek auth token.

---

## Installation

**Using pip (recommended):**

```bash
pip install p2d-deepseek
```

**Upgrade to latest version:**

```bash
pip install p2d-deepseek --upgrade
```

**Install specific version:**

```bash
pip install p2d-deepseek==0.1.6
```

> **Note:** The PyPI package is named `p2d-deepseek` but the Python import name is `deepseek`.
> Install with `pip install p2d-deepseek`, then use `from deepseek import DeepSeekClient` in your code.

---

## Getting Your Auth Token

To use this package, you need your DeepSeek auth token. Choose whichever method suits you best.

---

### Method 1 — LocalStorage (Fastest, Desktop)

This is the quickest way if you are on a desktop browser.

1. Go to [chat.deepseek.com](https://chat.deepseek.com) and log in
2. Open DevTools — press `F12` or right-click anywhere → **Inspect**
3. Go to the **Application** tab (if hidden, click `»` to find it)
4. In the left sidebar, expand **Local Storage** → click `https://chat.deepseek.com`
5. Find the key called `userToken`
6. Copy the **value** field — that is your token

---

### Method 2 — Network Tab (Desktop)

Use this if the LocalStorage method does not work for you.

1. Go to [chat.deepseek.com](https://chat.deepseek.com) and log in
2. Open DevTools → **Network** tab
3. Send any message in the chat
4. Click on any request going to `chat.deepseek.com`
5. Open the **Headers** section
6. Find the `authorization` header and copy its value (without the `Bearer ` prefix)

---

### Method 3 — Kiwi Browser (Android / Mobile)

Mobile users can extract the token using **Kiwi Browser**, which supports DevTools.

1. Install [Kiwi Browser](https://play.google.com/store/apps/details?id=com.kiwibrowser.browser) from the Play Store
2. Open [chat.deepseek.com](https://chat.deepseek.com) and log in
3. Tap the menu (⋮) → **Developer Tools**
4. Go to the **Application** tab → **Local Storage** → `https://chat.deepseek.com`
5. Find the key called `userToken` and copy the **value** field

> **Note:** Kiwi Browser is only available on Android. iPhone users can use a laptop or PC with any of the desktop methods above.

---

### Cloudflare Issues

If you see a **"Just a moment..."** page or requests are being blocked, DeepSeek has triggered a Cloudflare challenge. In this case:

- Try logging out and back in on [chat.deepseek.com](https://chat.deepseek.com)
- Wait a few minutes, then grab a fresh token
- If the problem keeps happening, switch to a different network (e.g. mobile data vs Wi-Fi)
- Avoid making too many requests in a short time — space them out to stay under the radar

> Your token is tied to your session. If DeepSeek logs you out or your session expires, just repeat any of the steps above to get a fresh one.

---

## Quick Start

```python
from deepseek import DeepSeekClient

client = DeepSeekClient(api_key="YOUR_TOKEN_HERE")

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

client = DeepSeekClient(api_key="YOUR_TOKEN_HERE")

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

- Tokens expire when your DeepSeek session ends — refresh using any method above
- Web search slightly increases response time but adds real-time data
- Thinking mode exposes the model's internal reasoning before the final answer
- All responses are automatically stripped of HTML tags and citation markers

---

## License

MIT — made by [addy](https://t.me/pythontodayz)
