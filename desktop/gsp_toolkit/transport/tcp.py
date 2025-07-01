# desktop/gsp_toolkit/transport/tcp.py

import socket
from .uart import _END  # reuse the SLIP END delimiter

class TCPTransport:
    """
    TCP-based transport for GSP frames.
    Frames are sent raw (SLIP-wrapped) and read back until the SLIP END delimiter.
    """
    def __init__(self, host: str, port: int, timeout: float = None):
        """
        :param host:    Remote hostname or IP
        :param port:    Remote TCP port
        :param timeout: Optional socket timeout in seconds
        """
        self.sock = socket.create_connection((host, port), timeout)

    def send(self, frame: bytes) -> None:
        """Send the entire SLIP-wrapped frame over TCP."""
        self.sock.sendall(frame)

    def recv_frame(self) -> bytes:
        """
        Read bytes one at a time until SLIP END (0xC0) is received.
        Returns the full frame (including END).
        """
        buf = bytearray()
        while True:
            b = self.sock.recv(1)
            if not b:
                # connection closed
                break
            buf += b
            if b == bytes([_END]):
                break
        return bytes(buf)
