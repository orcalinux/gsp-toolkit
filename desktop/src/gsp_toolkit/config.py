import os
from pathlib import Path
import yaml

_DEFAULT = {
    "general": {
        "max_retries": 5,
    },
    "serial": {
        "port":        "/dev/ttyUSB0",
        "baudrate":    115200,
        "timeout":     0.2,
        "vid":         None,
        "pid":         None,
        "desc_filter": None,
    },
    "tcp": {
        "host":    None,
        "port":    0,
        "timeout": 0.2,
    }
}

def load_config() -> dict:
    """
    Load configuration in this order:
      1. Path from $GSP_CONFIG (if set and non-empty)
      2. ./gsp.yaml
      3. ~/.gsp.yaml
    Falls back to defaults if none found or on load errors.
    """
    paths = []
    env_path = os.getenv("GSP_CONFIG")
    if env_path:
        paths.append(Path(env_path))
    paths.extend([
        Path.cwd() / "gsp.yaml",
        Path.home() / ".gsp.yaml",
    ])

    cfg = { section: dict(vals) for section, vals in _DEFAULT.items() }
    for p in paths:
        if p.is_file():
            try:
                data = yaml.safe_load(p.read_text()) or {}
            except yaml.YAMLError:
                continue
            for section in ("serial", "tcp"):
                sec = data.get(section)
                if isinstance(sec, dict):
                    cfg[section].update(sec)
            break

    return cfg
