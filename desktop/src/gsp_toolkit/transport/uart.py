# desktop/gsp_toolkit/transport/uart.py

import serial

_END = 0xC0

class UARTTransport:
    """
    UART transport for GSP frames.

    Sends raw SLIP‐wrapped frames and reads back until SLIP END.
    """
    def __init__(self, port: str, baudrate: int, timeout: float):
        """
        :param port:     Serial port (e.g. "/dev/ttyUSB0" or "COM3")
        :param baudrate: Baud rate (e.g. 115200)
        :param timeout:  Read timeout in seconds
        """
        self.ser = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)

    def send(self, frame: bytes) -> None:
        """
        Write a complete SLIP‐wrapped frame to UART.
        """
        self.ser.write(frame)

    def recv_frame(self) -> bytes:
        """
        Read bytes until SLIP END (0xC0) is received.
        Returns the full frame (including delimiter).
        """
        return self.ser.read_until(bytes([_END]))
