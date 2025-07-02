# src/gsp_core/protocol/dlt.py

from typing import Tuple
from .slip import encode, decode
from .crc import crc16

def encode_frame(cmd_frame: bytes, crc_enable: bool = True) -> bytes:
    """
    Encapsulate a raw CRA frame into a SLIP-wrapped DTL packet.

    Packet layout before SLIP:
      • 1 byte  : header  = (CRC_EN << 7) | 0x00
      • N bytes : cmd_frame
      • [2 bytes: CRC-16 little-endian]  if crc_enable

    Returns SLIP-encoded bytes (adds leading & trailing END delimiters).
    """
    header = 0x80 if crc_enable else 0x00
    payload = bytes([header]) + cmd_frame
    if crc_enable:
        payload += crc16(payload).to_bytes(2, "little")
    return encode(payload)


def decode_frame(frame: bytes) -> Tuple[bytes, bool]:
    """
    Decode a SLIP-wrapped DTL packet back into the raw CRA frame.

    Steps:
      1. SLIP-decode (removes END delimiters & un-escapes).
      2. Read header byte: high bit = CRC_EN flag.
      3. If CRC_EN set, split off last 2 bytes as CRC and verify.
      4. Return (cmd_frame, crc_enable).

    Raises ValueError on malformed packet or CRC mismatch.
    """
    raw = decode(frame)
    if not raw:
        raise ValueError("DTL frame too short")

    crc_enable = bool(raw[0] & 0x80)
    content = raw[1:]

    if crc_enable:
        if len(content) < 2:
            raise ValueError("Missing CRC in DTL frame")
        data, recv_crc = content[:-2], int.from_bytes(content[-2:], "little")
        calc_crc = crc16(raw[:-2])  # header + data
        if recv_crc != calc_crc:
            raise ValueError(f"CRC mismatch: got 0x{recv_crc:04X}, expected 0x{calc_crc:04X}")
        cmd_frame = data
    else:
        cmd_frame = content

    return cmd_frame, crc_enable
