# desktop/tests/test_tcp.py
import os, sys, pytest, socket
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, repo_root)

from src.gsp_toolkit.transport.tcp import TCPTransport, _END

class DummySocket:
    """
    Stores bytes written via sendall() and returns them byte-by-byte
    so TCPTransport.recv_frame() can reconstruct each SLIP frame.
    """
    def __init__(self, addr, timeout=None):
        self._buf = bytearray()

    def sendall(self, data: bytes):
        self._buf.extend(data)

    def recv(self, nbytes: int) -> bytes:
        if not self._buf:
            return b''
        # pop exactly one byte
        b = self._buf[:1]
        del self._buf[:1]
        return bytes(b)

@pytest.fixture(autouse=True)
def patch_socket(monkeypatch):
    monkeypatch.setattr(
        socket, "create_connection",
        lambda addr, timeout=None: DummySocket(addr, timeout)
    )
    yield

def test_tcp_single_frame():
    t = TCPTransport("127.0.0.1", 5000)
    frame = bytes([_END]) + b"HELLO" + bytes([_END])
    t.send(frame)
    assert t.recv_frame() == frame

def test_tcp_two_frames_back_to_back():
    t = TCPTransport("localhost", 6000)
    f1 = bytes([_END]) + b"ONE" + bytes([_END])
    f2 = bytes([_END]) + b"TWO" + bytes([_END])

    t.send(f1)
    t.send(f2)

    assert t.recv_frame() == f1
    assert t.recv_frame() == f2
