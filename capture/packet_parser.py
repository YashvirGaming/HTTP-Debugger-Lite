from __future__ import annotations

from typing import Dict, Optional, Tuple

HTTP_METHODS = (b"GET ", b"POST ", b"PUT ", b"PATCH ", b"DELETE ", b"OPTIONS ", b"HEAD ")


def safe_decode(data: bytes) -> str:
    return data.decode("utf-8", errors="replace")


def looks_like_http_request(payload: bytes) -> bool:
    return any(payload.startswith(method) for method in HTTP_METHODS)


def looks_like_http_response(payload: bytes) -> bool:
    return payload.startswith(b"HTTP/1.")


def split_headers_body(text: str) -> Tuple[str, str]:
    if "\r\n\r\n" in text:
        return text.split("\r\n\r\n", 1)
    if "\n\n" in text:
        return text.split("\n\n", 1)
    return text, ""


def parse_http_request(payload: bytes) -> Optional[Dict[str, str]]:
    try:
        text = safe_decode(payload)
        headers_text, body = split_headers_body(text)
        lines = headers_text.splitlines()
        if not lines:
            return None
        parts = lines[0].split()
        if len(parts) < 2:
            return None
        method, path = parts[0], parts[1]
        headers = "\n".join(lines[1:])
        host = ""
        for line in lines[1:]:
            if line.lower().startswith("host:"):
                host = line.split(":", 1)[1].strip()
                break
        url = f"http://{host}{path}" if host else path
        return {
            "method": method,
            "path": path,
            "host": host,
            "url": url,
            "headers": headers,
            "body": body,
            "raw": text,
        }
    except Exception:
        return None


def parse_http_response(payload: bytes) -> Optional[Dict[str, str | int]]:
    try:
        text = safe_decode(payload)
        headers_text, body = split_headers_body(text)
        lines = headers_text.splitlines()
        if not lines:
            return None
        status_line = lines[0].split()
        status = int(status_line[1]) if len(status_line) >= 2 and status_line[1].isdigit() else 0
        headers = "\n".join(lines[1:])
        return {
            "status": status,
            "headers": headers,
            "body": body,
            "raw": text,
        }
    except Exception:
        return None


def parse_tls_sni(payload: bytes) -> Optional[str]:
    try:
        if len(payload) < 5 or payload[0] != 0x16:
            return None
        if payload[5] != 0x01:
            return None
        idx = 5
        idx += 4
        idx += 2
        idx += 32
        session_id_len = payload[idx]
        idx += 1 + session_id_len
        cipher_len = int.from_bytes(payload[idx:idx+2], 'big')
        idx += 2 + cipher_len
        comp_len = payload[idx]
        idx += 1 + comp_len
        ext_len = int.from_bytes(payload[idx:idx+2], 'big')
        idx += 2
        end = idx + ext_len
        while idx + 4 <= end and idx + 4 <= len(payload):
            ext_type = int.from_bytes(payload[idx:idx+2], 'big')
            ext_size = int.from_bytes(payload[idx+2:idx+4], 'big')
            idx += 4
            ext_data = payload[idx:idx+ext_size]
            idx += ext_size
            if ext_type == 0x0000:
                if len(ext_data) < 5:
                    return None
                list_len = int.from_bytes(ext_data[0:2], 'big')
                pos = 2
                while pos + 3 <= len(ext_data) and pos - 2 < list_len:
                    name_type = ext_data[pos]
                    name_len = int.from_bytes(ext_data[pos+1:pos+3], 'big')
                    pos += 3
                    server_name = ext_data[pos:pos+name_len]
                    if name_type == 0:
                        return server_name.decode('utf-8', errors='replace')
                    pos += name_len
        return None
    except Exception:
        return None
