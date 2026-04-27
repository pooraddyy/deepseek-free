# p2d-deepseek

<p>
  <a href="https://t.me/pythontodayz">
    <img src="https://img.shields.io/badge/Telegram-pythontodayz-2CA5E0?logo=telegram&logoColor=white&style=for-the-badge" alt="Telegram Channel"/>
  </a>
  <img src="https://img.shields.io/pypi/v/p2d-deepseek?style=for-the-badge" alt="PyPI Version"/>
  <img src="https://img.shields.io/pypi/pyversions/p2d-deepseek?style=for-the-badge" alt="Python Versions"/>
  <img src="https://img.shields.io/github/license/pooraddyy/deepseek-free?style=for-the-badge" alt="License"/>
</p>

Unofficial Python client for DeepSeek. Supports default and expert models with thinking, web search, and **file/image uploads** — no special API needed, just your DeepSeek auth token.

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
pip install p2d-deepseek==0.1.9
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
| `parent_message_id` | `int` | `None` | Override which message in the session this reply continues from. The client tracks this automatically — set it only if you want to branch off an earlier turn. |
| `files` | `list[str]` | `None` | Local file paths to upload and attach to this prompt |
| `file_ids` | `list[str]` | `None` | Already-uploaded file IDs (from `client.upload_file()`) to attach |

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

## File & Image Uploads

Attach images, PDFs, code files, spreadsheets, and more to any prompt. The client uploads the file, waits for DeepSeek to parse it, and includes it as a reference for the model.

### Quickest way — pass `files` directly to `chat()`

```python
response = client.chat(
    "What is in this image?",
    files=["path/to/photo.jpg"],
)
print(response.response)
```

You can attach multiple files at once:

```python
response = client.chat(
    "Compare these two screenshots",
    files=["before.png", "after.png"],
)
```

### Upload once, reuse the same file across multiple chats

If you want to ask several questions about the same file without re-uploading every time, upload it once and reuse the returned `file_id`:

```python
file_id = client.upload_file("report.pdf")

r1 = client.chat("Summarise this PDF in 3 bullets", file_ids=[file_id])
r2 = client.chat("What conclusion does the author reach?", file_ids=[file_id], session_id=r1.session_id)
r3 = client.chat("List every cited source", file_ids=[file_id], session_id=r1.session_id)
```

### Mix uploaded IDs with new files in the same prompt

```python
existing_id = client.upload_file("contract.pdf")

response = client.chat(
    "Are these two pages from the same contract?",
    files=["page_scan.jpg"],          # uploaded now
    file_ids=[existing_id],           # already uploaded earlier
)
```

### Inspect uploaded file metadata

```python
infos = client.fetch_files([file_id])
print(infos[0])
# {
#   "id": "file-...",
#   "file_name": "report.pdf",
#   "status": "SUCCESS",
#   "file_size": 234567,
#   "is_image": False,
#   "token_usage": 812,
#   ...
# }
```

### Supported file types

DeepSeek accepts a wide range of files. Common ones that work out of the box:

| Category | Extensions |
|----------|-----------|
| Images | `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`, `.bmp`, `.heic`, `.heif`, `.tiff` |
| Documents | `.pdf` |
| Office | `.doc`, `.docx`, `.xls`, `.xlsx`, `.ppt`, `.pptx` |
| Text & Markdown | `.txt`, `.md`, `.rtf` |
| Code | `.py`, `.js`, `.ts`, `.tsx`, `.jsx`, `.java`, `.kt`, `.swift`, `.c`, `.h`, `.cpp`, `.hpp`, `.cs`, `.go`, `.rs`, `.rb`, `.php`, `.sh`, `.bash`, `.zsh`, `.lua`, `.r`, `.scala`, `.dart` |
| Web | `.html`, `.htm`, `.css`, `.scss`, `.vue`, `.svelte` |
| Data | `.json`, `.xml`, `.yaml`, `.yml`, `.toml`, `.csv`, `.tsv`, `.sql`, `.ipynb`, `.log` |

> If a file type isn't recognised, the client falls back to `application/octet-stream`. DeepSeek will still try to parse it.

### `upload_file()` parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `file_path` | `str` | required | Local path to the file |
| `model` | `str` | `"default"` | Model that will use the file (just affects upload allocation) |
| `thinking` | `bool` | `False` | Whether the upload should be flagged for thinking-mode usage |
| `poll_interval` | `float` | `1.0` | Seconds between status checks while DeepSeek parses the file |
| `timeout` | `float` | `120.0` | Maximum seconds to wait for parsing before erroring out |

Returns: the `file_id` string (e.g. `"file-a7be4dc1-07b8-4911-b98a-02e79266ca7d"`) once status is `SUCCESS`.

---

## Continuing a Conversation

Pass the previous `session_id` back into `chat()` to keep the context. The client remembers the last `message_id` per session, so each new call appends a fresh turn instead of editing the previous one.

```python
r1 = client.chat("My name is Alex")
r2 = client.chat("What is my name?", session_id=r1.session_id)
print(r2.response)  # "Your name is Alex."
```

> **Note:** Earlier versions of this library would overwrite the same message when you reused `session_id` without an explicit `parent_message_id`. That is fixed — you no longer need to pass `parent_message_id` manually.

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

### Image attached

```python
response = client.chat(
    "Describe this photo in two sentences",
    files=["vacation.jpg"]
)
print(response.response)
```

### PDF attached + thinking

```python
response = client.chat(
    "What are the three main risks mentioned in this PDF?",
    files=["annual_report.pdf"],
    thinking=True,
)
print(response.full_response)
```

### Multi-turn conversation about an uploaded file

```python
file_id = client.upload_file("data.csv")

r1 = client.chat("Give me a 1-line summary of this CSV", file_ids=[file_id])
r2 = client.chat("Which column has the highest variance?", file_ids=[file_id], session_id=r1.session_id)
r3 = client.chat("Suggest 3 charts to visualise it", file_ids=[file_id], session_id=r1.session_id)
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
| `DeepSeekAPIError` | Token expired/invalid, file failed to parse, or DeepSeek returned an error |

---

## Telegram Bot Example — Full Feature Support

A complete, production-ready bot that supports **every feature** of `p2d-deepseek`:

- Text chat with per-user session memory
- Photo uploads (single + albums / media groups)
- Document uploads (PDFs, code, spreadsheets, etc.)
- `/think on|off` — toggle reasoning mode
- `/search on|off` — toggle live web search
- `/model default|expert` — switch model
- `/reset` — start a new conversation
- `/status` — show current settings
- `/start`, `/help`
- Long-message splitting (Telegram's 4096-char limit)
- Per-user state — every user has their own session, model, flags

Install dependencies first:

```bash
pip install p2d-deepseek python-telegram-bot
```

```python
import asyncio
import os
import tempfile
from collections import defaultdict
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from deepseek import DeepSeekClient, DeepSeekConnectionError, DeepSeekAPIError

DEEPSEEK_TOKEN = "YOUR_DEEPSEEK_TOKEN"
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"

client = DeepSeekClient(api_key=DEEPSEEK_TOKEN)

DEFAULT_STATE = {
    "session_id": None,
    "model": "default",
    "thinking": False,
    "search": False,
}
user_state = defaultdict(lambda: dict(DEFAULT_STATE))
album_buffer = defaultdict(list)


def get_state(uid: int) -> dict:
    return user_state[uid]


async def _download(file_obj, suffix: str) -> str:
    fd, path = tempfile.mkstemp(suffix=suffix)
    os.close(fd)
    await file_obj.download_to_drive(path)
    return path


async def _send_long(msg, text: str):
    if not text:
        text = "(empty response)"
    LIMIT = 4000
    for i in range(0, len(text), LIMIT):
        await msg.reply_text(text[i : i + LIMIT])


def _toggle(arg: str) -> bool:
    return arg.strip().lower() in {"on", "true", "1", "yes", "y"}


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hi! I am a DeepSeek bot.\n\n"
        "Send me text, photos, or documents.\n\n"
        "Commands:\n"
        "/think on|off — toggle thinking mode\n"
        "/search on|off — toggle web search\n"
        "/model default|expert — switch model\n"
        "/reset — start a new conversation\n"
        "/status — show current settings\n"
        "/help — show this message"
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await cmd_start(update, context)


async def cmd_reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    s = get_state(update.effective_user.id)
    s["session_id"] = None
    await update.message.reply_text("Session cleared. Next message starts a new conversation.")


async def cmd_think(update: Update, context: ContextTypes.DEFAULT_TYPE):
    s = get_state(update.effective_user.id)
    if context.args:
        s["thinking"] = _toggle(context.args[0])
    else:
        s["thinking"] = not s["thinking"]
    await update.message.reply_text(f"Thinking: {'ON' if s['thinking'] else 'OFF'}")


async def cmd_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    s = get_state(update.effective_user.id)
    if context.args:
        s["search"] = _toggle(context.args[0])
    else:
        s["search"] = not s["search"]
    await update.message.reply_text(f"Web search: {'ON' if s['search'] else 'OFF'}")


async def cmd_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    s = get_state(update.effective_user.id)
    if context.args and context.args[0].lower() in {"default", "expert"}:
        s["model"] = context.args[0].lower()
        await update.message.reply_text(f"Model set to: {s['model']}")
    else:
        await update.message.reply_text("Usage: /model default | expert")


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    s = get_state(update.effective_user.id)
    await update.message.reply_text(
        f"Model: {s['model']}\n"
        f"Thinking: {'ON' if s['thinking'] else 'OFF'}\n"
        f"Search: {'ON' if s['search'] else 'OFF'}\n"
        f"Session: {'active' if s['session_id'] else 'new'}"
    )


async def _process(uid: int, msg, prompt: str, file_paths: list):
    s = get_state(uid)
    try:
        await msg.chat.send_action(ChatAction.TYPING)

        def run():
            return client.chat(
                prompt,
                model=s["model"],
                thinking=s["thinking"],
                search=s["search"],
                session_id=s["session_id"],
                files=file_paths or None,
            )

        response = await asyncio.to_thread(run)
        s["session_id"] = response.session_id
        await _send_long(msg, response.full_response)
    except DeepSeekConnectionError:
        await msg.reply_text("Connection error, please try again.")
    except DeepSeekAPIError as e:
        await msg.reply_text(f"API error: {e}")
    except Exception as e:
        await msg.reply_text(f"Unexpected error: {e}")
    finally:
        for p in file_paths:
            try:
                os.remove(p)
            except OSError:
                pass


async def _flush_album(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    uid, group_id = job.data
    items = album_buffer.pop(group_id, [])
    if not items:
        return
    items.sort(key=lambda x: x["mid"])
    first_msg = items[0]["msg"]
    prompt = next((it["caption"] for it in items if it["caption"]), "Describe these")
    file_paths = []
    for it in items:
        try:
            file_paths.append(await _download(it["tg_file"], it["suffix"]))
        except Exception:
            continue
    await _process(uid, first_msg, prompt, file_paths)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg:
        return
    uid = update.effective_user.id

    if msg.media_group_id:
        if msg.photo:
            tg_file = await msg.photo[-1].get_file()
            suffix = ".jpg"
        elif msg.document:
            tg_file = await msg.document.get_file()
            suffix = os.path.splitext(msg.document.file_name or "")[1] or ".bin"
        else:
            return
        album_buffer[msg.media_group_id].append(
            {"mid": msg.message_id, "msg": msg, "tg_file": tg_file, "suffix": suffix, "caption": msg.caption or ""}
        )
        for j in context.job_queue.get_jobs_by_name(f"album:{msg.media_group_id}"):
            j.schedule_removal()
        context.job_queue.run_once(
            _flush_album, when=1.5, data=(uid, msg.media_group_id), name=f"album:{msg.media_group_id}"
        )
        return

    prompt = msg.text or msg.caption or "Describe this"
    file_paths = []
    if msg.photo:
        tg_file = await msg.photo[-1].get_file()
        file_paths.append(await _download(tg_file, ".jpg"))
    elif msg.document:
        tg_file = await msg.document.get_file()
        suffix = os.path.splitext(msg.document.file_name or "")[1] or ".bin"
        file_paths.append(await _download(tg_file, suffix))

    await _process(uid, msg, prompt, file_paths)


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("reset", cmd_reset))
    app.add_handler(CommandHandler("think", cmd_think))
    app.add_handler(CommandHandler("search", cmd_search))
    app.add_handler(CommandHandler("model", cmd_model))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(
        MessageHandler(
            (filters.TEXT | filters.PHOTO | filters.Document.ALL) & ~filters.COMMAND,
            handle_message,
        )
    )
    app.run_polling()


if __name__ == "__main__":
    main()
```

---

## Notes

- Tokens expire when your DeepSeek session ends — refresh using any method above
- Web search slightly increases response time but adds real-time data
- Thinking mode exposes the model's internal reasoning before the final answer
- All responses are automatically stripped of HTML tags and citation markers
- Always use `response.full_response` in bots — it works correctly whether thinking is enabled or not, and avoids duplicate messages
- File uploads are parsed by DeepSeek before the model can read them. The client polls until parsing is `SUCCESS` (default 120 s timeout — increase via `upload_file(..., timeout=...)` for very large files)
- Upload a file once and reuse its `file_id` for follow-up questions instead of re-uploading every turn

---

## License

MIT — made by [addy](https://t.me/pythontodayz)
