# src/gsp_cli/commands/erase.py

import os
import typer
from typer import Context, Option
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.theme import Theme

from gsp_core.config import load_config
from gsp_core.protocol.codec import Priority
from gsp_core.client.highlevel import GSPClient, GSPTimeout

# Register custom Rich styles
theme = Theme({
    "info":    "bold cyan",
    "success": "bold green",
    "error":   "bold red",
})
console = Console(theme=theme)

def erase(
    ctx: Context,
    interactive: bool = Option(
        None, "-i", "--interactive", help="Interactive prompts for erase"
    ),
    priority: Priority = Option(
        Priority.NORMAL,
        "--priority", "-P",
        case_sensitive=False,
        help="Command priority: LOW, NORMAL, HIGH, or CRITICAL"
    ),
    address: int = Option(None, "-a", "--address", help="Start address to erase"),
    length: int = Option(None, "-l", "--length", help="Length in bytes to erase"),
    port: str = Option("", "-p", "--port", help="Serial port (e.g. /dev/ttyACM0)"),
    baud: int = Option(None, "-b", "--baud", help="Baud rate override"),
    timeout: float = Option(None, "-t", "--timeout", help="I/O timeout override (s)"),
):
    # Late‐import to break circular dependency:
    from gsp_cli.main import _get_transport

    # Determine interactive mode
    global_i   = ctx.find_root().obj.get("interactive", False)
    interactive = interactive if interactive is not None else global_i

    # Interactive prompts for missing address/length
    if interactive and address is None and length is None:
        console.print(
            Panel(
                f"[bold]GSP Erase Command Interactive Mode[/]\n\n"
                f"Current directory: [cyan]{os.getcwd()}[/]\n\n"
                "Ready to erase flash memory.",
                title="Erase",
                style="info"
            )
        )
        try:
            full = Prompt.ask("Full-chip erase?", choices=["y", "n"], default="y")
        except KeyboardInterrupt:
            console.print()  # blank line
            raise typer.Exit()

        if full.lower() == "n":
            try:
                addr_str   = Prompt.ask("Start address (hex)", default="0x08000000")
                length_str = Prompt.ask("Length in bytes",   default="65536")
            except KeyboardInterrupt:
                console.print()
                raise typer.Exit()

            try:
                address = int(addr_str,   0)
                length  = int(length_str, 0)
            except ValueError:
                console.print("[error]Invalid numeric input.[/error]")
                raise typer.Exit(1)

    # Load defaults from config if not provided
    cfg     = load_config()
    baud    = baud    or cfg["serial"]["baudrate"]
    timeout = timeout or cfg["serial"]["timeout"]

    transport = _get_transport(port, baud, timeout, interactive)
    client    = GSPClient(transport)

    try:
        console.print(Panel("Erasing flash…", style="info"))
        client.erase_flash(address, length, priority)
        console.print("[success]Flash erased successfully![/success]")
    except GSPTimeout as e:
        console.print(f"[error]Timeout: {e}[/error]")
    except Exception as e:
        console.print(f"[error]{e}[/error]")


if __name__ == "__main__":
    typer.run(erase)
