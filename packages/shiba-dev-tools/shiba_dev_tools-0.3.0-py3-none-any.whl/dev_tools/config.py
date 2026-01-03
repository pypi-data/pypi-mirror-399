from __future__ import annotations

import contextlib
import json
import os
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import Any, Literal

import typer

from dev_tools.cli_utils import (
    _die,
    _die_from,
    _die_suppress,
    _ok,
    launch_editor,
    read_json_dict,
    show_help_callback,
    validate_safe_name,
)
from dev_tools.file_io import TextFileIO
from dev_tools.paths import get_configs_dir, get_default_config_path

app = typer.Typer(help="Configuration management commands")

_file_io = TextFileIO(encoding="utf-8")


@app.callback(invoke_without_command=True)
def _config_root(ctx: typer.Context) -> None:
    """
    Prints the command help and exits if no subcommand was invoked.

    Parameters:
        ctx (typer.Context): The Typer invocation context for the current command.
    """
    show_help_callback(ctx)


def _warn_if_config_invalid_json(path: Path) -> None:
    """
    Best-effort validation after external edits.

    After launching an external editor, the user may leave the file with invalid JSON (or a non-object top-level value).
    `_load_config` exits the CLI on parse/validation errors, so we catch that and warn instead.
    """
    try:
        _load_config(path)
    except typer.Exit:
        typer.secho(
            "Warning: Config file may contain invalid JSON.",
            fg=typer.colors.YELLOW,
        )


def _require_mutually_exclusive(*, a_flag: str, a_value: Any, b_flag: str, b_value: Any) -> None:
    """
    Ensure two mutually exclusive options are not both provided.

    If both `a_value` and `b_value` are not None, prints an error message instructing the user to use either `a_flag` or
    `b_flag` (not both) and exits the program.

    Parameters:
        a_flag (str): The command-line flag name for the first option (e.g., '--name').
        a_value (Any): The value provided for the first option, or None if not supplied.
        b_flag (str): The command-line flag name for the second option (e.g., '--config').
        b_value (Any): The value provided for the second option, or None if not supplied.
    """
    if a_value is not None and b_value is not None:
        _die(f"Error: Use either {a_flag} or {b_flag}, not both.")


def _default_config_data() -> dict[str, Any]:
    """
    Default configuration dictionary for new or missing config files.

    Returns:
        dict: A configuration mapping with keys:
            - "version": str version string (e.g., "1.0.0")
            - "settings": dict containing "debug" (bool) and "timeout" (int)
            - "features": dict containing "enabled" (list)
    """
    return {
        "version": "1.0.0",
        "settings": {
            "debug": False,
            "timeout": 30,
        },
        "features": {
            "enabled": [],
        },
    }


def _configs_dir() -> Path:
    """
    Get the path to the global .sdt/configs directory.

    Returns:
        path (Path): Path to the global `.sdt/configs` directory (e.g., ~/.sdt/configs).
    """
    return get_configs_dir()


def _named_config_path(name: str) -> Path:
    """
    Resolve the filesystem path for a named configuration file located under the tool's configs directory.

    Parameters:
        name (str): Config name; may include or omit the `.json` extension. The name is validated for allowed characters
            and disallowed path traversal.

    Returns:
        Path: Path to the config file under the configs directory with a `.json` extension appended if it was not
            provided.
    """
    name = validate_safe_name(name, name_type="config")
    filename = name if name.endswith(".json") else f"{name}.json"
    base_dir = _configs_dir()
    path = base_dir / filename

    # Defense in depth: ensure the resulting path cannot escape the intended directory even if validation regresses.
    base_resolved = base_dir.resolve(strict=False)
    path_resolved = path.resolve(strict=False)
    if not path_resolved.is_relative_to(base_resolved):
        _die("Error: Invalid config name (path traversal attempt).")

    return path


def _resolve_config_path(*, name: str | None, config_path: Path | None) -> Path:
    """
    Resolve which configuration file path to use based on the provided `name` or an explicit `config_path`.

    Parameters:
        name (str | None): Name of a named config stored under the configs directory; mutually exclusive with
            `config_path`.
        config_path (Path | None): Explicit path to a config file; mutually exclusive with `name`.

    Returns:
        Path: The resolved filesystem path — the named config path when `name` is provided, `config_path` when provided,
            or the default config path otherwise.
    """
    _require_mutually_exclusive(a_flag="--name", a_value=name, b_flag="--config", b_value=config_path)

    if name is not None:
        return _named_config_path(name)
    if config_path is not None:
        return config_path
    return get_default_config_path()


def _load_config(path: Path) -> dict[str, Any]:
    """
    Load a JSON configuration object from the given file path.

    Parameters:
        path (Path): Path to the configuration file to read.

    Returns:
        dict[str, Any]: The parsed top-level JSON object.

    Notes:
        If the file does not exist, cannot be parsed as JSON, or the top-level JSON value is not an object, the function
        will emit an error and exit the CLI.
    """
    if not path.exists():
        _die(f"Error: Config file '{path}' does not exist. Create one with: sdt config create")

    return read_json_dict(path, file_type="config file")


def _atomic_write_json(path: Path, data: Any) -> None:
    """
    Atomically write `data` as pretty-printed JSON to `path`, ensuring parent directories exist.

    Writes the JSON-serialized `data` (2-space indentation, trailing newline, UTF-8) to a temporary file adjacent to
    `path` and atomically replaces `path` with the temporary file to avoid partial writes.

    Parameters:
        path (Path): Destination file path to write.
        data (Any): JSON-serializable object to persist.
    """
    json_content = json.dumps(data, indent=2) + "\n"
    _file_io.write(path, json_content)


def _lock_path_for_config(config_path: Path) -> Path:
    return config_path.with_suffix(config_path.suffix + ".lock")


@contextlib.contextmanager
def _locked_config_internal(config_path: Path, *, mode: Literal["exclusive", "shared"] = "exclusive") -> Iterator[None]:
    """
    Internal implementation: Acquire an exclusive inter-process lock for config updates.

    We lock a sibling lockfile (not the config itself) so that atomic replaces of the config do not invalidate the lock.
    """
    lock_path = _lock_path_for_config(config_path)
    lock_path.parent.mkdir(parents=True, exist_ok=True)

    with open(lock_path, "a+b") as lock_file:
        lock_file.seek(0, os.SEEK_END)
        if lock_file.tell() == 0:
            lock_file.write(b"0")
            lock_file.flush()
        lock_file.seek(0)

        if os.name == "nt":
            import msvcrt

            lock_mode = msvcrt.LK_LOCK if mode == "exclusive" else msvcrt.LK_RLCK
            msvcrt.locking(lock_file.fileno(), lock_mode, 1)
            try:
                yield
            finally:
                msvcrt.locking(lock_file.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl

            lock_mode = fcntl.LOCK_EX if mode == "exclusive" else fcntl.LOCK_SH
            fcntl.flock(lock_file.fileno(), lock_mode)
            try:
                yield
            finally:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


@contextlib.contextmanager
def _locked_config(config_path: Path, *, mode: Literal["exclusive", "shared"] = "exclusive") -> Iterator[None]:
    """
    Acquire an inter-process lock for config updates with automatic error handling.

    Wraps the lock acquisition with OSError handling to provide consistent error messages.
    We lock a sibling lockfile (not the config itself) so that atomic replaces of the config
    do not invalidate the lock.

    Parameters:
        config_path (Path): Path to the config file to lock.
        mode (Literal["exclusive", "shared"]): Lock mode - "exclusive" for writes, "shared" for reads.

    Yields:
        None: Control is yielded while the lock is held.

    Raises:
        SystemExit: If the lock cannot be acquired (OSError), exits with error message.
    """
    try:
        with _locked_config_internal(config_path, mode=mode):
            yield
    except OSError as exc:
        _die_from(exc, f"Error locking config file '{config_path}': {exc}")


def _parse_list_index(part: str) -> int:
    try:
        return int(part)
    except ValueError as exc:
        raise ValueError(f"List index must be numeric, got: {part}") from exc


def _split_key_path(key_path: str) -> list[str]:
    """
    Split a dot-separated key path into non-empty segments.

    Parameters:
        key_path (str): Dot-separated path; surrounding whitespace is trimmed. Must not be empty.

    Returns:
        list[str]: List of path segments with empty segments removed.

    Raises:
        SystemExit: Exits with an error if `key_path` is empty after trimming.
    """
    key_path = key_path.strip()
    if not key_path:
        _die("Error: Path cannot be empty.")
    return [part for part in key_path.split(".") if part]


def _get_value_at_path(data: Any, parts: list[str]) -> Any:
    """
    Traverse nested dictionaries and lists following a dotted key path and return the value found at that path.

    Parameters:
        data (Any): The root data structure (expected to be composed of dicts and lists).
        parts (list[str]): Sequence of path segments; dict keys or list indices (as strings).

    Returns:
        Any: The value located at the end of the path.

    Raises:
        KeyError: If a required dict key is missing, or traversal encounters a non-dict/non-list where further traversal
            is required.
        IndexError: If a numeric list index is out of range.
        ValueError: If a list index path segment is not numeric.
    """
    cur: Any = data
    for part in parts:
        if isinstance(cur, dict):
            if part not in cur:
                raise KeyError(part)
            cur = cur[part]
            continue
        if isinstance(cur, list):
            idx = _parse_list_index(part)
            if idx < 0 or idx >= len(cur):
                raise IndexError(idx)
            cur = cur[idx]
            continue
        raise KeyError(part)
    return cur


def _set_value_at_path(data: dict[str, Any], parts: list[str], value: Any) -> None:
    """
    Set a value in a nested mapping/list structure using a list of path segments.

    The function traverses `data` following `parts` to reach the target location and assigns `value` there. Intermediate
    dictionaries are created for missing keys. When a traversal node is a list, each corresponding path segment must be
    a decimal integer index; list elements are replaced with an empty dict if they are not already a dict or list to
    allow further traversal.

    Parameters:
        data (dict[str, Any]): Root dictionary to modify in-place.
        parts (list[str]): Sequence of path segments leading to the target; the final segment is the key or list index
            to set.
        value (Any): Value to assign at the target location.

    Raises:
        KeyError: If traversal encounters a non-dict/non-list node where a container is required, or if a final
            container is neither a dict nor a list.
        IndexError: If a numeric index for a list is out of range or negative.
        ValueError: If a list index path segment is not numeric.
    """
    cur: Any = data
    for part in parts[:-1]:
        if isinstance(cur, dict):
            if part not in cur or not isinstance(cur[part], dict | list):
                cur[part] = {}
            cur = cur[part]
            continue

        if isinstance(cur, list):
            idx = _parse_list_index(part)
            if idx < 0:
                raise IndexError(idx)
            # Auto-grow lists to support paths like "items.0.name" on an empty list.
            while idx >= len(cur):
                cur.append({})
            if not isinstance(cur[idx], dict | list):
                cur[idx] = {}
            cur = cur[idx]
            continue

        raise KeyError(part)

    last = parts[-1]
    if isinstance(cur, dict):
        cur[last] = value
        return
    if isinstance(cur, list):
        idx = _parse_list_index(last)
        if idx < 0:
            raise IndexError(idx)
        # Allow setting list indices beyond current length by extending with nulls.
        while idx >= len(cur):
            cur.append(None)
        cur[idx] = value
        return
    raise KeyError(last)


def _unset_value_at_path(data: dict[str, Any], parts: list[str]) -> None:
    """
    Remove the value located at the given dot-path within the provided nested configuration dictionary.

    Parameters:
        data (dict[str, Any]): Root mapping to modify in-place.
        parts (list[str]): Sequence of path segments identifying the target location; numeric segments index lists.

    Raises:
        KeyError: If a required mapping key does not exist or the parent container is not a mapping/list when expected.
        IndexError: If a numeric list index is out of range.
    """
    if len(parts) == 1:
        key = parts[0]
        if key not in data:
            raise KeyError(key)
        del data[key]
        return

    parent = _get_value_at_path(data, parts[:-1])
    last = parts[-1]
    if isinstance(parent, dict):
        if last not in parent:
            raise KeyError(last)
        del parent[last]
        return
    if isinstance(parent, list):
        idx = _parse_list_index(last)
        if idx < 0 or idx >= len(parent):
            raise IndexError(idx)
        parent.pop(idx)
        return
    raise KeyError(last)


@app.command()
def create(
    name: str | None = typer.Option(  # noqa: B008
        None,
        "--name",
        "-n",
        help="Save as ~/.sdt/configs/{name}.json",
    ),
    output: Path | None = typer.Option(  # noqa: B008
        None,
        "--output",
        "-o",
        help="Path where the config file will be created (default: ~/.sdt/configs/config.json)",
    ),
    overwrite: bool = typer.Option(  # noqa: B008
        False,
        "--overwrite",
        "-f",
        help="Overwrite existing config file",
    ),
) -> None:
    """
    Create a new configuration file populated with the default JSON data.

    Parameters:
        name (str | None): If given, save as ~/.sdt/configs/{name}.json.
            Mutually exclusive with `output`.
        output (Path | None): Explicit filesystem path where the config will be created. If omitted and `name` is not
            provided, the default path ~/.sdt/configs/config.json is used.
        overwrite (bool): If True, overwrite an existing file at the target path; otherwise, fail if the file already
            exists.
    """
    _require_mutually_exclusive(a_flag="--name", a_value=name, b_flag="--output", b_value=output)

    if name is not None:
        output = _named_config_path(name)
    elif output is None:
        output = get_default_config_path()

    default_config = _default_config_data()

    try:
        with _locked_config(output):
            if output.exists() and not overwrite:
                _die(f"Error: Config file '{output}' already exists. Use --overwrite to replace it.")
            _atomic_write_json(output, default_config)
        _ok(f"✓ Config file created successfully at: {output.absolute()}")
    except Exception as exc:
        _die_from(exc, f"Error creating config file: {exc}")


@app.command()
def get(
    key_path: str | None = typer.Argument(  # noqa: B008
        None,
        help="Dot-path to read (e.g. settings.timeout). If omitted, prints the full config JSON.",
    ),
    name: str | None = typer.Option(  # noqa: B008
        None,
        "--name",
        "-n",
        help="Read from ~/.sdt/configs/{name}.json",
    ),
    config_path: Path | None = typer.Option(  # noqa: B008
        None,
        "--config",
        "-c",
        help="Path to the config JSON file (default: ~/.sdt/configs/config.json)",
    ),
    raw: bool = typer.Option(  # noqa: B008
        False,
        "--raw",
        help="Print scalar values without JSON quoting (objects/arrays still print as JSON).",
    ),
) -> None:
    """
    Read and print a value from the resolved configuration.

    If `key_path` is omitted, prints the entire configuration as formatted JSON. When `key_path` is provided, resolves
    the dotted path and prints the selected value; if `raw` is true and the value is a scalar or `None`, prints the raw
    value without JSON quoting. If the requested path does not exist, prints an error message and exits without raising
    an exception.

    Parameters:
        key_path (str | None): Dot-path to read (e.g. "settings.timeout"); if omitted, the full config is printed.
        name (str | None): Name of a stored config under ~/.sdt/configs (mutually exclusive with `config_path`).
        config_path (Path | None): Explicit path to a config JSON file (mutually exclusive with `name`).
        raw (bool): If true, print scalar values and `None` without JSON quoting.
    """
    path = _resolve_config_path(name=name, config_path=config_path)
    with _locked_config(path, mode="shared"):
        data = _load_config(path)

    if key_path is None:
        typer.echo(json.dumps(data, indent=2))
        return

    parts = _split_key_path(key_path)
    try:
        value = _get_value_at_path(data, parts)
    except ValueError as exc:
        _die_suppress(f"Error: {exc}")
    except (KeyError, IndexError):
        _die_suppress(f"Error: Path '{key_path}' not found in config.")

    if raw and (isinstance(value, str | int | float | bool) or value is None):
        typer.echo("" if value is None else str(value))
        return

    typer.echo(json.dumps(value, indent=2))


@app.command()
def set(
    key_path: str = typer.Argument(..., help="Dot-path to set (e.g. settings.timeout)"),  # noqa: B008
    value: str | None = typer.Argument(None, help="Value to set (ignored if --stdin)"),  # noqa: B008
    name: str | None = typer.Option(  # noqa: B008
        None,
        "--name",
        "-n",
        help="Write to ~/.sdt/configs/{name}.json",
    ),
    config_path: Path | None = typer.Option(  # noqa: B008
        None,
        "--config",
        "-c",
        help="Path to the config JSON file (default: ~/.sdt/configs/config.json)",
    ),
    json_value: bool = typer.Option(  # noqa: B008
        False,
        "--json",
        help='Parse the value as JSON (e.g. true, 123, [1,2], {"a":1}).',
    ),
    stdin: bool = typer.Option(  # noqa: B008
        False,
        "--stdin",
        help="Read the value from stdin.",
    ),
) -> None:
    """
    Set a configuration value at a dot-separated key path, creating intermediate objects or list elements as needed.

    Parameters:
        key_path (str): Dot-path locating the value to set (for example, "settings.timeout").
        value (str | None): Value to assign as a raw string; ignored if `stdin` is true.
        name (str | None): Target named config stored at ~/.sdt/configs/{name}.json.
        config_path (Path | None): Explicit path to the config file; takes precedence over the default path.
        json_value (bool): When true, parse the provided value (or stdin content) as JSON before storing.
        stdin (bool): When true, read the value from standard input instead of using the `value` argument.
    """
    path = _resolve_config_path(name=name, config_path=config_path)

    if stdin:
        raw_value = sys.stdin.read()
    else:
        if value is None:
            _die("Error: Missing VALUE (or use --stdin).")
        raw_value = value

    if json_value:
        try:
            parsed: Any = json.loads(raw_value)
        except Exception as exc:
            _die_from(exc, f"Error: Failed to parse VALUE as JSON: {exc}")
        new_value: Any = parsed
    else:
        new_value = raw_value

    parts = _split_key_path(key_path)
    try:
        with _locked_config(path):
            data = _load_config(path)
            _set_value_at_path(data, parts, new_value)
            _atomic_write_json(path, data)
    except ValueError as exc:
        _die_suppress(f"Error: {exc}")
    except (KeyError, IndexError):
        _die_suppress(f"Error: Invalid path '{key_path}'.")
    except Exception as exc:
        _die_from(exc, f"Error writing config file '{path}': {exc}")

    _ok(f"✓ Updated {key_path}")


@app.command()
def unset(
    key_path: str = typer.Argument(..., help="Dot-path to remove (e.g. settings.timeout)"),  # noqa: B008
    name: str | None = typer.Option(  # noqa: B008
        None,
        "--name",
        "-n",
        help="Write to ~/.sdt/configs/{name}.json",
    ),
    config_path: Path | None = typer.Option(  # noqa: B008
        None,
        "--config",
        "-c",
        help="Path to the config JSON file (default: ~/.sdt/configs/config.json)",
    ),
) -> None:
    """
    Remove a value from the JSON config at the given dot-path.

    If the final path segment is a numeric index and its parent is a list, the list element at that index is removed;
    otherwise the mapping key is deleted. The target config file is resolved from `--name` (writes to
    ~/.sdt/configs/{name}.json) or `--config`; if neither is given the default ~/.sdt/configs/config.json is used.

    Parameters:
        key_path (str): Dot-path to remove (e.g. "settings.timeout" or "items.2").
        name (str | None): Optional config name to resolve to ~/.sdt/configs/{name}.json.
        config_path (Path | None): Optional explicit path to the config JSON file.
    """
    parts = _split_key_path(key_path)
    path = _resolve_config_path(name=name, config_path=config_path)

    try:
        with _locked_config(path):
            data = _load_config(path)
            _unset_value_at_path(data, parts)
            _atomic_write_json(path, data)
    except (KeyError, IndexError, ValueError):
        _die_suppress(f"Error: Path '{key_path}' not found in config.")
    except Exception as exc:
        _die_from(exc, f"Error writing config file '{path}': {exc}")

    _ok(f"✓ Removed {key_path}")


@app.command()
def edit(
    name: str | None = typer.Option(  # noqa: B008
        None,
        "--name",
        "-n",
        help="Edit ~/.sdt/configs/{name}.json",
    ),
    config_path: Path | None = typer.Option(  # noqa: B008
        None,
        "--config",
        "-c",
        help="Path to the config JSON file (default: ~/.sdt/configs/config.json)",
    ),
    create_if_missing: bool = typer.Option(  # noqa: B008
        False,
        "--create",
        help="Create a default config file if it doesn't exist.",
    ),
    print_path: bool = typer.Option(  # noqa: B008
        False,
        "--print-path",
        help="Only print the resolved config path (useful for scripting).",
    ),
) -> None:
    """
    Open the resolved configuration file in the user's editor, optionally creating it or printing its path.

    Parameters:
        name (str | None): Optional named config identifier; resolves to ~/.sdt/configs/{name}.json.
        config_path (Path | None): Optional explicit path to the config JSON file; when provided, this path is used
            instead of a named config.
        create_if_missing (bool): If True, create a default config file when the resolved path does not exist.
        print_path (bool): If True, print the resolved config path and exit without launching an editor.
    """
    path = _resolve_config_path(name=name, config_path=config_path)
    if print_path:
        typer.echo(str(path))
        return

    if not path.exists():
        if not create_if_missing:
            _die(f"Error: Config file '{path}' does not exist (use --create or run: sdt config create).")
        with _locked_config(path):
            if not path.exists():
                _atomic_write_json(path, _default_config_data())

    launch_editor(path)
    _warn_if_config_invalid_json(path)
