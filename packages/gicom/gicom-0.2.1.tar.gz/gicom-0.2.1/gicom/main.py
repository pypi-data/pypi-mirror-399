import subprocess
import typer
import pyperclip
from openai import OpenAI
from rich.console import Console
from rich.panel import Panel
from gicom.config import get_api_key
from typing import Optional

app = typer.Typer(no_args_is_help=True)
console = Console()


def get_git_diff() -> Optional[str]:
    """Return staged git diff. None means not a git repo."""
    try:
        subprocess.check_output(
            ["git", "rev-parse", "--is-inside-work-tree"], stderr=subprocess.DEVNULL
        )
    except subprocess.CalledProcessError:
        return None
    except FileNotFoundError:
        return None
    diff = (
        subprocess.check_output(["git", "diff", "--cached"], stderr=subprocess.STDOUT)
        .decode("utf-8", errors="replace")
        .strip()
    )
    return diff


def generate_text(diff: str) -> str:
    api_key = get_api_key().strip()
    if not api_key:
        raise RuntimeError("Missing OpenAI API key.")

    client = OpenAI(api_key=api_key)

    system_prompt = (
        "You are an expert developer. You are writing a git commit message for the provided diff. "
        "Follow the Conventional Commits specification (type(scope): subject). "
        "Common types: feat, fix, docs, style, refactor, test, chore. "
        "Rules:\n"
        "1. The first line must be under 50 characters.\n"
        "2. If the change is complex, add a bulleted body description.\n"
        "3. Do NOT output markdown code blocks (```). Just the raw text.\n"
        "4. Do NOT use backquote.\n"
        "5. Write like a human."
    )

    with console.status(
        "[bold green]🧠 AI is thinking...[/bold green]", spinner="dots"
    ):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": diff},
            ],
            temperature=0.3,
            max_tokens=200,
        )
    return (response.choices[0].message.content or "").strip()


def _ensure_diff_or_exit(diff: Optional[str]):
    if diff is None:
        console.print("[bold red]Error:[/bold red] Not a git repository.")
        raise typer.Exit(code=1)
    if not diff:
        console.print(
            "[bold yellow]⚠️ No staged changes.[/bold yellow] Run 'git add .' first."
        )
        raise typer.Exit(code=1)


@app.command(name="get-ai")
def get_ai():
    """Reads staged git changes, generates a message, and copies it to clipboard."""
    diff = get_git_diff()
    _ensure_diff_or_exit(diff)

    try:
        message = generate_text(diff)
    except Exception as e:
        console.print(f"[bold red]OpenAI error:[/bold red] {e}")
        raise typer.Exit(code=1)

    pyperclip.copy(message)
    console.print(
        Panel(
            message,
            title="[bold green]Copied to Clipboard![/bold green]",
            border_style="green",
        )
    )


@app.command()
def commit():
    """Generate a commit message and optionally commit."""
    diff = get_git_diff()
    _ensure_diff_or_exit(diff)

    try:
        msg = generate_text(diff)
    except Exception as e:
        console.print(f"[bold red]OpenAI error:[/bold red] {e}")
        raise typer.Exit(code=1)

    console.print(Panel(msg, title="Generated", border_style="blue"))

    if typer.confirm("🚀 Commit this?"):
        subprocess.run(["git", "commit", "-m", msg], check=False)
        console.print("[green]Done![/green]")
