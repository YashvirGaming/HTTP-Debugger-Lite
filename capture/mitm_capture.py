from mitmproxy.tools.dump import DumpMaster
from mitmproxy.options import Options
import asyncio
import threading

from capture.mitm_addon import MitmAddon


class MitmCapture:
    def __init__(self, callback):
        self.callback = callback
        self.master = None
        self.loop = None
        self.thread = None

    def start(self):
        def run_loop():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

            async def runner():
                opts = Options(listen_host="127.0.0.1", listen_port=8080)

                self.master = DumpMaster(opts)

                addon = MitmAddon(self.callback)
                self.master.addons.add(addon)

                print("[MITM] Running on 127.0.0.1:8080")

                await self.master.run()

            self.loop.run_until_complete(runner())

        self.thread = threading.Thread(target=run_loop, daemon=True)
        self.thread.start()

    def stop(self):
        if self.master:
            print("[MITM] Stopping")
            self.master.shutdown()

        if self.loop:
            self.loop.stop()