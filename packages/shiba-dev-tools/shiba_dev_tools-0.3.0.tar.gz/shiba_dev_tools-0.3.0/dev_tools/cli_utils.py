from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
from pathlib import Path
from typing import Any, NoReturn

import typer

from dev_tools.file_io import TextFileIO

_SAFE_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")
_file_io = TextFileIO(encoding="utf-8")


def validate_safe_name(name: str, *, name_type: str = "name") -> str:
    """
    Validate and normalize a name to prevent path traversal attacks and ensure filesystem safety.

    Performs comprehensive validation including:
    - Whitespace trimming and validation (no leading/trailing whitespace allowed)
    - Non-empty check
    - Path separator detection ("/" and "\\")
    - Directory traversal prevention ("..")
    - Character pattern enforcement (alphanumeric start, limited special chars, max 128 chars)

    Parameters:
        name (str): The name to validate (e.g., config name, category, slug).
        name_type (str): Type of name for error messages (e.g., "config", "category", "slug").

    Returns:
        str: The validated name (unchanged if validation passes).

    Raises:
        SystemExit: Exits with an error if the name is invalid.

    Example:
        validated = validate_safe_name("my-config.json", name_type="config")
    """
    candidate = name.strip()
    if candidate != name:
        _die(f"Error: Invalid {name_type} name (leading/trailing whitespace is not allowed).")

    if not candidate:
        _die(f"Error: Invalid {name_type} name (empty).")

    if "/" in candidate or "\\" in candidate:
        _die(f"Error: Invalid {name_type} name (must not contain '/' or '\\').")

    if ".." in candidate:
        _die(f"Error: Invalid {name_type} name (must not contain '..').")

    if not _SAFE_NAME_RE.fullmatch(candidate):
        _die(f"Error: Invalid {name_type} name (allowed: letters/digits and _ . -; must start with a letter/digit).")

    return candidate


def read_json_dict(path: Path, *, file_type: str = "JSON file") -> dict[str, Any]:
    """
    Read and parse a JSON file into a Python dictionary.

    Reads the file at the given path, parses it as JSON, and validates that the top-level
    value is a JSON object (dict). Exits with a descriptive error message if the file
    cannot be read, parsed, or if the top-level value is not an object.

    Parameters:
        path (Path): Path to the JSON file to read.
        file_type (str): Description of the file type for error messages (e.g., "config file", "JSON file").

    Returns:
        dict[str, Any]: The parsed top-level JSON object.

    Raises:
        SystemExit: Exits with an error message if the file cannot be read/parsed or if the
            top-level JSON value is not an object.

    Example:
        data = read_json_dict(Path("config.json"), file_type="config file")
    """
    try:
        data = json.loads(_file_io.read(path))
    except Exception as exc:
        _die_from(exc, f"Error reading {file_type} '{path}': {exc}")

    if not isinstance(data, dict):
        _die(f"Error: {file_type.capitalize()} '{path}' must contain a JSON object at the top level.")

    return data


def _exit_with_message(
    message: str,
    *,
    fg: str,
    code: int,
    exc: Exception | None = None,
    suppress_context: bool = False,
) -> NoReturn:
    """
    Print a colored message to the terminal and exit the program.

    Parameters:
        message (str): Message to print.
        fg (str): Foreground color name for the message.
        code (int): Exit code to use when terminating the process.
        exc (Exception | None): Optional exception to chain from; when provided, the exit is raised from this exception.
        suppress_context (bool): If True, suppress exception context by raising from None.

    Raises:
        typer.Exit: Exits the program with the specified code.
    """
    typer.secho(message, fg=fg)
    if exc is not None:
        raise typer.Exit(code=code) from exc
    if suppress_context:
        raise typer.Exit(code=code) from None
    raise typer.Exit(code=code)


def _die(message: str, *, code: int = 1) -> NoReturn:
    """
    Display an error message in red and exit with the given code.

    Parameters:
        message (str): The error message to display.
        code (int): Exit code to use (default: 1).
    """
    _exit_with_message(message, fg=typer.colors.RED, code=code)


def _die_from(exc: Exception, message: str, *, code: int = 1) -> NoReturn:
    """
    Print an error message in red and exit, preserving the original exception context.

    Parameters:
        exc (Exception): The originating exception to chain from.
        message (str): The user-facing error message to display.
        code (int): Exit code to use when terminating the program (default: 1).
    """
    _exit_with_message(message, fg=typer.colors.RED, code=code, exc=exc)


def _die_suppress(message: str, *, code: int = 1) -> NoReturn:
    """
    Print an error message in red and exit without chaining an exception.

    Parameters:
        message (str): The error message to display.
        code (int): Process exit code (default: 1).

    Raises:
        typer.Exit: Exits the program with the provided exit code.
    """
    _exit_with_message(message, fg=typer.colors.RED, code=code, suppress_context=True)


def _ok(message: str) -> None:
    """
    Print a success message to the terminal in green.

    Parameters:
        message (str): Text to display as a success/confirmation message.
    """
    typer.secho(message, fg=typer.colors.GREEN)


def show_help_callback(ctx: typer.Context) -> None:
    """
    Standard callback that shows help when no subcommand is invoked.

    This function is designed to be used as an app callback for Typer command groups.
    When a user runs a command group without specifying a subcommand, this callback
    will display the help text and exit cleanly.

    Parameters:
        ctx (typer.Context): The Typer invocation context for the current command.

    Example:
        app = typer.Typer()

        @app.callback(invoke_without_command=True)
        def callback(ctx: typer.Context) -> None:
            show_help_callback(ctx)
    """
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit(code=0)


def launch_editor(path: Path) -> None:
    """
    Launch the user's preferred editor to edit a file.

    Checks for VISUAL or EDITOR environment variables and uses them if set.
    Falls back to typer.launch() (which uses the system default) if neither is set.

    Parameters:
        path (Path): Path to the file to edit.

    Raises:
        SystemExit: Exits with an error if the editor cannot be launched.

    Example:
        launch_editor(Path("/path/to/file.txt"))
    """
    editor = os.environ.get("VISUAL") or os.environ.get("EDITOR")
    if editor:
        try:
            subprocess.run([*shlex.split(editor), str(path)], check=False)
        except Exception as exc:
            _die_from(exc, f"Error launching editor '{editor}': {exc}")
    else:
        typer.launch(str(path), wait=True)
