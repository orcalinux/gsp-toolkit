#!/usr/bin/env python3
import os
import typer
from typer import Context, Option
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.theme import Theme

from gsp_toolkit.config import load_config
from gsp_toolkit.highlevel import GSPClient, GSPTimeout
from cli.main import _get_transport

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
    address: int = Option(None, "-a", "--address", help="Start address to erase"),
    length: int = Option(None, "-l", "--length", help="Length in bytes to erase"),
    port: str = Option("", "-p", "--port", help="Serial port (e.g. /dev/ttyACM0)"),
    baud: int = Option(None, "-b", "--baud", help="Baud rate override"),
    timeout: float = Option(None, "-t", "--timeout", help="I/O timeout override (s)"),
):
    """
    Erase flash (full or partial).
    When in interactive mode, will prompt for address/length if both are missing.
    """
    # allow sub-command to override global interactive flag
    global_i = ctx.find_root().obj.get("interactive", False)
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

        full = Prompt.ask("Full-chip erase?", choices=["y", "n"], default="y")
        if full.lower() == "n":
            addr_str = Prompt.ask("Start address (hex)", default="0x08000000")
            length_str = Prompt.ask("Length in bytes", default="65536")
            try:
                address = int(addr_str, 0)
                length = int(length_str, 0)
            except ValueError:
                console.print("[error]Invalid numeric input.[/error]")
                raise typer.Exit(1)

    # Load defaults from config if not provided
    cfg = load_config()
    baud = baud or cfg["serial"]["baudrate"]
    timeout = timeout or cfg["serial"]["timeout"]

    # Obtain transport and GSP client
    transport = _get_transport(port, baud, timeout, interactive)
    client = GSPClient(transport)

    try:
        console.print(Panel("Erasing flash…", style="info"))
        client.erase_flash(address, length)
        console.print("[success]Flash erased successfully![/success]")
    except GSPTimeout as e:
        console.print(f"[error]Timeout: {e}[/error]")
    except Exception as e:
        console.print(f"[error]{e}[/error]")


if __name__ == "__main__":
    typer.run(erase)
