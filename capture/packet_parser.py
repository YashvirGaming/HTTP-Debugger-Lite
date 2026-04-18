from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

HTTP_METHODS = (
    b"GET ",
    b"POST ",
    b"PUT ",
    b"PATCH ",
    b"DELETE ",
    b"OPTIONS ",
    b"HEAD ",
)


def safe_decode(data: bytes) -> str:
    return data.decode("utf-8", errors="replace")


def looks_like_http_request(payload: bytes) -> bool:
    return any(payload.startswith(method) for method in HTTP_METHODS)


def looks_like_http_response(payload: bytes) -> bool:
    return payload.startswith(b"HTTP/1.")


def split_headers_body_bytes(payload: bytes) -> Tuple[bytes, bytes]:
    if b"\r\n\r\n" in payload:
        return payload.split(b"\r\n\r\n", 1)
    if b"\n\n" in payload:
        return payload.split(b"\n\n", 1)
    return payload, b""


def split_headers_body(text: str) -> Tuple[str, str]:
    if "\r\n\r\n" in text:
        return text.split("\r\n\r\n", 1)
    if "\n\n" in text:
        return text.split("\n\n", 1)
    return text, ""


def parse_headers(lines: list[str]) -> Dict[str, str]:
    headers: Dict[str, str] = {}
    last_key: Optional[str] = None

    for line in lines:
        if not line.strip():
            continue

        if (line.startswith(" ") or line.startswith("\t")) and last_key:
            headers[last_key] = f"{headers[last_key]} {line.strip()}".strip()
            continue

        if ":" not in line:
            continue

        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()

        if not key:
            continue

        headers[key] = value
        last_key = key

    return headers


def get_header(headers: Dict[str, str], name: str, default: str = "") -> str:
    target = name.lower()
    for key, value in headers.items():
        if key.lower() == target:
            return value
    return default


def build_url(host: str, path: str, scheme: str = "http") -> str:
    if not host:
        return path
    if path.startswith("http://") or path.startswith("https://"):
        return path
    return f"{scheme}://{host}{path}"


def parse_http_request(payload: bytes) -> Optional[Dict[str, Any]]:
    try:
        headers_raw, body_bytes = split_headers_body_bytes(payload)
        headers_text = safe_decode(headers_raw)
        body_text = safe_decode(body_bytes)

        lines = headers_text.splitlines()
        if not lines:
            return None

        request_line = lines[0].strip()
        parts = request_line.split()
        if len(parts) < 2:
            return None

        method = parts[0].upper()
        path = parts[1]
        version = parts[2] if len(parts) >= 3 else ""

        headers_dict = parse_headers(lines[1:])
        host = get_header(headers_dict, "Host")
        content_type = get_header(headers_dict, "Content-Type")
        content_length_raw = get_header(headers_dict, "Content-Length", "0")

        try:
            content_length = int(content_length_raw) if content_length_raw.isdigit() else 0
        except Exception:
            content_length = 0

        url = build_url(host, path, "http")

        return {
            "method": method,
            "path": path,
            "version": version,
            "host": host,
            "url": url,
            "headers": headers_dict,
            "headers_text": "\n".join(lines[1:]),
            "body": body_text,
            "body_bytes": body_bytes,
            "raw": safe_decode(payload),
            "raw_bytes": payload,
            "type": content_type,
            "content_length": content_length,
        }
    except Exception:
        return None


def parse_http_response(payload: bytes) -> Optional[Dict[str, Any]]:
    try:
        headers_raw, body_bytes = split_headers_body_bytes(payload)
        headers_text = safe_decode(headers_raw)
        body_text = safe_decode(body_bytes)

        lines = headers_text.splitlines()
        if not lines:
            return None

        status_line = lines[0].strip().split()
        status = int(status_line[1]) if len(status_line) >= 2 and status_line[1].isdigit() else 0
        version = status_line[0] if status_line else ""
        reason = " ".join(status_line[2:]) if len(status_line) > 2 else ""

        headers_dict = parse_headers(lines[1:])
        content_type = get_header(headers_dict, "Content-Type")
        content_length_raw = get_header(headers_dict, "Content-Length", "0")
        transfer_encoding = get_header(headers_dict, "Transfer-Encoding")
        content_encoding = get_header(headers_dict, "Content-Encoding")

        try:
            content_length = int(content_length_raw) if content_length_raw.isdigit() else 0
        except Exception:
            content_length = 0

        return {
            "status": status,
            "version": version,
            "reason": reason,
            "headers": headers_dict,
            "headers_text": "\n".join(lines[1:]),
            "body": body_text,
            "body_bytes": body_bytes,
            "raw": safe_decode(payload),
            "raw_bytes": payload,
            "type": content_type,
            "content_length": content_length,
            "transfer_encoding": transfer_encoding,
            "content_encoding": content_encoding,
        }
    except Exception:
        return None


def parse_tls_sni(payload: bytes) -> Optional[str]:
    try:
        if len(payload) < 6:
            return None

        if payload[0] != 0x16:
            return None

        if len(payload) <= 5 or payload[5] != 0x01:
            return None

        idx = 5

        if idx + 4 > len(payload):
            return None
        idx += 4

        if idx + 2 > len(payload):
            return None
        idx += 2

        if idx + 32 > len(payload):
            return None
        idx += 32

        if idx >= len(payload):
            return None
        session_id_len = payload[idx]
        idx += 1

        if idx + session_id_len > len(payload):
            return None
        idx += session_id_len

        if idx + 2 > len(payload):
            return None
        cipher_len = int.from_bytes(payload[idx:idx + 2], "big")
        idx += 2

        if idx + cipher_len > len(payload):
            return None
        idx += cipher_len

        if idx >= len(payload):
            return None
        comp_len = payload[idx]
        idx += 1

        if idx + comp_len > len(payload):
            return None
        idx += comp_len

        if idx + 2 > len(payload):
            return None
        ext_len = int.from_bytes(payload[idx:idx + 2], "big")
        idx += 2

        end = idx + ext_len
        if end > len(payload):
            return None

        while idx + 4 <= end:
            if idx + 4 > len(payload):
                return None

            ext_type = int.from_bytes(payload[idx:idx + 2], "big")
            ext_size = int.from_bytes(payload[idx + 2:idx + 4], "big")
            idx += 4

            if idx + ext_size > len(payload):
                return None

            ext_data = payload[idx:idx + ext_size]
            idx += ext_size

            if ext_type != 0x0000:
                continue

            if len(ext_data) < 5:
                return None

            list_len = int.from_bytes(ext_data[0:2], "big")
            pos = 2
            list_end = min(len(ext_data), 2 + list_len)

            while pos + 3 <= list_end:
                name_type = ext_data[pos]
                name_len = int.from_bytes(ext_data[pos + 1:pos + 3], "big")
                pos += 3

                if pos + name_len > list_end:
                    return None

                server_name = ext_data[pos:pos + name_len]
                pos += name_len

                if name_type == 0:
                    return server_name.decode("utf-8", errors="replace")

        return None
    except Exception:
        return None