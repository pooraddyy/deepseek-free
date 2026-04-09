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
pip install p2d-deepseek==0.1.8
```

> **Note:** The PyPI package is named `p2d-deepseek` but the Python import name is `deepseek`.
> Install with `pip install p2d-deepseek`, then use `from deepseek import DeepSeekClient` in your code.

---

## Getting Your Auth Token

To use this package, you need your DeepSeek auth token. Choose whichever method suits you best.

---

### Method 1 — LocalStorage (Fastest, Desktop)

1. Go to [chat.deepseek.com](https://chat.deepseek.com) and log in
2. Open DevTools — press `F12` or right-click anywhere → **Inspect**
3. Go to the **Application** tab (if hidden, click `»` to find it)
4. In the left sidebar, expand **Local Storage** → click `https://chat.deepseek.com`
5. Find the key called `userToken`
6. Copy the **value** field — that is your token

---

### Method 2 — Network Tab (Desktop)

1. Go to [chat.deepseek.com](https://chat.deepseek.com) and log in
2. Open DevTools → **Network** tab
3. Send any message in the chat
4. Click on any request going to `chat.deepseek.com`
5. Open the **Headers** section
6. Find the `authorization` header and copy its value (without the `Bearer ` prefix)

---

### Method 3 — Kiwi Browser (Android / Mobile)

1. Install [Kiwi Browser](https://play.google.com/store/apps/details?id=com.kiwibrowser.browser) from the Play Store
2. Open [chat.deepseek.com](https://chat.deepseek.com) and log in
3. Tap the menu (⋮) → **Developer Tools**
4. Go to the **Application** tab → **Local Storage** → `https://chat.deepseek.com`
5. Find the key called `userToken` and copy the **value** field

> **Note:** Kiwi Browser is only available on Android. iPhone users can use a laptop or PC with any of the desktop methods above.

---

### Cloudflare Issues

If you see a **"Just a moment..."** page or requests are being blocked:

- Try logging out and back in on [chat.deepseek.com](https://chat.deepseek.com)
- Wait a few minutes, then grab a fresh token
- If the problem keeps happening, switch to a different network (e.g. mobile data vs Wi-Fi)
- Avoid making too many requests in a short time

> Your token is tied to your session. If DeepSeek logs you out or your session expires, repeat any of the steps above to get a fresh one.

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

## Response Fields

Every `client.chat()` call returns a `ChatResponse` object with these fields:

| Field | Type | Description |
|-------|------|-------------|
| `response` | `str` | Clean final answer from the model |
| `thinking_content` | `str \| None` | Raw thinking process (only when `thinking=True`, else `None`) |
| `full_response` | `str` | **Thinking first + answer below** — use this in bots when thinking is enabled |
| `answer` | `str` | Same as `response` — clean final answer only |
| `session_id` | `str` | Session ID — use to continue conversations |
| `message_id` | `int` | Message ID in the session |
| `model_type` | `str` | Model used (`default` or `expert`) |
| `thinking_enabled` | `bool` | Whether thinking was enabled |
| `search_enabled` | `bool` | Whether web search was enabled |
| `status` | `str` | Response status from DeepSeek |

---

## Thinking Mode — Important

When `thinking=True`, the model shows its internal reasoning before giving the final answer.

### Which field to use?

```python
response = client.chat("What is 17 * 23?", thinking=True)

response.response          # "391"  ← just the clean answer
response.thinking_content  # "We need to compute 17 * 23..."  ← just the thinking
response.full_response     # thinking first + answer below (combined in one string)
```

### In a bot — always use `full_response`

```python
response = client.chat(user_message, thinking=True)

# WRONG — sends two separate messages, thinking appears twice
await message.reply(response.response)
await message.reply(response.thinking_content)

# CORRECT — one message, thinking first, answer below
await message.reply(response.full_response)
```

### Without thinking — use `full_response`

`full_response` works correctly whether thinking is on or off — always use it in bots.

```python
response = client.chat(user_message)  # thinking=False by default

# WRONG — response.response works but is inconsistent; breaks if you later enable thinking
await message.reply(response.response)

# CORRECT — full_response returns just the clean answer when thinking=False
await message.reply(response.full_response)
```

### `full_response` when thinking is disabled

If `thinking=False`, `full_response` returns the same thing as `response` — no thinking content, just the clean answer. So you can safely always use `full_response` and it will work correctly in both cases.

```python
# Works correctly whether thinking=True or thinking=False
await message.reply(response.full_response)
```

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

print(response.full_response)
# Output:
# We need to compute 17 * 23. 17*20=340, 17*3=51, total is 391.
#
# 17 multiplied by 23 equals 391.
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
print(response.full_response)
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
print(response.full_response)
```

### Expert + thinking + web search (all enabled)

```python
response = client.chat(
    "Analyze the current state of AI regulation globally",
    model="expert",
    thinking=True,
    search=True
)
print(response.full_response)
```

### Continue a conversation (reuse session)

```python
response1 = client.chat("My name is Alex")
session_id = response1.session_id

response2 = client.chat("What is my name?", session_id=session_id)
print(response2.response)
```

---

## Error Handling

```python
from deepseek import DeepSeekClient, DeepSeekConnectionError, DeepSeekAPIError

client = DeepSeekClient(api_key="YOUR_TOKEN_HERE")

try:
    response = client.chat("Hello!")
    print(response.response)
except DeepSeekConnectionError as e:
    print(f"Connection failed: {e}")
except DeepSeekAPIError as e:
    print(f"API error: {e}")
```

| Exception | When it happens |
|-----------|----------------|
| `DeepSeekConnectionError` | Cannot connect to DeepSeek (network issue) |
| `DeepSeekAPIError` | Token expired/invalid, or DeepSeek returned an error |

---

## Demo Script

Save this as `demo.py` and run it with your token:

```python
from deepseek import DeepSeekClient, DeepSeekConnectionError, DeepSeekAPIError

TOKEN = "YOUR_TOKEN_HERE"

client = DeepSeekClient(api_key=TOKEN)

print("=" * 50)
print("Test 1: Basic chat")
print("=" * 50)
r = client.chat("Say hello in 5 different languages")
print(r.response)
print()

print("=" * 50)
print("Test 2: Thinking mode")
print("=" * 50)
r = client.chat("What is 17 * 23?", thinking=True)
print("-- Thinking --")
print(r.thinking_content)
print()
print("-- Answer --")
print(r.response)
print()
print("-- full_response (use this in bots) --")
print(r.full_response)
print()

print("=" * 50)
print("Test 3: Web search")
print("=" * 50)
r = client.chat("What is today's date?", search=True)
print(r.response)
print()

print("=" * 50)
print("Test 4: Expert model")
print("=" * 50)
r = client.chat("What is the square root of 144?", model="expert")
print(r.response)
print()

print("=" * 50)
print("Test 5: Session continuity")
print("=" * 50)
r1 = client.chat("My name is Alex")
r2 = client.chat("What is my name?", session_id=r1.session_id)
print(r2.response)
print()

print("=" * 50)
print("Test 6: Error handling")
print("=" * 50)
bad_client = DeepSeekClient(api_key="invalid_token")
try:
    bad_client.chat("Hello")
except DeepSeekAPIError as e:
    print(f"Caught error correctly: {e}")
```

---

## Telegram Bot Example

```python
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from deepseek import DeepSeekClient, DeepSeekConnectionError, DeepSeekAPIError

TOKEN = "YOUR_DEEPSEEK_TOKEN"
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"

client = DeepSeekClient(api_key=TOKEN)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    def run():
        return client.chat(user_message, thinking=True)

    try:
        response = await asyncio.to_thread(run)
        await update.message.reply_text(response.full_response)
    except DeepSeekConnectionError:
        await update.message.reply_text("Connection error, please try again.")
    except DeepSeekAPIError as e:
        await update.message.reply_text(f"Error: {e}")


app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.run_polling()
```

---

## Notes

- Tokens expire when your DeepSeek session ends — refresh using any method above
- Web search slightly increases response time but adds real-time data
- Thinking mode exposes the model's internal reasoning before the final answer
- All responses are automatically stripped of HTML tags and citation markers
- Always use `response.full_response` in bots — it works correctly whether thinking is enabled or not, and avoids duplicate messages

---

## License

MIT — made by [addy](https://t.me/pythontodayz)
