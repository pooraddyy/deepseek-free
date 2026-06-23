<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&weight=700&size=32&duration=3000&pause=1000&color=4F8EF7&center=true&vCenter=true&width=600&lines=p2d-deepseek;Unofficial+DeepSeek+Python+Client;Chat+%7C+Vision+%7C+Thinking+%7C+Search" alt="p2d-deepseek" />

<br/>

[![PyPI](https://img.shields.io/pypi/v/p2d-deepseek?style=for-the-badge&color=4F8EF7&labelColor=0d1117&label=PyPI)](https://pypi.org/project/p2d-deepseek/)
[![Python](https://img.shields.io/pypi/pyversions/p2d-deepseek?style=for-the-badge&color=4F8EF7&labelColor=0d1117)](https://pypi.org/project/p2d-deepseek/)
[![License](https://img.shields.io/github/license/pooraddyy/deepseek-free?style=for-the-badge&color=4F8EF7&labelColor=0d1117)](LICENSE)
[![Telegram](https://img.shields.io/badge/Telegram-pythontodayz-4F8EF7?style=for-the-badge&logo=telegram&logoColor=white&labelColor=0d1117)](https://t.me/pythontodayz)

<br/>

```
Unofficial Python client for DeepSeek — no API subscription required.
Just your auth token from chat.deepseek.com.
```

</div>

---

## Features

```
  Chat              deepseek-v4-flash and deepseek-v4-pro
  Vision            Image and document uploads (JPEG, PNG, PDF, DOCX, CSV, ...)
  Thinking          Chain-of-thought reasoning
  Web Search        Live search grounding
  Streaming         Token-by-token output
  Multi-turn        Session memory with automatic parent tracking
```

---

## Installation

```bash
pip install p2d-deepseek
```

```bash
pip install p2d-deepseek --upgrade
```

> Package name on PyPI is `p2d-deepseek`. Import name is `deepseek`.

---

## Getting Your Auth Token

### Method 1 — LocalStorage (Desktop)

```
1. Open  https://chat.deepseek.com  and log in
2. Press F12  ->  Application tab  ->  Local Storage
3. Click  https://chat.deepseek.com
4. Find key  userToken  and copy the value
```

### Method 2 — Network Tab (Desktop)

```
1. Open  https://chat.deepseek.com  and log in
2. Press F12  ->  Network tab
3. Send any message
4. Click any request to chat.deepseek.com
5. Copy the  authorization  header value (without "Bearer ")
```

### Method 3 — Kiwi Browser (Android)

```
1. Install Kiwi Browser from Play Store
2. Open  https://chat.deepseek.com  and log in
3. Menu  ->  Developer Tools  ->  Application  ->  Local Storage
4. Copy the  userToken  value
```

> Tokens expire when your DeepSeek session ends. Refresh using any method above.

---

## Quick Start

```python
from deepseek import DeepSeekClient

client = DeepSeekClient(api_key="YOUR_TOKEN_HERE")

response = client.chat("What is the capital of France?")
print(response.response)
# Paris
```

---

## Models

| Model | API name | Description |
|-------|----------|-------------|
| `deepseek-v4-flash` | `default` | Fast, general purpose — **default** |
| `deepseek-v4-pro` | `expert` | Deeper reasoning, more detailed answers |

```python
response = client.chat("Solve this integral", model="deepseek-v4-pro")
```

---

## Chat Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `prompt` | `str` | required | Your message |
| `model` | `str` | `deepseek-v4-flash` | Model to use |
| `thinking` | `bool` | `False` | Enable chain-of-thought reasoning |
| `search` | `bool` | `False` | Enable live web search |
| `session_id` | `str` | `None` | Reuse an existing chat session |
| `parent_message_id` | `int` | `None` | Override parent turn (auto-tracked by default) |
| `files` | `list[str]` | `None` | Local file paths to upload and attach |
| `file_ids` | `list[str]` | `None` | Already-uploaded file IDs to reuse |

---

## Response Fields

```python
response = client.chat("Your prompt here", thinking=True)

response.response          # Final clean answer
response.thinking_content  # Internal reasoning (only when thinking=True)
response.full_response     # Thinking + answer combined — use this in bots
response.session_id        # Continue the conversation
response.message_id        # Message ID in the session
response.status            # Response status from DeepSeek
```

---

## Thinking Mode

```python
response = client.chat("What is 17 * 23?", thinking=True)

print(response.response)
# 391

print(response.thinking_content)
# We need to compute 17 × 23. 17 × 20 = 340, 17 × 3 = 51, total = 391.

print(response.full_response)
# We need to compute 17 × 23. 17 × 20 = 340, 17 × 3 = 51, total = 391.
#
# 17 multiplied by 23 equals 391.
```

> In bots, always use `response.full_response` — it works correctly whether thinking is on or off.

---

## Image and Document Uploads

### Attach directly in `chat()`

```python
# Single image
response = client.chat(
    "What is in this image?",
    files=["photo.jpg"],
)

# Multiple files
response = client.chat(
    "Compare these two screenshots",
    files=["before.png", "after.png"],
)

# PDF with thinking
response = client.chat(
    "What are the three main risks in this document?",
    files=["annual_report.pdf"],
    thinking=True,
)
```

### Upload once, reuse across multiple turns

```python
file_id = client.upload_file("report.pdf")

r1 = client.chat("Summarise this in 3 bullets", file_ids=[file_id])
r2 = client.chat("What conclusion does the author reach?", file_ids=[file_id], session_id=r1.session_id)
r3 = client.chat("List every cited source", file_ids=[file_id], session_id=r1.session_id)
```

### Mix new uploads with existing IDs

```python
existing_id = client.upload_file("contract.pdf")

response = client.chat(
    "Are these from the same contract?",
    files=["page_scan.jpg"],
    file_ids=[existing_id],
)
```

### Inspect file metadata

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
# }
```

### `upload_file()` parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `file_path` | `str` | required | Local path to the file |
| `thinking` | `bool` | `False` | Flag for thinking-mode usage |
| `poll_interval` | `float` | `1.0` | Seconds between status polls |
| `timeout` | `float` | `120.0` | Max seconds before timing out |

Returns: `file_id` string once status is `SUCCESS`.

### Supported file types

| Category | Extensions |
|----------|-----------|
| Images | `.jpg` `.jpeg` `.png` `.gif` `.webp` `.bmp` `.heic` `.tiff` |
| Documents | `.pdf` |
| Office | `.doc` `.docx` `.xls` `.xlsx` `.ppt` `.pptx` |
| Text | `.txt` `.md` `.rtf` |
| Code | `.py` `.js` `.ts` `.tsx` `.java` `.kt` `.swift` `.c` `.cpp` `.cs` `.go` `.rs` `.rb` `.php` `.sh` `.lua` `.r` `.scala` `.dart` |
| Web | `.html` `.css` `.scss` `.vue` `.svelte` |
| Data | `.json` `.xml` `.yaml` `.toml` `.csv` `.tsv` `.sql` `.ipynb` `.log` |

---

## Streaming

```python
from deepseek import DeepSeekClient

client = DeepSeekClient(api_key="YOUR_TOKEN_HERE")

for chunk in client.chat_stream("Explain black holes in simple words"):
    print(chunk, end="", flush=True)
print()
```

### Streaming with pro model

```python
for chunk in client.chat_stream("Prove that sqrt(2) is irrational", model="deepseek-v4-pro"):
    print(chunk, end="", flush=True)
print()
```

### `chat_stream()` parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `prompt` | `str` | required | Your message |
| `model` | `str` | `deepseek-v4-flash` | Model to use |
| `thinking` | `bool` | `False` | Thinking mode (only final answer is yielded) |
| `search` | `bool` | `False` | Live web search |
| `session_id` | `str` | `None` | Reuse an existing session |
| `parent_message_id` | `int` | `None` | Override parent turn |
| `file_ids` | `list[str]` | `None` | Already-uploaded file IDs to attach |

---

## Multi-turn Conversations

```python
r1 = client.chat("My name is Alex")
r2 = client.chat("What is my name?", session_id=r1.session_id)
print(r2.response)
# Your name is Alex.
```

The client tracks the last `message_id` per session automatically — each turn appends correctly without needing `parent_message_id`.

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
| `DeepSeekConnectionError` | Network error or cannot reach DeepSeek |
| `DeepSeekAPIError` | Token expired/invalid, file parse failure, or DeepSeek returned an error |

---

## Full Examples

### All features combined

```python
from deepseek import DeepSeekClient

client = DeepSeekClient(api_key="YOUR_TOKEN_HERE")

# Upload once
file_id = client.upload_file("data.csv")

# Chat with file + thinking + search
r1 = client.chat(
    "Summarise this dataset and find recent trends",
    file_ids=[file_id],
    model="deepseek-v4-pro",
    thinking=True,
    search=True,
)
print(r1.full_response)

# Continue the conversation
r2 = client.chat(
    "Which column shows the most variance?",
    file_ids=[file_id],
    session_id=r1.session_id,
)
print(r2.response)
```

### Telegram bot with full feature support

A production-ready bot supporting text, photos, documents, session memory, `/think`, `/search`, `/model`, `/reset`, `/status`, and long-message splitting.

```bash
pip install p2d-deepseek python-telegram-bot
```

```python
import asyncio, os, tempfile
from collections import defaultdict
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from deepseek import DeepSeekClient, DeepSeekConnectionError, DeepSeekAPIError

DEEPSEEK_TOKEN = "YOUR_DEEPSEEK_TOKEN"
BOT_TOKEN      = "YOUR_TELEGRAM_BOT_TOKEN"

client     = DeepSeekClient(api_key=DEEPSEEK_TOKEN)
user_state = defaultdict(lambda: {"session_id": None, "model": "deepseek-v4-flash", "thinking": False, "search": False})
album_buf  = defaultdict(list)

def get(uid): return user_state[uid]

async def dl(f, suffix):
    fd, p = tempfile.mkstemp(suffix=suffix); os.close(fd)
    await f.download_to_drive(p); return p

async def send(msg, text):
    for i in range(0, max(len(text), 1), 4000):
        await msg.reply_text(text[i:i+4000] or "(empty)")

async def process(uid, msg, prompt, paths):
    s = get(uid)
    try:
        await msg.chat.send_action(ChatAction.TYPING)
        r = await asyncio.to_thread(
            client.chat, prompt,
            model=s["model"], thinking=s["thinking"], search=s["search"],
            session_id=s["session_id"], files=paths or None
        )
        s["session_id"] = r.session_id
        await send(msg, r.full_response)
    except (DeepSeekConnectionError, DeepSeekAPIError) as e:
        await msg.reply_text(str(e))
    finally:
        for p in paths:
            try: os.remove(p)
            except: pass

async def flush_album(ctx):
    uid, gid = ctx.job.data
    items = album_buf.pop(gid, [])
    if not items: return
    items.sort(key=lambda x: x["mid"])
    paths  = [await dl(it["f"], it["s"]) for it in items]
    prompt = next((it["c"] for it in items if it["c"]), "Describe these")
    await process(uid, items[0]["msg"], prompt, paths)

async def on_message(upd: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = upd.message
    if not msg: return
    uid = upd.effective_user.id

    if msg.media_group_id:
        f = await (msg.photo[-1] if msg.photo else msg.document).get_file()
        s = ".jpg" if msg.photo else (os.path.splitext(msg.document.file_name or "")[1] or ".bin")
        album_buf[msg.media_group_id].append({"mid": msg.message_id, "msg": msg, "f": f, "s": s, "c": msg.caption or ""})
        for j in ctx.job_queue.get_jobs_by_name(f"a:{msg.media_group_id}"): j.schedule_removal()
        ctx.job_queue.run_once(flush_album, 1.5, data=(uid, msg.media_group_id), name=f"a:{msg.media_group_id}")
        return

    paths, prompt = [], msg.text or msg.caption or "Describe this"
    if msg.photo:
        paths.append(await dl(await msg.photo[-1].get_file(), ".jpg"))
    elif msg.document:
        ext = os.path.splitext(msg.document.file_name or "")[1] or ".bin"
        paths.append(await dl(await msg.document.get_file(), ext))
    await process(uid, msg, prompt, paths)

async def cmd_think(u, c):
    s = get(u.effective_user.id); arg = c.args[0] if c.args else None
    s["thinking"] = (arg.lower() in {"on","1","true","yes"}) if arg else not s["thinking"]
    await u.message.reply_text(f"Thinking: {'ON' if s['thinking'] else 'OFF'}")

async def cmd_search(u, c):
    s = get(u.effective_user.id); arg = c.args[0] if c.args else None
    s["search"] = (arg.lower() in {"on","1","true","yes"}) if arg else not s["search"]
    await u.message.reply_text(f"Web search: {'ON' if s['search'] else 'OFF'}")

async def cmd_model(u, c):
    s = get(u.effective_user.id)
    valid = {"deepseek-v4-flash", "deepseek-v4-pro"}
    if c.args and c.args[0] in valid:
        s["model"] = c.args[0]; await u.message.reply_text(f"Model: {s['model']}")
    else:
        await u.message.reply_text("Usage: /model deepseek-v4-flash|deepseek-v4-pro")

async def cmd_reset(u, c):
    get(u.effective_user.id)["session_id"] = None
    await u.message.reply_text("Session cleared.")

async def cmd_status(u, c):
    s = get(u.effective_user.id)
    await u.message.reply_text(
        f"Model:   {s['model']}\nThinking: {'ON' if s['thinking'] else 'OFF'}\n"
        f"Search:  {'ON' if s['search'] else 'OFF'}\nSession: {'active' if s['session_id'] else 'new'}"
    )

async def cmd_start(u, c):
    await u.message.reply_text(
        "DeepSeek bot — send text, photos or documents.\n\n"
        "/think on|off    toggle reasoning\n"
        "/search on|off   toggle web search\n"
        "/model <name>    switch model\n"
        "/reset           new conversation\n"
        "/status          current settings"
    )

app = ApplicationBuilder().token(BOT_TOKEN).build()
for cmd, fn in [("start",cmd_start),("help",cmd_start),("reset",cmd_reset),
                ("think",cmd_think),("search",cmd_search),("model",cmd_model),("status",cmd_status)]:
    app.add_handler(CommandHandler(cmd, fn))
app.add_handler(MessageHandler((filters.TEXT|filters.PHOTO|filters.Document.ALL)&~filters.COMMAND, on_message))
app.run_polling()
```

---

## License

MIT — by [addy](https://t.me/pythontodayz)
