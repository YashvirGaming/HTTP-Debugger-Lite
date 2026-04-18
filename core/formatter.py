from __future__ import annotations

import base64
import json
from typing import Any
from urllib.parse import parse_qsl, unquote_plus


def _to_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="ignore")
    if isinstance(value, dict):
        return "\n".join(f"{k}: {v}" for k, v in value.items())
    return str(value)


def guess_content_type(headers_text: str | dict | None, body_text: str | bytes | None) -> str:
    headers = _to_text(headers_text).lower()
    body = _to_text(body_text).lstrip()

    if "application/json" in headers:
        return "json"
    if "text/html" in headers or body.startswith("<!doctype html") or body.startswith("<html"):
        return "html"
    if "javascript" in headers:
        return "js"
    if "text/css" in headers:
        return "css"
    if "xml" in headers or body.startswith("<?xml"):
        return "xml"
    if "image/" in headers:
        return "image"
    if "application/x-www-form-urlencoded" in headers:
        return "form"
    if body.startswith("{") or body.startswith("["):
        return "json"
    if body.startswith("<"):
        return "html"
    if "=" in body and "&" in body:
        return "form"
    if body:
        return "text"
    return "other"


def pretty_json(text: Any) -> str:
    if text is None or text == "":
        return ""

    try:
        if isinstance(text, (dict, list)):
            return json.dumps(text, indent=4, ensure_ascii=False)

        stripped = _to_text(text).strip()
        if not stripped:
            return ""

        obj = json.loads(stripped)
        return json.dumps(obj, indent=4, ensure_ascii=False)
    except Exception:
        return _to_text(text)


def pretty_headers(headers: Any) -> str:
    if headers is None:
        return ""
    if isinstance(headers, dict):
        return "\n".join(f"{k}: {v}" for k, v in headers.items())
    return _to_text(headers)


def pretty_form_data(text: Any) -> str:
    raw = _to_text(text).strip()
    if not raw:
        return ""

    try:
        pairs = parse_qsl(raw, keep_blank_values=True)
        if not pairs:
            return raw
        return "\n".join(f"{k} = {v}" for k, v in pairs)
    except Exception:
        return raw


def try_url_decode(text: Any) -> str:
    raw = _to_text(text)
    if not raw:
        return ""
    try:
        return unquote_plus(raw)
    except Exception:
        return raw


def try_base64_decode(text: Any) -> str:
    raw = _to_text(text).strip()
    if not raw or len(raw) < 8:
        return _to_text(text)

    try:
        padding = "=" * (-len(raw) % 4)
        decoded = base64.b64decode(raw + padding, validate=False)
        return decoded.decode("utf-8", errors="ignore")
    except Exception:
        return _to_text(text)


def smart_format(body: Any, headers: Any = None) -> str:
    kind = guess_content_type(headers, body)
    raw = _to_text(body)

    if kind == "json":
        return pretty_json(raw)
    if kind == "form":
        return pretty_form_data(raw)
    return raw


def make_preview_text(text: str, limit: int = 12000) -> str:
    if text is None:
        return ""
    if len(text) <= limit:
        return text
    return text[:limit] + "\n\n...[truncated]..."