import re
import socket
import html as html_module
from typing import Optional

from ..exceptions import DeepSeekAPIError

BASE_HEADERS = {
    "User-Agent": "DeepSeek/2.1.8 iOS/26.5",
    "Content-Type": "application/json",
    "x-client-version": "2.1.8",
    "x-client-bundle-id": "com.deepseek.chat",
    "x-client-platform": "ios",
    "x-client-locale": "en_US",
    "x-client-timezone-offset": "19800",
    "x-rangers-id": "7917485426619761413",
    "x-hif-leim": "Ql5a/yjz/zex3xnmbjeUY6lBkUvOXmdtHnbRo1X3NslowiVHjNlbI/E=.mkNG7LeTD8tIij8w",
    "x-hif-dliq": "5Dbvz9zqqbD/LEc7fFVybn4c4IL1MiUn/jWIzuycURM33m1CwpC+7To=.d6U9AemELnLxNfir",
    "accept-language": "en-US,en;q=0.9",
    "priority": "u=3, i",
}

DEEPSEEK_BASE = "https://chat.deepseek.com/api/v0"

JUNK_STRINGS = {"FINISHEDSEARCH", "FINSEARCH", "SEARCH_DONE"}

original_getaddrinfo = socket.getaddrinfo


def ipv4_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    return original_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)


socket.getaddrinfo = ipv4_getaddrinfo


def get_headers(authorization: str, extra: Optional[dict] = None) -> dict:
    headers = {**BASE_HEADERS, "authorization": authorization}
    if extra:
        headers.update(extra)
    return headers


def check_api_response(data: dict) -> None:
    code = data.get("code", 0)
    if code != 0 or data.get("data") is None:
        msg = data.get("msg", "Unknown API error")
        if code == 40003 or "invalid token" in msg.lower() or "authorization" in msg.lower():
            raise DeepSeekAPIError(
                f"Token expired or invalid. Please get a fresh token from chat.deepseek.com. ({msg})"
            )
        raise DeepSeekAPIError(f"DeepSeek API error: {msg}")


def clean_response(text: str) -> str:
    text = html_module.unescape(text)
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\[citation:\d+\]", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def is_junk(val: str) -> bool:
    return val.strip() in JUNK_STRINGS
