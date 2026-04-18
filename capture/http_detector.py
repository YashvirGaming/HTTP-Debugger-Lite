from __future__ import annotations

from capture.stream_reassembler import StreamBuffer
from core.models import SessionRecord
from capture.packet_parser import (
    parse_http_request,
    parse_http_response,
    parse_tls_sni,
    looks_like_http_request,
    looks_like_http_response,
)


class HttpDetector:
    def __init__(self) -> None:
        self.next_id = 1
        self.flow_to_session: dict[tuple, SessionRecord] = {}
        self.tls_seen: set[tuple] = set()
        self.streams = StreamBuffer()

    def _new_session(self) -> SessionRecord:
        session = SessionRecord(id=self.next_id)
        self.next_id += 1
        return session

    def ingest_packet(self, packet) -> SessionRecord | None:
        payload = bytes(packet.payload or b"")
        if not payload:
            return None

        reverse_key = (str(packet.dst_addr), packet.dst_port, str(packet.src_addr), packet.src_port)
        flow_key = (str(packet.src_addr), packet.src_port, str(packet.dst_addr), packet.dst_port)

        if packet.dst_port == 80:
            full_data = self.streams.add(flow_key, payload)
            if not full_data:
                return None
            payload = full_data

            if looks_like_http_request(payload):
                parsed = parse_http_request(payload)
                if not parsed:
                    return None

                session = self._new_session()
                session.method = parsed["method"]
                session.url = parsed["url"]
                session.host = parsed["host"]

                session.request_headers = parsed["headers"]
                session.request_body = parsed["body"]
                session.request_bytes = parsed["body_bytes"]
                session.request_raw = parsed["raw"]

                session.type = parsed.get("type", "")
                session.size = len(payload)

                self.flow_to_session[flow_key] = session
                return session

        if packet.src_port == 80:
            full_data = self.streams.add(flow_key, payload)
            if not full_data:
                return None
            payload = full_data

            if looks_like_http_response(payload):
                parsed = parse_http_response(payload)
                if not parsed:
                    return None

                session = self.flow_to_session.get(reverse_key)
                if not session:
                    session = self._new_session()

                session.status = parsed["status"]
                session.response_headers = parsed["headers"]
                session.response_body = parsed["body"]
                session.response_bytes = parsed["body_bytes"]
                session.response_raw = parsed["raw"]

                session.type = parsed.get("type", "")
                session.size = len(payload)

                session.finalize()

                self.flow_to_session.pop(reverse_key, None)
                self.streams.clear(flow_key)
                self.streams.clear(reverse_key)

                return session

        if packet.dst_port == 443:
            sni = parse_tls_sni(payload)
            if sni:
                tls_key = (flow_key, sni)
                if tls_key in self.tls_seen:
                    return None

                self.tls_seen.add(tls_key)

                if len(self.tls_seen) > 5000:
                    self.tls_seen.clear()
                    self.tls_seen.add(tls_key)

                session = self._new_session()
                session.method = "TLS"
                session.url = sni or str(packet.dst_addr)
                session.host = sni
                session.type = "tls"

                session.request_headers = {
                    "SNI": sni,
                    "Destination": f"{packet.dst_addr}:{packet.dst_port}",
                }
                session.request_body = "Encrypted HTTPS traffic detected"
                session.request_raw = str(session.request_headers)

                session.response_headers = {}
                session.response_body = "Encrypted HTTPS response"
                session.response_raw = ""

                session.notes = "HTTPS host preview only"
                session.size = len(payload)

                session.finalize()
                return session

        return None