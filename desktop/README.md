# GSP Toolkit — Host‐Side CLI for General Serial Protocol

A Python-based command-line toolkit (`gsp`) for talking to embedded targets over UART (or TCP) using the General Serial Protocol (GSP). Supports firmware erase, upload, verify, reset, and abort operations, with both non-interactive and interactive modes, colored output, progress bars, and tab-completion.

---

## Features

- **Erase**, **Write**, **Verify**, **Reset**, **Abort** via simple commands
- **Interactive launcher** (`gsp -i`) with a numbered menu
- **Rich** colored output (`info`, `status`, `success`, `error`)
- **Progress bars** for chunked uploads
- **Configurable** defaults via `gsp.yaml` or `~/.gsp.yaml`
- **Automatic** Bash/Zsh tab-completion powered by `argcomplete`

---

## Installation

```bash
# create & activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# install from PyPI or locally editable
pip install gsp-toolkit
# or during development:
pip install -e .
```

Dependencies (pulled in automatically):

- `pyserial` (UART transport)
- `typer` (CLI framework)
- `rich` (colored output & progress bars)
- `PyYAML` (config files)
- `argcomplete` (tab-completion)

---

## Project Structure

```
desktop/
├── src/
│   ├── cli/
│   │   ├── main.py          # entrypoint & interactive launcher
│   │   └── commands/
│   │       ├── erase.py     # `gsp erase`
│   │       ├── write.py     # `gsp write`
│   │       └── …            # verify.py, run.py, abort.py
│   └── gsp_toolkit/
│       ├── config.py        # load `gsp.yaml` / defaults
│       ├── transport/
│       │   ├── uart.py      # serial transport
│       │   └── tcp.py       # TCP transport
│       ├── slip.py          # SLIP encoding/decoding
│       ├── crc.py           # CRC-16/CCITT-False
│       ├── cra.py           # GSP frame builder/parser
│       ├── dtl.py           # Data Transfer Layer
│       ├── events.py        # publish/subscribe hooks
│       └── highlevel.py     # `GSPClient` with retries & timeouts
├── gsp.yaml                 # example config file
├── pyproject.toml           # project metadata & entrypoint `gsp=cli.main:app`
└── README.md                # this file
```

---

## Configuration

Create a `gsp.yaml` in your project root (or `~/.gsp.yaml`) to override defaults:

```yaml
serial:
  port: "/dev/ttyACM0"
  baudrate: 115200
  timeout: 0.2
  vid: 0x0483 # optional USB vendor ID
  pid: 0x5740 # optional USB product ID
  desc_filter: "STM32" # optional substring match

tcp:
  host: "192.168.1.50"
  port: 4001
  timeout: 0.2
```

At runtime, command-line flags override config values.

---

## Usage

### Non-interactive

```bash
# show help
gsp --help

# erase entire flash
gsp erase

# erase region
gsp erase --address 0x08000000 --length 0x20000

# upload firmware.bin
gsp write firmware.bin

# specify port/baud/timeout on the fly
gsp write firmware.bin \
    --port /dev/ttyUSB1 \
    --baud 57600 \
    --timeout 0.5
```

### Interactive launcher

```bash
gsp -i
```

Will print a numbered list of commands:

```
╭─ Available GSP Commands ───────────────────╮
│ 1. erase                                   │
│ 2. write                                   │
│ 3. verify                                  │
│ 4. run                                     │
│ 5. abort                                   │
╰────────────────────────────────────────────╯
Pick command number:
```

Enter the number to invoke that command. You can combine `-i` with no other arguments only.

---

## Shell Completion

With `argcomplete` installed, add one line to your shell startup:

- **Bash** (`~/.bashrc`):

  ```bash
  eval "$(register-python-argcomplete gsp)"
  ```

- **Zsh** (`~/.zshrc`):

  ```bash
  autoload -U bashcompinit && bashcompinit
  eval "$(register-python-argcomplete gsp)"
  ```

Then restart or source your config:

```bash
source ~/.bashrc   # or ~/.zshrc
```

Now `<TAB><TAB>` after `gsp ` will complete commands and flags.

---

## Development & Testing

```bash
# run all tests
pytest -q

# format & lint
black .
flake8
```

---

## License

MIT © Mahmoud Abdelraouf
