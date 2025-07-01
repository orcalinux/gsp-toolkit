# desktop/tests/test_tcp.py

import pytest
import socket
from gsp_toolkit.transport.tcp import TCPTransport
from gsp_toolkit.transport.uart import _END

class DummySocket:
    """
    Dummy socket that echoes sent data back via recv().
    """
    def __init__(self, host_port, timeout):
        self._buffer = bytearray()

    def sendall(self, data: bytes):
        self._buffer.extend(data)

    def recv(self, nbytes: int) -> bytes:
        if not self._buffer:
            return b''
        # Pop one byte at a time
        b = self._buffer[:1]
        self._buffer = self._buffer[1:]
        return bytes(b)

@pytest.fixture(autouse=True)
def patch_socket(monkeypatch):
    """
    Monkey-patch socket.create_connection to return our DummySocket.
    """
    monkeypatch.setattr(socket, "create_connection", lambda addr, timeout=None: DummySocket(addr, timeout))
    yield

def test_tcp_send_and_recv():
    t = TCPTransport("127.0.0.1", 1234, timeout=0.1)
    frame = b"HELLO" + bytes([_END])
    t.send(frame)
    received = t.recv_frame()
    assert received == frame

def test_tcp_multiple_frames():
    t = TCPTransport("localhost", 5678)
    f1 = b"\xC0ONE\xC0"
    f2 = b"\xC0TWO\xC0"
    t.send(f1)
    t.send(f2)
    assert t.recv_frame() == f1
    assert t.recv_frame() == f2
