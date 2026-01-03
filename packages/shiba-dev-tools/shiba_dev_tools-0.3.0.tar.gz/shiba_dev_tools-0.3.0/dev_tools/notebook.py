from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import typer

from dev_tools.cli_utils import _die, _die_from, _ok, launch_editor, validate_safe_name
from dev_tools.file_io import TextFileIO
from dev_tools.paths import get_notebooks_dir

_file_io = TextFileIO(encoding="utf-8")


@dataclass
class ParsedArgs:
    """Parsed command line arguments for the nb command."""

    positional_args: list[str]
    flags: dict[str, str | bool]
    content_args: list[str]
    rename_arg: str | None


def _confirm_action(message: str) -> None:
    """
    Prompt user for confirmation and exit if they decline.

    Parameters:
        message (str): The confirmation message to display.

    Raises:
        SystemExit: Exits with code 0 if user declines.
    """
    if not typer.confirm(message, default=False):
        typer.echo("Cancelled")
        raise typer.Exit(0)


def _notebooks_dir() -> Path:
    """
    Return the path to the global notebooks directory.

    Returns:
        Path: Path to the global .sdt/notebooks directory (e.g., ~/.sdt/notebooks).
    """
    return get_notebooks_dir()


def _archive_dir() -> Path:
    """
    Return the path to the archive directory for soft-deleted categories.

    Returns:
        Path: Path to the global .sdt/notebooks/.archive directory (e.g., ~/.sdt/notebooks/.archive).
    """
    return _notebooks_dir() / ".archive"


def _list_dirs_in(path: Path, *, exclude: set[str] | None = None) -> list[str]:
    """
    List all directory names in the given path.

    Parameters:
        path (Path): Directory to list.
        exclude (set[str] | None): Set of directory names to exclude.

    Returns:
        list[str]: Sorted list of directory names.

    Raises:
        SystemExit: Exits if listing fails.
    """
    if not path.exists():
        return []

    exclude = exclude or set()
    dirs = []

    try:
        for item in path.iterdir():
            if item.is_dir() and item.name not in exclude:
                dirs.append(item.name)
    except Exception as exc:
        _die_from(exc, f"Error listing directories in '{path}': {exc}")

    return sorted(dirs)


def _get_category_path(category: str, *, must_exist: bool = True, archived: bool = False) -> Path:
    """
    Get and validate category path.

    Parameters:
        category (str): Category name.
        must_exist (bool): If True, die if category doesn't exist.
        archived (bool): If True, get path from archive directory.

    Returns:
        Path: Validated category path.

    Raises:
        SystemExit: Exits if validation fails or path doesn't exist when required.
    """
    validate_safe_name(category, name_type="category")
    base_dir = _archive_dir() if archived else _notebooks_dir()
    category_path = base_dir / category

    if must_exist and not category_path.exists():
        location = "archive" if archived else "active categories"
        _die(f"Error: Category '{category}' does not exist in {location}")

    return category_path


def _resolve_note_path(category: str, slug: str) -> Path:
    """
    Build and validate the full path to a note file.

    Parameters:
        category (str): Category name.
        slug (str): Note slug.

    Returns:
        Path: Validated absolute path to the note file.

    Raises:
        SystemExit: Exits if path validation fails or path traversal is detected.
    """
    validate_safe_name(category, name_type="category")
    validate_safe_name(slug, name_type="slug")

    notebooks = _notebooks_dir()
    note_path = notebooks / category / f"{slug}.txt"

    # Defense in depth: ensure the resolved path is within notebooks directory
    try:
        resolved = note_path.resolve()
        if not str(resolved).startswith(str(notebooks.resolve())):
            _die(f"Error: Path traversal detected for '{category}/{slug}'")
    except Exception as exc:
        _die_from(exc, f"Error: Could not resolve path for '{category}/{slug}': {exc}")

    return note_path


def _ensure_category_dir(category: str) -> None:
    """
    Create the category directory if it doesn't exist.

    Parameters:
        category (str): Category name.

    Raises:
        SystemExit: Exits if directory creation fails.
    """
    validate_safe_name(category, name_type="category")
    category_path = _notebooks_dir() / category

    try:
        category_path.mkdir(parents=True, exist_ok=True)
    except Exception as exc:
        _die_from(exc, f"Error creating category directory '{category}': {exc}")


def _list_notes_in_category(category: str) -> list[str]:
    """
    List all note slugs in a category.

    Parameters:
        category (str): Category name.

    Returns:
        list[str]: Sorted list of note slugs (without .txt extension).
    """
    validate_safe_name(category, name_type="category")
    category_path = _notebooks_dir() / category

    if not category_path.exists():
        return []

    try:
        notes = []
        for file_path in category_path.glob("*.txt"):
            if file_path.is_file():
                notes.append(file_path.stem)
        return sorted(notes)
    except Exception as exc:
        _die_from(exc, f"Error listing notes in category '{category}': {exc}")


def _handle_list_category(category: str) -> None:
    """
    List all note slugs in a category.

    Parameters:
        category (str): Category name.
    """
    notes = _list_notes_in_category(category)
    if not notes:
        typer.echo(f"No notes in category '{category}'")
        return
    for slug in notes:
        typer.echo(slug)


def _handle_read(category: str, slug: str) -> None:
    """
    Read and print note content (raw, pipeable).

    Parameters:
        category (str): Category name.
        slug (str): Note slug.

    Raises:
        SystemExit: Exits if note doesn't exist or can't be read.
    """
    note_path = _resolve_note_path(category, slug)
    if not note_path.exists():
        _die(f"Error: Note '{category}/{slug}' does not exist")

    try:
        content = _file_io.read(note_path)
    except Exception as exc:
        _die_from(exc, f"Error reading note: {exc}")

    # Print raw content (pipeable)
    typer.echo(content, nl=False)


def _handle_write(category: str, slug: str, content: str) -> None:
    """
    Write content to note.

    Parameters:
        category (str): Category name.
        slug (str): Note slug.
        content (str): Content to write.

    Raises:
        SystemExit: Exits if write fails.
    """
    note_path = _resolve_note_path(category, slug)

    # Ensure category directory exists
    _ensure_category_dir(category)

    try:
        _file_io.write(note_path, content)
    except Exception as exc:
        _die_from(exc, f"Error writing note: {exc}")

    _ok(f"✓ Note '{category}/{slug}' written")


def _handle_edit(category: str, slug: str) -> None:
    """
    Edit note in editor.

    Parameters:
        category (str): Category name.
        slug (str): Note slug.

    Raises:
        SystemExit: Exits if editor launch fails.
    """
    note_path = _resolve_note_path(category, slug)

    # Create empty note if doesn't exist
    if not note_path.exists():
        _ensure_category_dir(category)
        try:
            _file_io.write(note_path, "")
        except Exception as exc:
            _die_from(exc, f"Error creating note: {exc}")

    # Launch editor
    launch_editor(note_path)

    _ok(f"✓ Note '{category}/{slug}' edited")


def _handle_delete(category: str, slug: str) -> None:
    """
    Delete note with confirmation.

    Parameters:
        category (str): Category name.
        slug (str): Note slug.

    Raises:
        SystemExit: Exits if note doesn't exist or deletion fails.
    """
    note_path = _resolve_note_path(category, slug)

    if not note_path.exists():
        _die(f"Error: Note '{category}/{slug}' does not exist")

    _confirm_action(f"Delete note '{category}/{slug}'?")

    try:
        note_path.unlink()
    except Exception as exc:
        _die_from(exc, f"Error deleting note: {exc}")

    _ok(f"✓ Note '{category}/{slug}' deleted")


# Category management functions


def _list_categories(*, include_archived: bool = False) -> tuple[list[str], list[str]]:
    """
    List all categories, optionally including archived ones.

    Parameters:
        include_archived (bool): If True, return archived categories in second list.

    Returns:
        tuple[list[str], list[str]]: (active_categories, archived_categories)
    """
    # List active categories (exclude .archive directory)
    active_categories = _list_dirs_in(_notebooks_dir(), exclude={".archive"})

    # List archived categories if requested
    archived_categories = []
    if include_archived:
        archived_categories = _list_dirs_in(_archive_dir())

    return active_categories, archived_categories


def _handle_list_categories(*, include_archived: bool = False) -> None:
    """
    List all categories with color coding.

    Parameters:
        include_archived (bool): If True, also show archived categories.
    """
    active_categories, archived_categories = _list_categories(include_archived=include_archived)

    if not active_categories and not archived_categories:
        typer.echo("No categories found")
        return

    # Show active categories in green
    if active_categories:
        if include_archived:
            typer.echo("Active categories:")
        for category in active_categories:
            typer.secho(f"  {category}", fg=typer.colors.GREEN)

    # Show archived categories in red (if requested)
    if include_archived and archived_categories:
        if active_categories:
            typer.echo("")  # Add blank line between sections
        typer.echo("Archived categories:")
        for category in archived_categories:
            typer.secho(f"  {category}", fg=typer.colors.RED)


def _handle_delete_category(category: str) -> None:
    """
    Soft delete a category by moving it to .archive.

    Parameters:
        category (str): Category name to delete.

    Raises:
        SystemExit: Exits if category doesn't exist or deletion fails.
    """
    category_path = _get_category_path(category, must_exist=True)
    _confirm_action(f"Archive category '{category}' and all its notes?")

    # Ensure archive directory exists
    archive_dir = _archive_dir()
    try:
        archive_dir.mkdir(parents=True, exist_ok=True)
    except Exception as exc:
        _die_from(exc, f"Error creating archive directory: {exc}")

    # Move to archive
    archived_path = archive_dir / category
    if archived_path.exists():
        _die(f"Error: Category '{category}' already exists in archive")

    try:
        category_path.rename(archived_path)
    except Exception as exc:
        _die_from(exc, f"Error archiving category '{category}': {exc}")

    _ok(f"✓ Category '{category}' archived")


def _handle_rename_category(category: str, new_name: str) -> None:
    """
    Rename a category directory.

    Parameters:
        category (str): Current category name.
        new_name (str): New category name.

    Raises:
        SystemExit: Exits if category doesn't exist, new name exists, or rename fails.
    """
    category_path = _get_category_path(category, must_exist=True)
    new_path = _get_category_path(new_name, must_exist=False)

    if new_path.exists():
        _die(f"Error: Category '{new_name}' already exists")

    # Check if new name exists in archive
    archived_new_path = _get_category_path(new_name, must_exist=False, archived=True)
    if archived_new_path.exists():
        _die(f"Error: Category '{new_name}' exists in archive")

    try:
        category_path.rename(new_path)
    except Exception as exc:
        _die_from(exc, f"Error renaming category '{category}' to '{new_name}': {exc}")

    _ok(f"✓ Category '{category}' renamed to '{new_name}'")


def _handle_restore_category(category: str) -> None:
    """
    Restore an archived category.

    Parameters:
        category (str): Category name to restore.

    Raises:
        SystemExit: Exits if archived category doesn't exist or restore fails.
    """
    archived_path = _get_category_path(category, must_exist=True, archived=True)
    category_path = _get_category_path(category, must_exist=False)

    if category_path.exists():
        _die(f"Error: Category '{category}' already exists in active categories")

    try:
        archived_path.rename(category_path)
    except Exception as exc:
        _die_from(exc, f"Error restoring category '{category}': {exc}")

    _ok(f"✓ Category '{category}' restored")


def _get_flag_value_or_args(
    flag_value: str | bool, args_value: str | list[str] | None, *, flag_name: str, join_args: bool = False
) -> str:
    """
    Extract and validate flag value from either equals syntax or space-separated args.

    Parameters:
        flag_value: Value from flags dict (could be True or a string).
        args_value: Value from dedicated args (string or list of strings).
        flag_name: Name of the flag for error messages.
        join_args: If True, join list args with spaces.

    Returns:
        str: The extracted value.

    Raises:
        SystemExit: Exits if no valid value found.
    """
    # If we have a dedicated args value, use it
    if args_value:
        if isinstance(args_value, list):
            if join_args:
                return " ".join(args_value)
            return args_value[0] if args_value else ""
        return args_value

    # Otherwise, get from flag value
    if isinstance(flag_value, str):
        return flag_value

    # Flag is True but no value provided
    error_suffix = "content arguments" if flag_name == "write" else "a value"
    _die(f"Error: --{flag_name} requires {error_suffix}")


def _parse_nb_args(args: list[str]) -> ParsedArgs:
    """
    Parse arguments for the nb command.

    Parameters:
        args (list[str]): Command line arguments.

    Returns:
        ParsedArgs: Parsed arguments including positional args, flags, content args, and rename arg.

    Raises:
        SystemExit: Exits if invalid flags or syntax detected.
    """
    positional_args = []
    flags = {}
    content_args = []
    rename_arg = None

    i = 0
    while i < len(args):
        arg = args[i]
        if arg.startswith("--"):
            # Long flag
            if "=" in arg:
                key, value = arg[2:].split("=", 1)
                flags[key] = value
            else:
                flag_name = arg[2:]
                flags[flag_name] = True
                # If it's --write, collect remaining args as content
                if flag_name == "write":
                    content_args = args[i + 1 :]
                    break
                # If it's --rename, collect next arg as new name
                elif flag_name == "rename":
                    if i + 1 < len(args):
                        rename_arg = args[i + 1]
                        i += 1  # Skip the next arg since we consumed it
                    else:
                        _die("Error: --rename requires a new name")
        elif arg.startswith("-") and len(arg) > 1:
            # Short flag
            if "=" in arg:
                # Handle -r=value, -w=value syntax
                flag_char, value = arg[1:].split("=", 1)
                if flag_char == "r":
                    flags["restore"] = value
                elif flag_char == "w":
                    flags["write"] = value
                else:
                    _die(f"Error: Unknown flag '{arg}'")
            elif len(arg) == 2:
                flag_char = arg[1]
                # Map short flags to long flags
                if flag_char == "d":
                    flags["delete"] = True
                elif flag_char == "e":
                    flags["edit"] = True
                elif flag_char == "w":
                    flags["write"] = True
                    # Collect remaining args as content
                    content_args = args[i + 1 :]
                    break
                elif flag_char == "r":
                    # -r can be for rename (category-level) - collect next arg
                    if i + 1 < len(args):
                        flags["rename"] = True
                        rename_arg = args[i + 1]
                        i += 1  # Skip the next arg since we consumed it
                    else:
                        _die(
                            "Error: -r flag requires a value. "
                            "Use --restore=CATEGORY, -r=CATEGORY, or -r NEWNAME for rename"
                        )
                else:
                    _die(f"Error: Unknown flag '{arg}'")
            else:
                _die(f"Error: Invalid flag syntax '{arg}'")
        else:
            positional_args.append(arg)
        i += 1

    return ParsedArgs(
        positional_args=positional_args,
        flags=flags,
        content_args=content_args,
        rename_arg=rename_arg,
    )


# Create the nb command function
def nb_command(ctx: typer.Context, args: list[str]) -> None:
    """
    Notebook management - store and retrieve text notes organized by category.

    Usage:
      sdt nb                                      # List active categories
      sdt nb --archive                            # List all categories (including archived)
      sdt nb --restore=CATEGORY / -r=CATEGORY     # Restore archived category
      sdt nb {category}                           # List slugs in category
      sdt nb {category} --delete / -d             # Archive category
      sdt nb {category} --rename NEW_NAME / -r NEW_NAME  # Rename category (space syntax)
      sdt nb {category} --rename=NEW_NAME         # Rename category (equals syntax)
      sdt nb {category} {slug}                    # Read note
      sdt nb {category} {slug} --write / -w {content...}  # Write note (creates if needed)
      sdt nb {category} {slug} --write={content} / -w={content}  # Write note with = syntax
      sdt nb {category} {slug} --edit / -e        # Edit in editor
      sdt nb {category} {slug} --delete / -d      # Delete note

    Note: Categories and notes are created automatically when you write content.
    """
    # Parse command line arguments
    parsed = _parse_nb_args(args)
    positional_args = parsed.positional_args
    flags = parsed.flags
    content_args = parsed.content_args
    rename_arg = parsed.rename_arg

    # Handle global flags (no category specified)
    if not positional_args:
        if "archive" in flags:
            # sdt nb --archive - list all categories including archived
            _handle_list_categories(include_archived=True)
            return
        elif "restore" in flags:
            # sdt nb --restore=category - restore archived category
            category = flags["restore"]
            if not isinstance(category, str) or category is True:
                _die("Error: --restore requires a category name (e.g., --restore=mycat)")
            _handle_restore_category(category)
            return
        elif flags:
            _die(f"Error: Unknown flags: {', '.join(f'--{k}' for k in flags)}")
        else:
            # sdt nb - list active categories (new default behavior)
            _handle_list_categories(include_archived=False)
            return

    # Handle category-level operations (1 positional arg)
    category = positional_args[0]

    if len(positional_args) == 1:
        # Category-level operations
        if "delete" in flags:
            _handle_delete_category(category)
            return
        elif "rename" in flags:
            new_name = _get_flag_value_or_args(flags["rename"], rename_arg, flag_name="rename")
            _handle_rename_category(category, new_name)
            return
        elif flags:
            _die(f"Error: Unknown flags: {', '.join(f'--{k}' for k in flags)}")
        else:
            # No flags - list slugs in category
            _handle_list_category(category)
            return

    # Handle note operations (2+ positional args)
    elif len(positional_args) >= 2:
        slug = positional_args[1]

        # Check for note operation flags
        if "write" in flags:
            content = _get_flag_value_or_args(flags["write"], content_args, flag_name="write", join_args=True)
            _handle_write(category, slug, content)
            return

        elif "edit" in flags:
            _handle_edit(category, slug)
            return

        elif "delete" in flags:
            _handle_delete(category, slug)
            return

        elif flags:
            _die(f"Error: Unknown flags: {', '.join(f'--{k}' for k in flags)}")

        # No flags
        elif len(positional_args) == 2:
            # sdt nb {category} {slug} - read note
            _handle_read(category, slug)
            return
        else:
            # Too many positional args
            _die("Error: Too many arguments. Use flags for operations: --write, --edit, or --delete")
