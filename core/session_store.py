from __future__ import annotations

from typing import List, Optional

from PySide6.QtCore import QObject, Signal

from core.filters import session_matches
from core.models import SessionRecord


class SessionStore(QObject):
    changed = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._sessions: List[SessionRecord] = []

    def clear(self) -> None:
        self._sessions.clear()
        self.changed.emit()

    def upsert(self, session: SessionRecord) -> None:
        for index, existing in enumerate(self._sessions):
            if existing.id == session.id:
                self._sessions[index] = session
                self.changed.emit()
                return
        self._sessions.append(session)
        self.changed.emit()

    def all(self) -> List[SessionRecord]:
        return list(self._sessions)

    def get_by_id(self, session_id: int) -> Optional[SessionRecord]:
        for session in self._sessions:
            if session.id == session_id:
                return session
        return None

    def filtered(self, query: str, method: str, status_group: str, content_type: str) -> List[SessionRecord]:
        return [
            session
            for session in self._sessions
            if session_matches(session, query, method, status_group, content_type)
        ]
