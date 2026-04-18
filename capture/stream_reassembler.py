from __future__ import annotations


class StreamBuffer:
    def __init__(self, max_size: int = 2 * 1024 * 1024):
        self.buffers: dict[tuple, bytes] = {}
        self.max_size = max_size

    def add(self, key: tuple, data: bytes) -> bytes | None:
        if not data:
            return None

        buf = self.buffers.get(key, b"") + data

        if len(buf) > self.max_size:
            buf = buf[-self.max_size:]

        self.buffers[key] = buf

        if b"\r\n\r\n" not in buf:
            return None

        headers, body = buf.split(b"\r\n\r\n", 1)

        headers_lower = headers.lower()

        if b"content-length:" in headers_lower:
            try:
                for line in headers.split(b"\r\n"):
                    if line.lower().startswith(b"content-length:"):
                        length = int(line.split(b":", 1)[1].strip())
                        if len(body) >= length:
                            full = headers + b"\r\n\r\n" + body[:length]
                            self.buffers.pop(key, None)
                            return full
            except:
                pass

        if b"transfer-encoding: chunked" in headers_lower:
            if body.endswith(b"0\r\n\r\n"):
                full = headers + b"\r\n\r\n" + body
                self.buffers.pop(key, None)
                return full

        if len(body) > 0:
            full = headers + b"\r\n\r\n" + body
            self.buffers.pop(key, None)
            return full

        return None

    def clear(self, key: tuple):
        self.buffers.pop(key, None)

    def clear_all(self):
        self.buffers.clear()