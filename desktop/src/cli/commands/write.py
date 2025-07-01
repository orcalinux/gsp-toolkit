#!/usr/bin/env python3
import os
import typer
from typer import Context, Argument, Option
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
from rich.theme import Theme
from prompt_toolkit import prompt as pt_prompt
from prompt_toolkit.completion import PathCompleter
from prompt_toolkit.styles import Style

from gsp_toolkit.config import load_config
from gsp_toolkit.highlevel import GSPClient, GSPTimeout
from cli.main import _get_transport

# Register custom Rich styles
theme = Theme({
    "info":    "bold cyan",
    "error":   "bold red",
    "status":  "yellow",
    "success": "bold green",
})
console = Console(theme=theme)

def write(
    ctx: Context,
    interactive: bool = Option(
        None, "-i", "--interactive", help="Interactive prompts for write"
    ),
    file: str = Argument(None, help="Path to binary file"),
    port: str = Option("", "-p", "--port", help="Serial port"),
    baud: int = Option(None, "-b", "--baud", help="Baud rate override"),
    timeout: float = Option(None, "-t", "--timeout", help="I/O timeout override (s)"),
):
    """
    Upload a firmware image in 256-byte chunks.
    When in interactive mode, will prompt for any missing arguments (with TAB-completion).
    """
    global_i = ctx.find_root().obj.get("interactive", False)
    interactive = interactive if interactive is not None else global_i

    if interactive and not file:
        console.print(
            Panel(
                f"[bold]GSP Write Command Interactive Mode[/]\n\n"
                f"Current directory: [cyan]{os.getcwd()}[/]\n\n"
                "Press TAB to autocomplete file paths.",
                title="Write",
                style="info"
            )
        )
        completion_style = Style.from_dict({
            "completion-menu.completion":         "bg:#444444 #cccccc",
            "completion-menu.completion.current": "bg:#88aa88 #000000",
            "scrollbar.background":               "bg:#444444",
            "scrollbar.button":                   "bg:#888888",
        })
        prompt_text = f"{os.getcwd()} > Path to binary file: "
        file = pt_prompt(
            prompt_text,
            completer=PathCompleter(expanduser=True),
            style=completion_style,
            complete_in_thread=True,
        )

    if not file:
        console.print("[error]No file specified.[/error]")
        raise typer.Exit(1)

    file = file.strip().strip("'\"")
    file = os.path.expanduser(file)

    cfg = load_config()
    baud = baud or cfg["serial"]["baudrate"]
    timeout = timeout or cfg["serial"]["timeout"]

    transport = _get_transport(port, baud, timeout, interactive)
    client = GSPClient(transport)

    try:
        data = open(file, "rb").read()
    except Exception as e:
        console.print(f"[error]Unable to open file: {e}[/error]")
        raise typer.Exit(1)

    error_offset = None
    error_msg = ""
    with Progress() as prog:
        task = prog.add_task("[info]Uploading…[/info]", total=len(data))
        for i in range(0, len(data), 256):
            chunk = data[i : i + 256]
            try:
                client.write_chunk(chunk)
            except GSPTimeout as e:
                error_offset = i
                error_msg = str(e)
                break
            prog.update(task, advance=len(chunk))

    if error_offset is not None:
        # ensure it's on its own line, then exit
        console.print(f"\n[error]Write failed at offset {error_offset}: {error_msg}[/error]")
        raise typer.Exit(1)

    console.print("[success]Upload complete![/success]")


if __name__ == "__main__":
    typer.run(write)
