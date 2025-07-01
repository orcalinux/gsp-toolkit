# src/gsp_toolkit/ports.py

from serial.tools import list_ports
from typing import List, Tuple

def scan_serial_ports() -> List[Tuple[str,str]]:
    """
    Returns a list of (device, description) for all serial ports.
    E.g. [('/dev/ttyUSB0', 'FTDI FT232R USB UART'), ...]
    """
    return [(p.device, p.description) for p in list_ports.comports()]

def find_matching_ports(vid: int=None, pid: int=None, desc_filter: str=None) -> List[str]:
    """
    Filtered list of port names matching:
      • USB vendor ID (vid) and product ID (pid), OR
      • substring in the port description.
    """
    results = []
    for p in list_ports.comports():
        if vid and pid and (p.vid, p.pid) == (vid, pid):
            results.append(p.device)
        elif desc_filter and desc_filter.lower() in p.description.lower():
            results.append(p.device)
    return results
