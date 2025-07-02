# src/gsp_core/protocol/cra.py

from dataclasses import dataclass
from enum import IntEnum
from struct import pack, unpack_from
from typing import ClassVar, Tuple, Dict, Any

class Priority(IntEnum):
    LOW      = 0
    NORMAL   = 1
    HIGH     = 2
    CRITICAL = 3

@dataclass(slots=True)
class CommandFrame:
    sid:      int
    cmd:      int
    payload:  bytes = b""
    priority: Priority = Priority.NORMAL

    _HDR_LEN: ClassVar[int] = 5

    def build(self) -> bytes:
        """Builds a CRA command frame (no SLIP!)."""
        # Flags: reserved=0, AF=0 (command), priority=0-3
        flags = (0 << 3) | (0 << 2) | (self.priority & 0x03)
        # <BBBH = sid, flags, cmd, payload_len (LE)
        header = pack("<BBBH", self.sid, flags, self.cmd, len(self.payload))
        return header + self.payload

@dataclass(slots=True)
class AckFrame:
    sid: int

    def build(self) -> bytes:
        """Builds an ACK-only frame (3 bytes, no payload)."""
        # Flags: reserved=0, AF=1 (ACK), priority=0
        flags = (0 << 3) | (1 << 2) | 0
        return pack("<BBB", self.sid, flags, 0x00)  # sid, flags, cmd=0x00

def parse_frame(buf: bytes) -> Tuple[str, Dict[str, Any]]:
    """
    Parse raw CRA frame (pre-SLIP). Returns (kind, meta).
      kind: "cmd", "ack", or "resp"
      meta: dict with keys:
        - for "cmd": sid, cmd, priority, payload
        - for "ack": sid
        - for "resp": sid, status (byte), payload (bytes)
    """
    if len(buf) < 3:
        raise ValueError("frame too short")
    sid, flags, cmd = unpack_from("<BBB", buf)
    af = (flags >> 2) & 1
    if af:
        # ACK-only
        return "ack", {"sid": sid}

    # Command or response
    if len(buf) < 5:
        raise ValueError("missing length field")
    length  = unpack_from("<H", buf, 3)[0]
    payload = buf[5:]
    if length != len(payload):
        raise ValueError(f"length mismatch: expected {length}, got {len(payload)}")

    if cmd == 0x00:
        # Response: first byte of payload is status
        status = payload[:1]
        return "resp", {"sid": sid, "status": status, "payload": payload[1:]}
    else:
        # Command
        priority = Priority(flags & 0x03)
        return "cmd", {
            "sid": sid,
            "cmd": cmd,
            "priority": priority,
            "payload": payload
        }
