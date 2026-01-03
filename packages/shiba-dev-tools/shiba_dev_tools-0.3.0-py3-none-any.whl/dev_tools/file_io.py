from __future__ import annotations

import contextlib
import os
import tempfile
from pathlib import Path


class TextFileIO:
    """
    A utility class for reading and writing text files with atomic write support.

    This class provides safe file I/O operations with the following features:
    - Atomic writes using temporary files and os.replace()
    - Automatic parent directory creation
    - Configurable encoding (defaults to UTF-8)
    - Proper cleanup on errors
    """

    def __init__(self, encoding: str = "utf-8") -> None:
        """
        Initialize the TextFileIO handler.

        Parameters:
            encoding (str): Character encoding to use for read/write operations. Defaults to "utf-8".
        """
        self.encoding = encoding

    def read(self, path: Path) -> str:
        """
        Read the entire contents of a text file.

        Parameters:
            path (Path): Path to the file to read.

        Returns:
            str: The complete file contents as a string.

        Raises:
            FileNotFoundError: If the file does not exist.
            PermissionError: If the file cannot be read due to permissions.
            UnicodeDecodeError: If the file cannot be decoded with the configured encoding.
        """
        return path.read_text(encoding=self.encoding)

    def write(self, path: Path, content: str) -> None:
        """
        Atomically write content to a file, ensuring parent directories exist.

        Writes the content to a temporary file adjacent to the target path and atomically
        replaces the target file with the temporary file using os.replace(). This approach
        prevents partial writes and ensures that readers never see incomplete data.

        The temporary file is created in the same directory as the target to ensure the
        atomic rename operation works correctly (os.replace requires both files to be
        on the same filesystem).

        Parameters:
            path (Path): Destination file path to write.
            content (str): Text content to write to the file.

        Raises:
            OSError: If directory creation, file writing, or atomic replacement fails.
            PermissionError: If insufficient permissions to write to the path or parent directory.
        """
        path.parent.mkdir(parents=True, exist_ok=True)

        tmp_file_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding=self.encoding,
                dir=path.parent,
                prefix=f".{path.name}.",
                suffix=".tmp",
                delete=False,
            ) as tmp_file:
                tmp_file_path = Path(tmp_file.name)
                tmp_file.write(content)
                tmp_file.flush()
                os.fsync(tmp_file.fileno())

            os.replace(tmp_file_path, path)
        finally:
            if tmp_file_path is not None and tmp_file_path.exists():
                with contextlib.suppress(OSError):
                    tmp_file_path.unlink()
