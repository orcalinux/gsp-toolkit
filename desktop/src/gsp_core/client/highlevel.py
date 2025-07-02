# src/gsp_core/client/highlevel.py

from typing import Optional, Any
from gsp_core.protocol.cra import CommandFrame, parse_frame, Priority
from gsp_core.protocol.slip import encode, decode
from gsp_core.events import publish
from gsp_core.config import load_config

_OK_STATUS = 0x00

class GSPTimeout(Exception):
    """
    Raised when GSP retries are exhausted or a timeout occurs.
    """
    pass

class GSPClient:
    """
    High-level GSP client. Sends commands over any transport
    implementing send(bytes) and recv_frame() -> bytes.
    Retries are governed by config.general.max_retries.
    """
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
        """
        Build a CommandFrame, send it SLIP-encoded, await
        a 'resp' frame, and return its payload. Retries
        on timeouts, framing/CRC errors, up to max_retries.
        """
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

    def erase_flash(
        self,
        address: Optional[int] = None,
        length:  Optional[int] = None,
        priority: Priority = Priority.NORMAL
    ) -> None:
        """
        Erase flash memory. If address+length given, erases that region;
        otherwise a full-chip erase.
        """
        publish("status", "Erasing flash")
        data = b""
        if address is not None and length is not None:
            data = address.to_bytes(4, "little") + length.to_bytes(4, "little")
        self._call(cmd=0x10, payload=data, priority=priority)

    def write_chunk(
        self,
        data: bytes,
        priority: Priority = Priority.NORMAL
    ) -> None:
        """
        Send one 0–256 byte data chunk to the target.
        """
        publish("progress", len(data))
        self._call(cmd=0x11, payload=data, priority=priority)

    def verify_chunk(self) -> None:
        """
        Request CRC check of the last written chunk.
        """
        publish("status", "Verifying chunk")
        self._call(cmd=0x12)

    def reset_and_run(self) -> None:
        """
        Exit bootloader and run the main application.
        """
        publish("status", "Resetting and running")
        self._call(cmd=0x13)

    def abort(self) -> None:
        """
        Abort the current session and discard partial state.
        """
        publish("status", "Aborting session")
        self._call(cmd=0x14)
