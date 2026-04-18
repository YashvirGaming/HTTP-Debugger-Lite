from __future__ import annotations

import re
from typing import Any

from core.models import SessionRecord


def _to_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="ignore")
    if isinstance(value, dict):
        return " ".join(f"{k}: {v}" for k, v in value.items())
    if isinstance(value, (list, tuple, set)):
        return " ".join(_to_text(v) for v in value)
    return str(value)


def _match_status_group(code: int, status_group: str) -> bool:
    if status_group == "ALL":
        return True
    if code <= 0:
        return False
    if status_group == "1xx":
        return 100 <= code <= 199
    if status_group == "2xx":
        return 200 <= code <= 299
    if status_group == "3xx":
        return 300 <= code <= 399
    if status_group == "4xx":
        return 400 <= code <= 499
    if status_group == "5xx":
        return 500 <= code <= 599
    return True


def _match_content_type(session_type: str, selected_type: str) -> bool:
    if selected_type == "ALL":
        return True
    return selected_type.strip().lower() in (session_type or "").strip().lower()


def _build_haystack(session: SessionRecord) -> str:
    parts = [
        session.method,
        session.url,
        session.host,
        session.type,
        session.notes,
        _to_text(session.request_headers),
        _to_text(session.request_body),
        _to_text(session.response_headers),
        _to_text(session.response_body),
    ]
    return " ".join(_to_text(p) for p in parts).lower()


def _token_match(token: str, session: SessionRecord, haystack: str) -> bool:
    token = token.strip()
    if not token:
        return True

    if token.startswith("re:"):
        pattern = token[3:]
        try:
            return re.search(pattern, haystack, flags=re.IGNORECASE) is not None
        except re.error:
            return False

    negative = token.startswith("-")
    if negative:
        token = token[1:].strip()

    if ":" in token:
        key, value = token.split(":", 1)
        key = key.strip().lower()
        value = value.strip().lower()

        field_map = {
            "method": (session.method or "").lower(),
            "status": str(session.status or ""),
            "host": (session.host or "").lower(),
            "domain": (session.host or "").lower(),
            "url": (session.url or "").lower(),
            "type": (session.type or "").lower(),
            "mime": (session.type or "").lower(),
            "body": (_to_text(session.request_body) + " " + _to_text(session.response_body)).lower(),
            "req": (_to_text(session.request_body)).lower(),
            "resp": (_to_text(session.response_body)).lower(),
            "header": (_to_text(session.request_headers) + " " + _to_text(session.response_headers)).lower(),
        }

        field_value = field_map.get(key)
        matched = value in field_value if field_value is not None else token.lower() in haystack
    else:
        matched = token.lower() in haystack

    return not matched if negative else matched


def session_matches(
    session: SessionRecord,
    query: str,
    method: str,
    status_group: str,
    content_type: str,
) -> bool:
    if method != "ALL" and (session.method or "").upper() != method.upper():
        return False

    if not _match_status_group(int(session.status or 0), status_group):
        return False

    if not _match_content_type(session.type or "", content_type):
        return False

    query = (query or "").strip()
    if not query:
        return True

    haystack = _build_haystack(session)
    tokens = [t for t in query.split() if t.strip()]

    return all(_token_match(token, session, haystack) for token in tokens)