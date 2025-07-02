#!/usr/bin/env python3
import sys
import glob
import argcomplete
import typer
from typer import Context, Option
from rich.console import Console
from rich.panel import Panel
from rich.theme import Theme

from gsp_core.transport.uart import UARTTransport
from gsp_core.events import subscribe

console = Console(
    theme=Theme({
        "info":    "bold cyan",
        "error":   "bold red",
        "status":  "yellow",
        "success": "bold green",
    })
)

app = typer.Typer(
    name="gsp",
    help="GSP Toolkit CLI — host-side interface for the General Serial Protocol",
    add_completion=True,
)
argcomplete.autocomplete(app)

def _print_event(name, payload):
    if name == "status":
        console.print(f"[status] {payload}")
    elif name == "progress":
        console.print(f"[info] transferred {payload} bytes…")
    elif name == "error":
        console.print(f"[error] {payload}[/error]")
subscribe(_print_event)

def _choose_port(port_opt: str, interactive: bool) -> str:
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
    ctx.ensure_object(dict)
    ctx.obj["interactive"] = interactive

    # 1) if -i alone, show top‐level menu
    if interactive and ctx.invoked_subcommand is None:
        from gsp_cli.commands.erase import erase as cmd_erase
        from gsp_cli.commands.write import write as cmd_write

        commands = [("erase", cmd_erase), ("write", cmd_write)]
        menu = "\n".join(f"{i+1}. {name}" for i, (name, _) in enumerate(commands))
        console.print(Panel(menu, title="Available GSP Commands"))
        try:
            sel = console.input("Pick command number: ")
        except KeyboardInterrupt:
            # Move to a clean new line and exit
            console.print()  # prints just "\n"
            raise typer.Exit()

        try:
            idx = int(sel) - 1
            cmd_name, cmd_fn = commands[idx]
        except (ValueError, IndexError):
            console.print("[error] Invalid selection.")
            raise typer.Exit(1)

        sys.argv = ["gsp", cmd_name, "-i"]
        app()
        raise typer.Exit()

    # 2) guard against `gsp -i erase`
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

    # otherwise, subcommands will fire normally

# register subcommands
from gsp_cli.commands.erase import erase as cmd_erase
from gsp_cli.commands.write import write as cmd_write

app.command()(cmd_erase)
app.command()(cmd_write)

if __name__ == "__main__":
    app()
