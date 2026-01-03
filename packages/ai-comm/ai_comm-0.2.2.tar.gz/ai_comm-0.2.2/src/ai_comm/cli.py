"""ai-comm CLI entry point."""

from __future__ import annotations

from typing import Annotated

import typer

from ai_comm import __version__
from ai_comm.commands import response, send, window


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"ai-comm {__version__}")
        raise typer.Exit()


HELP_TEXT = """\
Cross-AI CLI communication tool for Kitty terminal.

Enables AI assistants (Claude, Codex, Gemini, Aider, Cursor, OpenCode)
running in separate Kitty windows to communicate with each other.

IMPORTANT: Only use parameters documented here. Hidden/internal
parameters exist for debugging only and must never be used.

Workflow:
  1. ai-comm list-ai-windows     Find available AI windows
  2. ai-comm send <MESSAGE> -w <ID>  Send message and get response

Notes:
  - AI assistants MUST use ONLY the two Workflow commands without
    any additional parameters. Other parameters are forbidden for AI use.
  - For long responses, ask AI to write to a file in project directory
    (/tmp requires manual approval on target AI — avoid).
  - Blocking is intentional: AI cannot perceive time, only acts on user
    input. Non-blocking = lost messages. Timed-out commands auto-move
    to background; results return when ready.

Examples:
  ai-comm list-ai-windows
  ai-comm send "review this code" -w 5
  ai-comm send "write to review_$(date +%s).md" -w 8
"""

app = typer.Typer(
    name="ai-comm",
    help=HELP_TEXT,
    no_args_is_help=True,
    add_completion=False,
)


@app.callback()
def _app_callback(
    version: Annotated[
        bool,
        typer.Option("--version", "-V", callback=_version_callback, is_eager=True),
    ] = False,
) -> None:
    pass


# Public commands
app.command(name="send", help=send.SEND_HELP)(send.send)
app.command(name="list-ai-windows", help=window.LIST_HELP)(window.list_ai_windows)

# Public commands for async workflow
app.command(name="get-response", help=response.GET_RESPONSE_HELP)(response.get_response)

# Hidden commands (for debugging)
app.command(name="wait-idle", hidden=True)(response.wait_idle)
app.command(name="get-text", hidden=True)(response.get_text)


def main() -> None:
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
