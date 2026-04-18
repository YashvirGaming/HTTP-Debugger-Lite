from __future__ import annotations

from collections import OrderedDict
from typing import Optional

from PySide6.QtCore import QObject, Signal

from core.filters import session_matches
from core.models import SessionRecord


class SessionStore(QObject):
    changed = Signal()

    def __init__(self, max_sessions: int = 5000) -> None:
        super().__init__()
        self._sessions: OrderedDict[int, SessionRecord] = OrderedDict()
        self.max_sessions = max_sessions

    def clear(self) -> None:
        self._sessions.clear()
        self.changed.emit()

    def upsert(self, session: SessionRecord) -> None:
        self._sessions[session.id] = session
        self._sessions.move_to_end(session.id)

        while len(self._sessions) > self.max_sessions:
            self._sessions.popitem(last=False)

        self.changed.emit()

    def all(self) -> list[SessionRecord]:
        return list(self._sessions.values())

    def get_by_id(self, session_id: int) -> Optional[SessionRecord]:
        return self._sessions.get(session_id)

    def filtered(
        self,
        query: str,
        method: str,
        status_group: str,
        content_type: str,
    ) -> list[SessionRecord]:
        return [
            session
            for session in self._sessions.values()
            if session_matches(session, query, method, status_group, content_type)
        ]

    def count(self) -> int:
        return len(self._sessions)

    def latest(self) -> Optional[SessionRecord]:
        if not self._sessions:
            return None
        last_key = next(reversed(self._sessions))
        return self._sessions[last_key]