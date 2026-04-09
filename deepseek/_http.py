import httpx
import json
import re
import html as html_module
from typing import Optional, Iterator

BASE_HEADERS = {
    "User-Agent": "DeepSeek/1.8.2 iOS/26.4",
    "Content-Type": "application/json",
    "x-client-version": "1.8.2",
    "x-client-bundle-id": "com.deepseek.chat",
    "x-client-platform": "ios",
    "x-client-locale": "en_US",
    "x-client-timezone-offset": "19800",
    "x-rangers-id": "7917485426619761413",
    "x-hif-leim": "c++lgX4xwG2K8g/TrlUonAKq3uLkfPfHMAkvUJAp1+1+GSGSRxCL8uA=.xKqJ14kAcIXk4EXI",
    "x-hif-dliq": "1loG5Ynr3k1yyUyaJZ1+AeD9FBKF//xM9oam9Ji/caQrBmsaO8MzQtA=.Ickqf/tuOs4wvlza",
    "accept-language": "en-US,en;q=0.9",
    "priority": "u=3, i",
}

DEEPSEEK_BASE = "https://chat.deepseek.com/api/v0"


def _get_headers(authorization: str, extra: Optional[dict] = None) -> dict:
    headers = {**BASE_HEADERS, "authorization": authorization}
    if extra:
        headers.update(extra)
    return headers


def clean_response(text: str) -> str:
    text = html_module.unescape(text)
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\[citation:\d+\]", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def create_session(authorization: str) -> dict:
    url = f"{DEEPSEEK_BASE}/chat_session/create"
    with httpx.Client(timeout=30) as client:
        resp = client.post(url, content=json.dumps({}), headers=_get_headers(authorization))
        resp.raise_for_status()
        data = resp.json()
    biz = data["data"]["biz_data"]
    session = biz["chat_session"]
    return {
        "session_id": session["id"],
        "ttl_seconds": biz["ttl_seconds"],
    }


def create_pow_challenge(authorization: str, target_path: str = "/api/v0/chat/completion") -> dict:
    url = f"{DEEPSEEK_BASE}/chat/create_pow_challenge"
    payload = {"target_path": target_path}
    with httpx.Client(timeout=30) as client:
        resp = client.post(url, content=json.dumps(payload), headers=_get_headers(authorization))
        resp.raise_for_status()
        session_cookie = None
        for key, value in resp.cookies.items():
            if key == "ds_session_id":
                session_cookie = value
                break
        if not session_cookie:
            set_cookie = resp.headers.get("set-cookie", "")
            if "ds_session_id=" in set_cookie:
                part = set_cookie.split("ds_session_id=")[1]
                session_cookie = part.split(";")[0]
        data = resp.json()
    challenge = data["data"]["biz_data"]["challenge"]
    return {
        "challenge": {
            "algorithm": challenge["algorithm"],
            "challenge": challenge["challenge"],
            "salt": challenge["salt"],
            "signature": challenge["signature"],
            "difficulty": challenge["difficulty"],
            "expire_at": challenge["expire_at"],
            "expire_after": challenge["expire_after"],
            "target_path": challenge["target_path"],
        },
        "session_cookie": session_cookie,
    }


def send_message_stream(
    authorization: str,
    chat_session_id: str,
    prompt: str,
    pow_response: str,
    session_cookie: str,
    model_type: str = "default",
    thinking_enabled: bool = False,
    search_enabled: bool = False,
    parent_message_id: Optional[int] = None,
) -> Iterator[str]:
    url = f"{DEEPSEEK_BASE}/chat/completion"
    payload = {
        "prompt": prompt,
        "search_enabled": search_enabled,
        "chat_session_id": chat_session_id,
        "preempt": False,
        "model_type": model_type,
        "parent_message_id": parent_message_id,
        "audio_id": None,
        "ref_file_ids": [],
        "thinking_enabled": thinking_enabled,
    }
    extra_headers = {
        "x-ds-pow-response": pow_response,
        "Cookie": f"ds_session_id={session_cookie}",
    }
    with httpx.Client(timeout=120) as client:
        with client.stream(
            "POST",
            url,
            content=json.dumps(payload),
            headers=_get_headers(authorization, extra=extra_headers),
        ) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                yield line


def send_message(
    authorization: str,
    chat_session_id: str,
    prompt: str,
    pow_response: str,
    session_cookie: str,
    model_type: str = "default",
    thinking_enabled: bool = False,
    search_enabled: bool = False,
    parent_message_id: Optional[int] = None,
) -> dict:
    response_text = ""
    thinking_text = ""
    message_id = None
    status = "WIP"

    for line in send_message_stream(
        authorization=authorization,
        chat_session_id=chat_session_id,
        prompt=prompt,
        pow_response=pow_response,
        session_cookie=session_cookie,
        model_type=model_type,
        thinking_enabled=thinking_enabled,
        search_enabled=search_enabled,
        parent_message_id=parent_message_id,
    ):
        if not line or line.startswith("event:"):
            continue
        if line.startswith("data:"):
            raw = line[5:].strip()
            if not raw:
                continue
            try:
                chunk = json.loads(raw)
            except json.JSONDecodeError:
                continue

            if "v" in chunk and isinstance(chunk["v"], dict) and "response" in chunk["v"]:
                response_obj = chunk["v"]["response"]
                message_id = response_obj.get("message_id")
                status = response_obj.get("status", "WIP")
                fragments = response_obj.get("fragments", [])
                for frag in fragments:
                    if frag.get("type") == "RESPONSE":
                        response_text += frag.get("content", "")
                    elif frag.get("type") == "THINKING":
                        thinking_text += frag.get("content", "")

            elif "p" in chunk and "o" in chunk and "v" in chunk:
                op = chunk["o"]
                path = chunk["p"]
                val = chunk["v"]
                if op == "APPEND" and "content" in path:
                    if "thinking" in path.lower():
                        thinking_text += val
                    else:
                        response_text += val
                elif op == "SET" and path == "response/status":
                    status = val

            elif "v" in chunk and isinstance(chunk["v"], str):
                response_text += chunk["v"]

    return {
        "message_id": message_id or 0,
        "response": clean_response(response_text),
        "thinking_content": clean_response(thinking_text) if thinking_text else None,
        "status": status,
    }
