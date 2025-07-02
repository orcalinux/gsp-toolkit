# src/gsp_cli/transport.py

import sys
import glob
from typer import Exit
from rich.console import Console
from rich.panel import Panel
from gsp_core.transport.uart import UARTTransport

console = Console()

def choose_port(port_opt: str, interactive: bool) -> str:
    if port_opt and not interactive:
        return port_opt

    if sys.platform.startswith("linux"):
        candidates = sorted(glob.glob("/dev/ttyACM*") + glob.glob("/dev/ttyUSB*"))
    elif sys.platform.startswith("win"):
        candidates = [f"COM{i}" for i in range(1, 20)]
    else:
        candidates = []

    if not candidates:
        console.print("[error] No serial ports found.")
        raise Exit(1)

    menu = "\n".join(f"{i}: {p}" for i, p in enumerate(candidates))
    console.print(Panel(menu, title="Available Serial Ports"))
    choice = console.input("Pick port index (enter number): ")
    try:
        return candidates[int(choice)]
    except (ValueError, IndexError):
        console.print("[error] Invalid selection.")
        raise Exit(1)

def get_transport(
    port: str,
    baud: int,
    timeout: float,
    interactive: bool
) -> UARTTransport:
    p = choose_port(port, interactive)
    console.print(f"[info] Using port: {p} @ {baud}bps, timeout={timeout}s")
    return UARTTransport(p, baud, timeout)
