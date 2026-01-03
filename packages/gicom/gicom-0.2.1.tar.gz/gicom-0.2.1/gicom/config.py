# config.py

import os
import json
import typer
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

console = Console()

APP_NAME = "gicom"
CONFIG_DIR = Path.home() / ".config" / APP_NAME
CONFIG_FILE = CONFIG_DIR / "config.json"


def get_api_key():
    """
    Load the API key from config, prompting the user if missing.

    Returns
    -------
    str
        The API key.
    """
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                key = data.get("api_key")
                if key:
                    return key
        except (json.JSONDecodeError, KeyError, IOError) as e:
            console.print(f"[yellow]Warning: Could not read config: {e}[/yellow]")
            pass

    console.print(
        Panel(
            "👋 Welcome to Gicom!\nWe need your OpenAI API Key to generate commits.",
            title="Setup",
            border_style="green",
        )
    )

    new_key = typer.prompt("Paste your API Key here (hidden)", hide_input=True)
    new_key = new_key.strip()

    save_api_key(new_key)
    return new_key


def save_api_key(key: str):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump({"api_key": key}, f)
    try:
        os.chmod(CONFIG_FILE, 0o600)
    except Exception:
        pass
    console.print(f"[bold green]✅ Key saved securely to {CONFIG_FILE}[/bold green]")
