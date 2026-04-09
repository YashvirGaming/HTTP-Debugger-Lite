from mitmproxy import http


class MitmAddon:
    def __init__(self, callback):
        self.callback = callback

    def response(self, flow: http.HTTPFlow):
        try:
            request = flow.request
            response = flow.response

            # 🔥 SAFE REQUEST BODY EXTRACTION
            try:
                request_body = request.get_text(strict=False)
                if not request_body:
                    raise Exception()
            except:
                request_body = (request.content or b"").decode(errors="ignore")

            # 🔥 SAFE RESPONSE BODY EXTRACTION
            try:
                response_body = response.get_text(strict=False)
                if not response_body:
                    raise Exception()
            except:
                response_body = (response.content or b"").decode(errors="ignore")

            session = {
                "method": request.method,
                "url": request.pretty_url,
                "host": request.host,

                "headers": dict(request.headers),
                "body": request_body,

                "status": response.status_code,
                "response_headers": dict(response.headers),
                "response_body": response_body,

                "type": response.headers.get("content-type", ""),
                "size": len(response.content or b""),
            }

            # 🔥 DEBUG (you can remove later)
            print("BODY LENGTH:", len(response_body))

            self.callback(session)

        except Exception as e:
            print("[MITM ERROR]", e)