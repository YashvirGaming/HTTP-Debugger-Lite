from __future__ import annotations

from dataclasses import dataclass, field
from time import time
from typing import Any, Optional


@dataclass
class SessionRecord:
    id: int
    method: str = ""
    status: int = 0
    url: str = ""
    type: str = "other"
    size: int = 0
    duration_ms: int = 0

    request_headers: dict[str, str] | str = field(default_factory=dict)
    request_body: str | bytes = ""
    request_raw: str = ""
    request_bytes: bytes = b""

    response_headers: dict[str, str] | str = field(default_factory=dict)
    response_body: str | bytes = ""
    response_raw: str = ""
    response_html: str = ""
    response_bytes: bytes = b""

    host: str = ""
    notes: str = ""

    start_ts: float = field(default_factory=time)
    end_ts: Optional[float] = None

    def finalize(self) -> None:
        self.end_ts = time()
        self.duration_ms = int((self.end_ts - self.start_ts) * 1000)

    @property
    def size_text(self) -> str:
        if self.size < 1024:
            return f"{self.size} B"
        if self.size < 1024 * 1024:
            return f"{self.size / 1024:.1f} KB"
        return f"{self.size / (1024 * 1024):.2f} MB"

    @property
    def duration_text(self) -> str:
        return f"{self.duration_ms} ms"

    @property
    def request_headers_text(self) -> str:
        if isinstance(self.request_headers, dict):
            return "\n".join(f"{k}: {v}" for k, v in self.request_headers.items())
        return str(self.request_headers or "")

    @property
    def response_headers_text(self) -> str:
        if isinstance(self.response_headers, dict):
            return "\n".join(f"{k}: {v}" for k, v in self.response_headers.items())
        return str(self.response_headers or "")

    @property
    def request_body_text(self) -> str:
        if isinstance(self.request_body, bytes):
            return self.request_body.decode("utf-8", errors="ignore")
        return str(self.request_body or "")

    @property
    def response_body_text(self) -> str:
        if isinstance(self.response_body, bytes):
            return self.response_body.decode("utf-8", errors="ignore")
        return str(self.response_body or "")

    @property
    def domain(self) -> str:
        return self.host or self.url.split("/")[2] if "://" in self.url else self.host