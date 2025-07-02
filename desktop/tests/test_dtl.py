# desktop/tests/test_dtl.py

import pytest
from gsp_core.protocol.dtl import encode_frame, decode_frame

def test_roundtrip_without_crc():
    cmd = b'\x01\x02\x03'
    frame = encode_frame(cmd, crc_enable=False)
    decoded, used_crc = decode_frame(frame)
    assert decoded == cmd
    assert used_crc is False

def test_roundtrip_with_crc():
    cmd = b'\x10\x20\x30\x40'
    frame = encode_frame(cmd, crc_enable=True)
    decoded, used_crc = decode_frame(frame)
    assert decoded == cmd
    assert used_crc is True

def test_crc_mismatch_raises():
    cmd = b'\xAA\xBB\xCC'
    frame = bytearray(encode_frame(cmd, crc_enable=True))
    # flip a bit to corrupt the CRC payload
    frame[3] ^= 0xFF
    with pytest.raises(ValueError, match="CRC mismatch"):
        decode_frame(bytes(frame))
