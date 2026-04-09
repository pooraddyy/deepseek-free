import httpx
import json
import re
import socket
import html as html_module
from typing import Optional, Iterator
from .exceptions import DeepSeekConnectionError, DeepSeekAPIError

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

_JUNK_STRINGS = {"FINISHEDSEARCH", "FINSEARCH", "SEARCH_DONE"}

_original_getaddrinfo = socket.getaddrinfo


def _ipv4_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    return _original_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)


socket.getaddrinfo = _ipv4_getaddrinfo


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


def _is_junk(val: str) -> bool:
    return val.strip() in _JUNK_STRINGS


def _check_api_response(data: dict) -> None:
    code = data.get("code", 0)
    if code != 0 or data.get("data") is None:
        msg = data.get("msg", "Unknown API error")
        if code == 40003 or "invalid token" in msg.lower() or "authorization" in msg.lower():
            raise DeepSeekAPIError(f"Token expired or invalid. Please get a fresh token from chat.deepseek.com. ({msg})")
        raise DeepSeekAPIError(f"DeepSeek API error: {msg}")


def create_session(authorization: str) -> dict:
    url = f"{DEEPSEEK_BASE}/chat_session/create"
    try:
        with httpx.Client(timeout=30) as client:
            resp = client.post(url, content=json.dumps({}), headers=_get_headers(authorization))
            resp.raise_for_status()
            data = resp.json()
    except (httpx.ConnectError, httpx.ConnectTimeout) as e:
        raise DeepSeekConnectionError(f"Cannot connect to DeepSeek: {e}") from e
    except httpx.HTTPStatusError as e:
        raise DeepSeekAPIError(f"DeepSeek API error: {e.response.status_code}") from e
    _check_api_response(data)
    biz = data["data"]["biz_data"]
    session = biz["chat_session"]
    return {
        "session_id": session["id"],
        "ttl_seconds": biz["ttl_seconds"],
    }


def create_pow_challenge(authorization: str, target_path: str = "/api/v0/chat/completion") -> dict:
    url = f"{DEEPSEEK_BASE}/chat/create_pow_challenge"
    payload = {"target_path": target_path}
    try:
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
    except (httpx.ConnectError, httpx.ConnectTimeout) as e:
        raise DeepSeekConnectionError(f"Cannot connect to DeepSeek: {e}") from e
    except httpx.HTTPStatusError as e:
        raise DeepSeekAPIError(f"DeepSeek API error: {e.response.status_code}") from e
    _check_api_response(data)
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
    try:
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
    except (httpx.ConnectError, httpx.ConnectTimeout) as e:
        raise DeepSeekConnectionError(f"Cannot connect to DeepSeek: {e}") from e
    except httpx.HTTPStatusError as e:
        raise DeepSeekAPIError(f"DeepSeek API error: {e.response.status_code}") from e


def _append_to(current_type: str, val: str, response_text: str, thinking_text: str):
    if not val or _is_junk(val):
        return response_text, thinking_text
    if current_type == "THINK":
        thinking_text += val
    elif current_type == "RESPONSE":
        response_text += val
    return response_text, thinking_text


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
    # Start as RESPONSE by default; will switch to THINK if thinking chunks come first
    current_type = "RESPONSE"
    # Track if we have seen any fragment type marker yet
    fragment_type_seen = False

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
        if not line.startswith("data:"):
            continue
        raw = line[5:].strip()
        if not raw:
            continue
        try:
            chunk = json.loads(raw)
        except json.JSONDecodeError:
            continue

        path = chunk.get("p", "")
        op = chunk.get("o", "APPEND")
        val = chunk.get("v")

        # Handle chunks that have no "p" key — these are full snapshot objects
        if "p" not in chunk and "v" in chunk:
            if isinstance(val, str):
                response_text, thinking_text = _append_to(current_type, val, response_text, thinking_text)
            elif isinstance(val, dict) and "response" in val:
                response_obj = val["response"]
                message_id = response_obj.get("message_id")
                status = response_obj.get("status", "WIP")
                for frag in response_obj.get("fragments", []):
                    ftype = frag.get("type", "")
                    if ftype in ("THINK", "THINKING"):
                        current_type = "THINK"
                        fragment_type_seen = True
                    elif ftype == "RESPONSE":
                        current_type = "RESPONSE"
                        fragment_type_seen = True
                    content = frag.get("content", "")
                    response_text, thinking_text = _append_to(current_type, content, response_text, thinking_text)
            continue

        # Handle response/fragments APPEND — this sets the fragment type
        if path == "response/fragments" and op == "APPEND":
            frags = val if isinstance(val, list) else [val]
            for frag in frags:
                ftype = frag.get("type", "")
                if ftype in ("THINK", "THINKING"):
                    current_type = "THINK"
                    fragment_type_seen = True
                elif ftype == "RESPONSE":
                    current_type = "RESPONSE"
                    fragment_type_seen = True
                content = frag.get("content", "")
                response_text, thinking_text = _append_to(current_type, content, response_text, thinking_text)
            continue

        # Handle fragment type switches (no content, just type update)
        if re.match(r"response/fragments/\d+/type$", path) and isinstance(val, str):
            if val in ("THINK", "THINKING"):
                current_type = "THINK"
                fragment_type_seen = True
            elif val == "RESPONSE":
                current_type = "RESPONSE"
                fragment_type_seen = True
            continue

        # Handle incremental content patches for any fragment index
        # Pattern: response/fragments/N/content or response/fragments/-1/content
        if re.match(r"response/fragments/-?\d+/content$", path) and isinstance(val, str):
            response_text, thinking_text = _append_to(current_type, val, response_text, thinking_text)
            continue

        # Handle status updates
        if path == "response/status" and isinstance(val, str):
            status = val
            continue

        # Handle message_id
        if path == "response/message_id" and val is not None:
            message_id = val
            continue

    return {
        "message_id": message_id or 0,
        "response": clean_response(response_text),
        "thinking_content": clean_response(thinking_text) if thinking_text else None,
        "status": status,
    }
