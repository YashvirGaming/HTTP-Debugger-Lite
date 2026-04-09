from __future__ import annotations

from core.models import SessionRecord


def session_matches(session: SessionRecord, query: str, method: str, status_group: str, content_type: str) -> bool:
    query = query.strip().lower()
    if query:
        haystack = " ".join(
            [
                session.method,
                session.url,
                session.host,
                session.type,
                session.request_headers,
                session.response_headers,
            ]
        ).lower()
        if query not in haystack:
            return False

    if method != "ALL" and session.method != method:
        return False

    if status_group != "ALL":
        code = session.status
        if status_group == "2xx" and not (200 <= code <= 299):
            return False
        if status_group == "3xx" and not (300 <= code <= 399):
            return False
        if status_group == "4xx" and not (400 <= code <= 499):
            return False
        if status_group == "5xx" and not (500 <= code <= 599):
            return False

    if content_type != "ALL" and session.type != content_type:
        return False

    return True
