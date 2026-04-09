from __future__ import annotations

from dataclasses import dataclass, field
from time import time
from typing import Optional


@dataclass
class SessionRecord:
    id: int
    method: str = ""
    status: int = 0
    url: str = ""
    type: str = "other"
    size: int = 0
    duration_ms: int = 0
    request_headers: str = ""
    request_body: str = ""
    request_raw: str = ""
    response_headers: str = ""
    response_body: str = ""
    response_raw: str = ""
    response_html: str = ""
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
