#!/usr/bin/env python3
import os
import sys
import glob
import argcomplete
import typer
from typer import Context, Option
from rich.console import Console
from rich.panel import Panel
from rich.theme import Theme

from gsp_toolkit.config import load_config
from gsp_toolkit.transport.uart import UARTTransport
from gsp_toolkit.highlevel import GSPClient, GSPTimeout
from gsp_toolkit.events import subscribe

# Configure Rich with custom styles
console = Console(
    theme=Theme({
        "info":    "bold cyan",
        "error":   "bold red",
        "status":  "yellow",
        "success": "bold green",
    })
)

# Main Typer app
app = typer.Typer(
    name="gsp",
    help="GSP Toolkit CLI — host-side interface for the General Serial Protocol",
    add_completion=True,
)

# Enable Argcomplete for shell tab-completion
argcomplete.autocomplete(app)

# Hook SDK events into Rich
def _print_event(name, payload):
    if name == "status":
        console.print(f"[status] {payload}")
    elif name == "progress":
        console.print(f"[info] transferred {payload} bytes…")
subscribe(_print_event)

def _choose_port(port_opt: str, interactive: bool) -> str:
    if port_opt and not interactive:
        return port_opt

    # Discover candidate serial ports
    if sys.platform.startswith("linux"):
        candidates = sorted(glob.glob("/dev/ttyACM*") + glob.glob("/dev/ttyUSB*"))
    elif sys.platform.startswith("win"):
        candidates = [f"COM{i}" for i in range(1, 20)]
    else:
        candidates = []

    if not candidates:
        console.print("[error] No serial ports found.")
        raise typer.Exit(1)

    menu = "\n".join(f"{i}: {p}" for i, p in enumerate(candidates))
    console.print(Panel(menu, title="Available Serial Ports"))
    choice = console.input("Pick port index (enter number): ")
    try:
        return candidates[int(choice)]
    except (ValueError, IndexError):
        console.print("[error] Invalid selection.")
        raise typer.Exit(1)

def _get_transport(
    port:        str,
    baud:        int,
    timeout:     float,
    interactive: bool
) -> UARTTransport:
    p = _choose_port(port, interactive)
    console.print(f"[info] Using port: {p} @ {baud}bps, timeout={timeout}s")
    return UARTTransport(p, baud, timeout)

@app.callback(invoke_without_command=True)
def main(
    ctx: Context,
    interactive: bool = Option(False, "-i", "--interactive", help="Launch interactive command menu")
):
    """
    Top-level callback: stores the global `interactive` flag,
    and if no sub-command is given in interactive mode, shows a menu.
    """
    ctx.ensure_object(dict)
    ctx.obj["interactive"] = interactive

    # Interactive dispatch menu if no subcommand
    if interactive and ctx.invoked_subcommand is None:
        from cli.commands.erase import erase as cmd_erase
        from cli.commands.write import write as cmd_write

        commands = [("erase", cmd_erase), ("write", cmd_write)]
        menu = "\n".join(f"{i+1}. {name}" for i, (name, _) in enumerate(commands))
        console.print(Panel(menu, title="Available GSP Commands"))
        sel = console.input("Pick command number: ")
        try:
            idx = int(sel) - 1
            cmd_name, cmd_fn = commands[idx]
        except (ValueError, IndexError):
            console.print("[error] Invalid selection.")
            raise typer.Exit(1)

        # Re-invoke Typer with the chosen command in interactive mode
        sys.argv = ["gsp", cmd_name, "-i"]
        app()
        raise typer.Exit()

    # Guard: cannot mix -i with explicit subcommands+args
    if interactive and ctx.invoked_subcommand is not None:
        if interactive and ctx.invoked_subcommand is not None:
            console.print("[error] The “--interactive” (-i) flag must come *after* the command name, not before.")
            console.print("You can also run `gsp -i` alone to pick a command from the menu.")
            console.print("Examples:")
            console.print("  • gsp --interactive          # correct")
            console.print("  • gsp erase --interactive    # correct")
            console.print("  • gsp write -i               # correct")
            console.print("  • gsp -i erase               # wrong positioning\n")
            typer.echo(ctx.get_help())
            raise typer.Exit(1)
    # Otherwise, normal CLI flow continues to subcommands


# Import and register subcommands
from cli.commands.erase import erase as cmd_erase
from cli.commands.write import write as cmd_write

app.command()(cmd_erase)
app.command()(cmd_write)

if __name__ == "__main__":
    app()
