from __future__ import annotations

from core.formatter import guess_content_type, pretty_json
from core.models import SessionRecord
from capture.packet_parser import parse_http_request, parse_http_response, parse_tls_sni, looks_like_http_request, looks_like_http_response


class HttpDetector:
    def __init__(self) -> None:
        self.next_id = 1
        self.flow_to_session: dict[tuple, SessionRecord] = {}
        self.tls_seen: set[tuple] = set()

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

        if packet.dst_port == 80 and looks_like_http_request(payload):
            parsed = parse_http_request(payload)
            if not parsed:
                return None
            session = self._new_session()
            session.method = str(parsed["method"])
            session.url = str(parsed["url"])
            session.host = str(parsed["host"])
            session.request_headers = str(parsed["headers"])
            session.request_body = str(parsed["body"])
            session.request_raw = str(parsed["raw"])
            session.size += len(payload)
            self.flow_to_session[flow_key] = session
            return session

        if packet.src_port == 80 and looks_like_http_response(payload):
            parsed = parse_http_response(payload)
            if not parsed:
                return None
            session = self.flow_to_session.get(reverse_key)
            if not session:
                session = self._new_session()
            session.status = int(parsed["status"])
            session.response_headers = str(parsed["headers"])
            body = str(parsed["body"])
            session.response_body = pretty_json(body)
            session.response_raw = str(parsed["raw"])
            session.response_html = body if guess_content_type(session.response_headers, body) == "html" else ""
            session.type = guess_content_type(session.response_headers, body)
            session.size += len(payload)
            session.finalize()
            return session

        if packet.dst_port == 443:
            sni = parse_tls_sni(payload)
            if sni:
                tls_key = (flow_key, sni)
                if tls_key in self.tls_seen:
                    return None
                self.tls_seen.add(tls_key)
                session = self._new_session()
                session.method = "TLS"
                session.url = sni or dst_ip
                session.host = sni
                session.type = "tls"
                session.request_headers = f"TLS ClientHello\nSNI: {sni}\nDestination: {packet.dst_addr}:{packet.dst_port}"
                session.request_body = "Encrypted HTTPS traffic detected. Request body is not available without TLS interception."
                session.request_raw = session.request_headers
                session.response_headers = "Encrypted HTTPS traffic"
                session.response_body = "Response body is not available without TLS interception."
                session.response_raw = "Encrypted HTTPS traffic"
                session.notes = "HTTPS host preview only"
                session.size += len(payload)
                session.finalize()
                return session

        return None
