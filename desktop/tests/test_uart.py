# desktop/tests/test_uart.py

import pytest
import serial
from gsp_toolkit.transport.uart import UARTTransport

END = 0xC0

class DummySerial:
    """
    Minimal replacement for serial.Serial.
    Stores bytes written via write() and returns them frame-by-frame in read_until().
    """
    def __init__(self, port, baudrate, timeout):
        self._buf = bytearray()

    def write(self, data: bytes):
        self._buf.extend(data)

    def read_until(self, terminator: bytes) -> bytes:
        """
        Pop and return bytes up to, and including, the first terminator byte.
        If no terminator yet, return everything (plus one terminator) and clear.
        """
        if not self._buf:
            return terminator     # empty frame for safety

        # ensure we start from first byte
        try:
            idx = self._buf.index(terminator[0], 1)  # search from index 1 to allow leading END
        except ValueError:
            # no second terminator yet → flush whole buffer with one END
            result = bytes(self._buf) + terminator
            self._buf.clear()
            return result

        result = bytes(self._buf[: idx + 1])   # slice inclusive
        del self._buf[: idx + 1]               # consume
        return result


# ───────────────────────────────────────── fixtures ───────────────────────────────────────── #

@pytest.fixture(autouse=True)
def patch_serial(monkeypatch):
    """
    Replace serial.Serial with DummySerial for all tests in this module.
    """
    monkeypatch.setattr(serial, "Serial", DummySerial)
    yield


# ────────────────────────────────────────── tests ─────────────────────────────────────────── #

def test_uart_send_and_recv():
    t = UARTTransport(port="COM1", baudrate=9600, timeout=0.1)
    frame = b"HELLO" + bytes([END])
    t.send(frame)
    assert t.recv_frame() == frame


def test_multiple_frames():
    t = UARTTransport(port="COM2", baudrate=19200, timeout=0.5)
    f1 = b"\xC0ONE\xC0"
    f2 = b"\xC0TWO\xC0"

    t.send(f1)
    t.send(f2)

    assert t.recv_frame() == f1
    assert t.recv_frame() == f2
