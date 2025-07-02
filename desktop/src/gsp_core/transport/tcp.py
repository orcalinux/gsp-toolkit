# desktop/gsp_core/transport/tcp.py

import socket

_END = 0xC0

class TCPTransport:
    """
    TCP-based transport for GSP frames.
    Reads a full SLIP-wrapped frame (with leading+trailing END) from a socket.
    """
    def __init__(self, host: str, port: int, timeout: float = None):
        self.sock = socket.create_connection((host, port), timeout)

    def send(self, frame: bytes) -> None:
        """Send the entire SLIP-wrapped frame over TCP."""
        self.sock.sendall(frame)

    def recv_frame(self) -> bytes:
        """
        Read bytes until we've seen two END (0xC0) delimiters:
        first marks frame start, second marks frame end.
        Returns the complete frame (including both ENDs).
        """
        buf = bytearray()
        ends_seen = 0

        while ends_seen < 2:
            b = self.sock.recv(1)
            if not b:
                # Connection closed or timeout; return what we have
                break
            buf.append(b[0])
            if b[0] == _END:
                ends_seen += 1

        return bytes(buf)
