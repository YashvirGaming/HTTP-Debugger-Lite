from __future__ import annotations

import json
from typing import Any


def guess_content_type(headers_text: str, body_text: str) -> str:
    headers = headers_text.lower()
    body = body_text.lstrip()
    if "application/json" in headers:
        return "json"
    if "text/html" in headers or body.startswith("<!doctype html") or body.startswith("<html"):
        return "html"
    if "javascript" in headers:
        return "js"
    if "text/css" in headers:
        return "css"
    if "image/" in headers:
        return "image"
    if body.startswith("{") or body.startswith("["):
        return "json"
    if body.startswith("<"):
        return "html"
    if body:
        return "text"
    return "other"


def pretty_json(text: Any) -> str:
    if not text:
        return ""

    try:
        # If it's already dict/list → format directly
        if isinstance(text, (dict, list)):
            return json.dumps(text, indent=4, ensure_ascii=False)

        # If it's string → parse then format
        stripped = str(text).strip()
        if not stripped:
            return ""

        obj = json.loads(stripped)
        return json.dumps(obj, indent=4, ensure_ascii=False)

    except Exception:
        return str(text)  # fallback (non-JSON)


def make_preview_text(text: str, limit: int = 12000) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + "\n\n...[truncated]..."
