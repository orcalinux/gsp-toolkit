# src/gsp_cli/interactive.py

import sys
from typer import Exit
from rich.console import Console
from rich.panel import Panel

console = Console()

def run_menu(app, commands: list[tuple[str, callable]], interactive: bool) -> None:
    """
    If interactive is True and no subcommand was invoked,
    present a numbered menu, then re‐invoke `app()` with the selection.
    Otherwise do nothing.
    """
    if not interactive:
        return

    menu = "\n".join(f"{i+1}. {name}" for i, (name, _) in enumerate(commands))
    console.print(Panel(menu, title="Available GSP Commands"))
    choice = console.input("Pick command number: ")
    try:
        name, fn = commands[int(choice) - 1]
    except (ValueError, IndexError):
        console.print("[error] Invalid selection.")
        raise Exit(1)

    # re-run CLI in interactive mode for that command
    sys.argv = ["gsp", name, "-i"]
    app()
    raise Exit()
