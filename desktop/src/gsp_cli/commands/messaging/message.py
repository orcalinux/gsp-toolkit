# src/gsp_cli/commands/messaging/message.py

import typer
from typer import Context, Option
from rich.console import Console
from rich.panel import Panel
from enum import Enum

from gsp_core.client.highlevel import GSPClient, GSPTimeout
from gsp_core.protocol.commands import CMD_SEND_MESSAGE
from gsp_core.protocol.cra import Priority
from gsp_core.config import load_config
from gsp_cli.transport import get_transport

console = Console()

class PayloadFormat(str, Enum):
    ascii = "ascii"
    hex   = "hex"

def message(
    ctx: Context,
    payload: str = Option(
        ..., "-p", "--payload",
        help="The text or hex blob to send"
    ),
    fmt: PayloadFormat = Option(
        PayloadFormat.ascii, "-f", "--format",
        case_sensitive=False,
        help="Interpret payload as plain ASCII or as HEX digits"
    ),
    topic: int = Option(
        CMD_SEND_MESSAGE, "-c", "--cmd",
        help="Raw command ID (defaults to CMD_SEND_MESSAGE)"
    ),
    priority: Priority = Option(
        Priority.NORMAL, "-P", "--priority",
        case_sensitive=False,
        help="Command priority: LOW, NORMAL, HIGH, CRITICAL"
    ),
    port: str = Option(
        "", "-o", "--port",
        help="Serial port (e.g. /dev/ttyACM0)"
    ),
    baud: int = Option(
        None, "-b", "--baud",
        help="Baud rate override"
    ),
    timeout: float = Option(
        None, "-t", "--timeout",
        help="Timeout override (s)"
    ),
):
    """
    Send an arbitrary message to the board using CMD_SEND_MESSAGE.
    """
    # 1) load defaults
    cfg     = load_config()
    baud    = baud    or cfg["serial"]["baudrate"]
    timeout = timeout or cfg["serial"]["timeout"]

    # 2) build transport & client
    transport = get_transport(port, baud, timeout, ctx.obj.get("interactive", False))
    client    = GSPClient(transport)

    # 3) parse payload according to fmt
    if fmt == PayloadFormat.hex:
        try:
            # allow spaces, e.g. "DE AD BE EF"
            data = bytes.fromhex(payload.replace(" ", ""))
        except ValueError:
            console.print("[error]Invalid hex payload. Use only 0-9 A-F pairs.[/error]")
            raise typer.Exit(1)
    else:
        data = payload.encode("utf-8")

    # 4) send it
    try:
        console.print(Panel(f"Sending 0x{topic:02X} → {len(data)} bytes…", style="info"))
        client.send_message(data, priority)
        console.print("[success]Message sent![/success]")
    except GSPTimeout as e:
        console.print(f"[error]Timeout: {e}[/error]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")
        raise typer.Exit(1)
