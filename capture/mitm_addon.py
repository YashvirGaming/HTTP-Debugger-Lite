from mitmproxy import http
import gzip
import zlib


MAX_BODY = 200000   # 200 KB max preview


class MitmAddon:
    def __init__(self, callback):
        self.callback = callback

    def response(self, flow: http.HTTPFlow):
        try:
            request = flow.request
            response = flow.response

            request_bytes = request.content or b""
            response_bytes = response.content or b""

            # Limit huge payloads
            if len(request_bytes) > MAX_BODY:
                request_bytes = request_bytes[:MAX_BODY]

            if len(response_bytes) > MAX_BODY:
                response_bytes = response_bytes[:MAX_BODY]

            encoding = response.headers.get("content-encoding", "").lower()

            if "gzip" in encoding:
                try:
                    response_bytes = gzip.decompress(response_bytes)
                except:
                    pass

            elif "deflate" in encoding:
                try:
                    response_bytes = zlib.decompress(response_bytes)
                except:
                    pass

            try:
                request_body = request.get_text(strict=False)[:MAX_BODY]
            except:
                request_body = request_bytes.decode(errors="ignore")

            try:
                response_body = response_bytes.decode(errors="ignore")
            except:
                response_body = "[binary content]"

            response_body = response_body[:MAX_BODY]

            session = {
                "method": request.method,
                "url": request.pretty_url,
                "host": request.host,

                "headers": dict(request.headers),
                "body": request_body,
                "request_bytes": request_bytes,

                "status": response.status_code,
                "response_headers": dict(response.headers),
                "response_body": response_body,
                "response_bytes": response_bytes,

                "type": response.headers.get("content-type", ""),
                "size": len(response.content or b""),
            }

            self.callback(session)

        except Exception as e:
            import traceback
            traceback.print_exc()