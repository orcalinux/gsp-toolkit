import pytest

from gsp_core.protocol.cra import CommandFrame, AckFrame, parse_frame, Priority


def test_command_frame_build_basic():
    # Test header only (no payload)
    frame = CommandFrame(sid=0x12, cmd=0x34, payload=b"", priority=Priority.NORMAL)
    raw = frame.build()
    # <BBBH: sid, flags, cmd, length>
    # flags = reserved=0, AF=0, priority=1
    expected_flags = (0 << 3) | (0 << 2) | Priority.NORMAL
    # pack 0x12, expected_flags, 0x34, length=0
    assert raw == bytes([0x12, expected_flags, 0x34, 0x00, 0x00])


def test_command_frame_build_with_payload():
    payload = b"ABC"
    frame = CommandFrame(sid=0x01, cmd=0xFF, payload=payload, priority=Priority.HIGH)
    raw = frame.build()
    expected_flags = (0 << 3) | (0 << 2) | Priority.HIGH
    # length = 3 => little endian 0x0003
    assert raw[:5] == bytes([0x01, expected_flags, 0xFF, 0x03, 0x00])
    assert raw[5:] == payload


def test_ack_frame_build():
    ack = AckFrame(sid=0xAB)
    raw = ack.build()
    # sid, flags=0b00000100, cmd=0x00
    expected_flags = (0 << 3) | (1 << 2) | 0
    assert raw == bytes([0xAB, expected_flags, 0x00])


@pytest.mark.parametrize(
    "buf, kind, meta", [
        # ACK-only frame
        (
            bytes([0x05, (1 << 2), 0x00]),
            "ack",
            {"sid": 0x05}
        ),
        # Command frame, NORMAL priority
        (
            bytes([0x10, 0x01, 0x22, 0x02, 0x00]) + b"ok",
            "cmd",
            {"sid": 0x10, "cmd": 0x22, "priority": Priority.NORMAL, "payload": b"ok"}
        ),
        # Response frame: cmd=0, status+payload
        (
            bytes([0xA0, 0x00, 0x00, 0x02, 0x00]) + b"\x01X",
            "resp",
            {"sid": 0xA0, "status": b"\x01", "payload": b"X"}
        ),
    ]
)
def test_parse_frame_various(buf, kind, meta):
    k, info = parse_frame(buf)
    assert k == kind
    for key, value in meta.items():
        assert info[key] == value


def test_parse_frame_length_mismatch():
    # Declared length 2 but actual payload length 1
    buf = bytes([0x01, 0x00, 0x00, 0x02, 0x00]) + b"Z"
    with pytest.raises(ValueError):
        parse_frame(buf)


def test_parse_frame_too_short():
    with pytest.raises(ValueError):
        parse_frame(b"\x01")


def test_parse_frame_priority_low():
    """
    Ensure that when flags = 0 (AF=0, priority=0), parse_frame
    yields Priority.LOW and empty payload for a command frame.
    """
    buf = bytes([0xAA, 0x00, 0x99, 0x00, 0x00])  # sid=0xAA, flags=0, cmd=0x99, len=0
    kind, info = parse_frame(buf)
    assert kind == "cmd"
    assert info["sid"] == 0xAA
    assert info["cmd"] == 0x99
    assert info["priority"] == Priority.LOW
    assert info["payload"] == b""
