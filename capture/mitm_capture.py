from mitmproxy.tools.dump import DumpMaster
from mitmproxy.options import Options
import asyncio
import threading
import traceback

from capture.mitm_addon import MitmAddon


class MitmCapture:
    def __init__(self, callback):
        self.callback = callback
        self.master = None
        self.loop = None
        self.thread = None
        self.running = False

    def start(self):
        if self.running:
            return

        self.running = True

        def run_loop():
            try:
                self.loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self.loop)

                async def runner():
                    opts = Options(
                        listen_host="127.0.0.1",
                        listen_port=8080
                    )

                    self.master = DumpMaster(opts)

                    addon = MitmAddon(self.callback)
                    self.master.addons.add(addon)

                    print("[MITM] Running on 127.0.0.1:8080")

                    await self.master.run()

                self.loop.run_until_complete(runner())

            except Exception:
                traceback.print_exc()

            finally:
                self.running = False

        self.thread = threading.Thread(
            target=run_loop,
            daemon=True
        )
        self.thread.start()

    def stop(self):
        self.running = False

        if self.master:
            try:
                self.master.shutdown()
            except Exception:
                traceback.print_exc()

        if self.loop and self.loop.is_running():
            try:
                self.loop.call_soon_threadsafe(self.loop.stop)
            except Exception:
                traceback.print_exc()