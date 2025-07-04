from typing import Any, Optional
from gsp_core.protocol.cra import CommandFrame, parse_frame, Priority
from gsp_core.protocol.slip import encode, decode
from gsp_core.config import load_config
from gsp_core.events import publish

_OK_STATUS = 0x00

class GSPTimeout(Exception):
    """Raised when GSP retries are exhausted or a timeout occurs."""
    pass

class BaseGSPClient:
    def __init__(self, transport: Any, start_sid: int = 0):
        cfg = load_config()
        self._max_retries = cfg.get("general", {}).get("max_retries", 5)
        self.transport    = transport
        self._sid         = start_sid & 0xFF

    def _next_sid(self) -> int:
        sid = self._sid
        self._sid = (sid + 1) & 0xFF
        return sid

    def _call(
        self,
        cmd: int,
        payload: bytes = b"",
        priority: Priority = Priority.NORMAL
    ) -> bytes:
        sid      = self._next_sid()
        raw_cmd  = CommandFrame(sid=sid, cmd=cmd, payload=payload, priority=priority).build()
        slip_cmd = encode(raw_cmd)
        last_exc = None

        for attempt in range(1, self._max_retries + 1):
            self.transport.send(slip_cmd)
            try:
                raw = self.transport.recv_frame()
                if not raw:
                    raise GSPTimeout(f"no data (timeout #{attempt})")

                resp = decode(raw)
                kind, info = parse_frame(resp)

                if kind != "resp":
                    raise RuntimeError(f"expected 'resp', got '{kind}'")
                if info["sid"] != sid:
                    raise RuntimeError(f"Session ID mismatch (sent={sid}, got={info['sid']})")
                status = info["status"]
                if status != bytes([_OK_STATUS]):
                    raise RuntimeError(f"GSP error status 0x{status.hex()}")

                return info.get("payload", b"")
            except (GSPTimeout, ValueError, RuntimeError) as e:
                last_exc = e
                if attempt < self._max_retries:
                    publish("status", f"Retrying (attempt {attempt}/{self._max_retries})")
                    continue
                break

        msg = f"Command 0x{cmd:02X} failed after {self._max_retries} attempts: {last_exc}"
        publish("error", msg)
        raise GSPTimeout(msg)
