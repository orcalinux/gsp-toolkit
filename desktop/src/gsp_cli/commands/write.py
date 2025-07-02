# src/gsp_cli/commands/write.py

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

from gsp_core.config import load_config
from gsp_core.client.highlevel import GSPClient, GSPTimeout
from gsp_core.protocol.cra import Priority

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
    priority: Priority = Option(
        Priority.NORMAL,
        "--priority", "-P",
        case_sensitive=False,
        help="Command priority (LOW, NORMAL, HIGH, CRITICAL)"
    ),
    port: str = Option("", "-p", "--port", help="Serial port"),
    baud: int = Option(None, "-b", "--baud", help="Baud rate override"),
    timeout: float = Option(None, "-t", "--timeout", help="I/O timeout override (s)"),
):
    """
    Upload a firmware image in 256-byte chunks, sending each chunk with the given priority.
    """
    # late-import to break circular dependency
    from gsp_cli.main import _get_transport

    # determine interactive flag
    global_i   = ctx.find_root().obj.get("interactive", False)
    interactive = interactive if interactive is not None else global_i

    # prompt for file if needed
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
        try:
            file = pt_prompt(
                prompt_text,
                completer=PathCompleter(expanduser=True),
                style=completion_style,
                complete_in_thread=True,
            )
        except KeyboardInterrupt:
            console.print()  # newline
            raise typer.Exit()

    # ensure we have a file
    if not file:
        console.print("[error]No file specified.[/error]")
        raise typer.Exit(1)

    # clean up path
    file = file.strip().strip("'\"")
    file = os.path.expanduser(file)

    # load config defaults
    cfg     = load_config()
    baud    = baud    or cfg["serial"]["baudrate"]
    timeout = timeout or cfg["serial"]["timeout"]

    # set up transport and client
    transport = _get_transport(port, baud, timeout, interactive)
    client    = GSPClient(transport)

    # read data
    try:
        data = open(file, "rb").read()
    except Exception as e:
        console.print(f"[error]Unable to open file: {e}[/error]")
        raise typer.Exit(1)

    error_offset = None
    error_msg    = ""

    # upload with progress, handle Ctrl+C
    try:
        with Progress() as prog:
            task = prog.add_task("[info]Uploading…[/info]", total=len(data))
            for i in range(0, len(data), 256):
                chunk = data[i : i + 256]
                try:
                    client.write_chunk(chunk, priority)
                except GSPTimeout as e:
                    error_offset = i
                    error_msg    = str(e)
                    break
                prog.update(task, advance=len(chunk))
    except KeyboardInterrupt:
        console.print()  # newline
        raise typer.Exit()

    # report any error_offset
    if error_offset is not None:
        console.print(f"\n[error]Write failed at offset {error_offset}: {error_msg}[/error]")
        raise typer.Exit(1)

    console.print("[success]Upload complete![/success]")


if __name__ == "__main__":
    typer.run(write)
