# src/gsp_cli/main.py

import argcomplete
import typer
from typer import Context, Option
from rich.console import Console
from rich.theme import Theme

from gsp_core.events import subscribe
from gsp_cli.transport import get_transport
from gsp_cli.interactive import run_menu

# your CLI commands
from gsp_cli.commands.bootloader_ops.erase import erase   as cmd_erase
from gsp_cli.commands.bootloader_ops.write import write   as cmd_write
from gsp_cli.commands.messaging.message       import message as cmd_message

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

def _print_event(name: str, payload: any) -> None:
    if name == "status":
        console.print(f"[status] {payload}")
    elif name == "progress":
        console.print(f"[info] transferred {payload} bytes…")
    elif name == "error":
        console.print(f"[error] {payload}[/error]")

# subscribe to core events (status, progress, error)
subscribe(_print_event)

@app.callback(invoke_without_command=True)
def main(
    ctx: Context,
    interactive: bool = Option(False, "-i", "--interactive", help="Launch interactive command menu")
):
    ctx.ensure_object(dict)
    ctx.obj["interactive"] = interactive

    # if `gsp -i` alone, show top‐level menu
    if interactive and ctx.invoked_subcommand is None:
        run_menu(app, [
            ("erase", cmd_erase),
            ("write", cmd_write),
            ("message", cmd_message),
        ], interactive)

    # guard against wrong flag placement: `gsp -i erase`
    if interactive and ctx.invoked_subcommand is not None:
        console.print("[error] The “--interactive” (-i) flag must come *after* the command name, not before.")
        console.print("Examples:\n  • gsp --interactive\n  • gsp erase --interactive\n  • gsp write -i")
        typer.echo(ctx.get_help())
        raise typer.Exit(1)

    # otherwise, let Typer dispatch the requested subcommand normally

# Register subcommands
app.command()(cmd_erase)
app.command()(cmd_write)
app.command()(cmd_message)

if __name__ == "__main__":
    app()
