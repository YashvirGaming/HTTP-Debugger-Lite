from __future__ import annotations

import threading
import time
from typing import Callable, Optional

try:
    import pydivert  # type: ignore
except Exception:  # pragma: no cover
    pydivert = None

from capture.http_detector import HttpDetector


class WinDivertCapture:
    def __init__(self, on_session: Callable[[object], None], on_state: Callable[[str], None], on_error: Callable[[str], None]) -> None:
        self.on_session = on_session
        self.on_state = on_state
        self.on_error = on_error
        self.detector = HttpDetector()
        self._thread: Optional[threading.Thread] = None
        self._running = False
        self._paused = False

    def start(self) -> None:
        if self._running:
            self._paused = False
            self.on_state("Running")
            return
        self._running = True
        self._paused = False
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def pause(self) -> None:
        self._paused = True
        self.on_state("Paused")

    def stop(self) -> None:
        self._running = False
        self._paused = False
        self.on_state("Stopped")

    def _run(self) -> None:
        if pydivert is None:
            self.on_error("pydivert is not installed. Run: pip install pydivert")
            self._running = False
            return

        self.on_state("Starting")
        flt = "tcp and (tcp.DstPort == 80 or tcp.SrcPort == 80 or tcp.DstPort == 443)"
        try:
            with pydivert.WinDivert(flt) as handle:
                self.on_state("Running")
                while self._running:
                    packet = handle.recv()
                    handle.send(packet)
                    if self._paused:
                        continue
                    try:
                        session = self.detector.ingest_packet(packet)
                        if session is not None:
                            self.on_session(session)
                    except Exception as exc:
                        self.on_error(f"Packet parse error: {exc}")
        except PermissionError:
            self.on_error("Administrator rights are required to start WinDivert capture.")
        except OSError as exc:
            self.on_error(f"WinDivert error: {exc}")
        except Exception as exc:
            self.on_error(f"Capture error: {exc}")
        finally:
            self._running = False
            time.sleep(0.05)
            self.on_state("Stopped")
