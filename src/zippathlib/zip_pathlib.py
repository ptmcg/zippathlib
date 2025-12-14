#!/usr/bin/env python
"""
ZipPath - A pathlib.Path subclass for accessing files in ZIP archives

This module provides a standalone utility class for working with files inside
ZIP archives using a familiar pathlib-like interface.
"""
from __future__ import annotations

import contextlib
import fnmatch
import functools
import io
import os
from pathlib import Path, PurePosixPath, PurePath
import stat
from typing import BinaryIO, TextIO, Any, NamedTuple

from collections.abc import Iterator
import zipfile


class _ZipWriteFile:
    """
    A file-like object for writing to a file within a ZIP archive.

    This class buffers written data and updates the ZIP file when closed.
    """

    def __init__(self, zip_path: ZipPath, mode: str, encoding: str | None = None):
        """
        Initialize a _ZipWriteFile object.

        Args:
            zip_path: The ZipPath object representing the file to write
            mode: The file mode ('w', 'wb', 'a', 'ab')
            encoding: Text encoding for text modes
        """
        self.zip_path = zip_path
        self.mode = mode
        self.encoding = encoding
        self.closed = False

        # Create the appropriate buffer based on mode
        if 'b' in mode:  # Binary mode
            self.buffer = io.BytesIO()
        else:  # Text mode
            self.buffer = io.StringIO()

        # Check if we're appending and the file exists
        if 'a' in mode and zip_path.is_file():
            # Read existing content
            if 'b' in mode:
                existing_data = zip_path.read_bytes()
                self.buffer.write(existing_data)
            else:
                existing_text = zip_path.read_text(encoding=encoding or 'utf-8')
                self.buffer.write(existing_text)

    def write(self, data: str | bytes) -> int:
        """
        Write data to the buffer.

        Args:
            data: The data to write

        Returns:
            Number of characters/bytes written

        Raises:
            ValueError: If the file is closed
        """
        if self.closed:
            raise ValueError("I/O operation on closed file")
        return self.buffer.write(data)

    def close(self) -> None:
        """
        Close the file and update the ZIP archive.
        """
        if self.closed:
            return

        self.buffer.seek(0)

        # Get the data from the buffer
        if 'b' in self.mode:  # Binary mode
            data = self.buffer.read()
        else:  # Text mode
            text = self.buffer.read()
            data = text.encode(self.encoding or 'utf-8')

        # Update the ZIP file
        normalized_path = self.zip_path._normalize_path(self.zip_path._path)

        # Open the ZIP file in append mode
        with zipfile.ZipFile(
            self.zip_path.zip_file,
            mode='a',
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=9,
        ) as zf:
            zf.writestr(normalized_path, data)

        self.closed = True
        self.buffer.close()

    def __enter__(self) -> _ZipWriteFile:
        """Context manager enter method."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit method."""
        self.close()


class _ZipStat(NamedTuple):
    st_mode: int = 0
    st_ino: int = 0
    st_dev: int = 0
    st_nlink: int = 1
    st_uid: int = 65534  # nobody
    st_gid: int = 65534  # nogroup
    st_size: int = 0
    st_atime: int = 0
    st_mtime: int = 0
    st_ctime: int = 0


class ZipPath(PurePosixPath):
    """
    A pathlib.Path-like interface to files within a ZIP archive.

    This class allows you to navigate and access files within a ZIP archive
    using a familiar pathlib-like interface. It handles the details of opening
    and closing the ZIP file as needed.

    Examples:
        # Open a file from a ZIP archive
        zip_path = ZipPath('archive.zip', 'path/to/file.txt')
        with zip_path.open() as f:
            content = f.read()

        # List all files in a directory within the ZIP
        zip_path = ZipPath('archive.zip', 'some/directory')
        for file in zip_path.iterdir():
            print(file)

        # Check if a file exists in the ZIP
        if ZipPath('archive.zip', 'path/to/file.txt').exists():
            print("File exists!")
    """

    def __init__(self, zip_file: str | PurePath, path: str = '', mode="r") -> None:
        """
        Initialize a ZipPath object.

        Args:
            zip_file: Path to the ZIP file
            path: Path within the ZIP file (default: root of the ZIP)
        """
        super().__init__(path)
        self.zip_file = Path(zip_file)
        self._path = path
        self._mode = mode
        self._zipfile_stat = os.stat(self.zip_file)

    @classmethod
    def at_path(cls, source_path: Path, dest_path: Path = None) -> ZipPath:
        """
        ZIP archive creator, returning a ZipPath object for the newly-created ZIP archive
        """
        if dest_path is None:
            dest = source_path.parent / f"{source_path.stem}.zip"
        else:
            dest = dest_path

        if dest.exists():
            return ZipPath(dest)
        else:
            # print(f"Creating {dest}")
            with zipfile.ZipFile(
                dest,
                mode="w",
                compression=zipfile.ZIP_DEFLATED,
                compresslevel=9,
            ) as new_zf:
                for file in source_path.rglob("*"):
                    if file.is_file():
                        # print(f"adding {file}")
                        new_zf.write(
                            file,
                            file.relative_to(source_path.parent),
                        )
            ret = ZipPath(dest)
            return ret

    @property
    def _depth(self):
        """Internal property for recursion and tree formatting"""
        return self._path.count("/")

    def is_valid(self) -> bool:
        """
        Validation function to confirm that a ZipPath object is valid and the
        zip file exists.
        :return:
        """
        try:
            self._get_zipfile()
        except Exception:
            return False
        else:
            return True

    def __str__(self) -> str:
        """Return a string representation of the path."""
        return f"{self.zip_file}::{self._path}"

    def __repr__(self) -> str:
        """Return a detailed string representation of the path."""
        return f"ZipPath('{self.zip_file}', '{self._path}')"

    def _get_zipfile(self) -> zipfile.ZipFile:
        """
        Internal method to return the ZIP file that underlies the ZipPath object's file model.

        Returns:
            An open zipfile.ZipFile object

        Raises:
            FileNotFoundError: If the ZIP file doesn't exist
            zipfile.BadZipFile: If the file is not a valid ZIP file
        """
        if not self.zip_file.exists():
            raise FileNotFoundError(f"ZIP file not found: '{self.zip_file}'")
        return zipfile.ZipFile(self.zip_file, mode=self._mode)

    def _normalize_path(self, path: str) -> str:
        """
        Normalize a path within the ZIP file.

        Args:
            path: Path to normalize

        Returns:
            Normalized path
        """
        # Remove leading slash if present
        return path.removeprefix("/")

    def joinpath(self, *paths: str) -> ZipPath:
        """
        Join this path with one or more path components.

        Args:
            *paths: Path components to join

        Returns:
            A new ZipPath object with the joined path
        """
        new_path = PurePosixPath(self._path).joinpath(*paths)
        return ZipPath(self.zip_file, str(new_path), mode=self._mode)

    def __truediv__(self, key: str) -> ZipPath:
        """
        Join this path with another using the / operator.

        Args:
            key: Path component to join

        Returns:
            A new ZipPath object with the joined path
        """
        return self.joinpath(key)

    def exists(self) -> bool:
        """
        Check if this path exists in the ZIP file.

        Returns:
            True if the path exists, False otherwise
        """
        if not self.zip_file.exists():
            return False

        try:
            with self._get_zipfile() as zf:
                # For the root directory
                if not self._path:
                    return True

                # For files
                normalized_path = self._normalize_path(self._path)
                if normalized_path in zf.namelist():
                    return True

                # For directories (check if any file starts with this path)
                if not normalized_path.endswith('/'):
                    normalized_path += '/'

                for name in zf.namelist():
                    if name.startswith(normalized_path):
                        return True

                return False
        except zipfile.BadZipFile:
            return False

    def is_file(self) -> bool:
        """
        Check if this path is a file in the ZIP archive.

        Returns:
            True if the path is a file, False otherwise
        """
        if not self.zip_file.exists():
            return False

        try:
            with self._get_zipfile() as zf:
                normalized_path = self._normalize_path(self._path)
                return normalized_path in zf.namelist() and not normalized_path.endswith('/')
        except zipfile.BadZipFile:
            return False

    def is_dir(self) -> bool:
        """
        Check if this path is a directory in the ZIP archive.

        Returns:
            True if the path is a directory, False otherwise
        """
        if not self.zip_file.exists():
            return False

        if self.is_root():
            return True

        try:
            with self._get_zipfile() as zf:
                # Root directory
                if not self._path:
                    return True

                normalized_path = self._normalize_path(self._path)

                # Explicit directory entry
                if normalized_path.endswith('/'):
                    return normalized_path in zf.namelist()
                else:
                    dir_path = normalized_path + '/'
                    if dir_path in zf.namelist():
                        return True

                # Implicit directory (contains files)
                if any(name.startswith(dir_path) for name in zf.namelist()):
                    return True

                return False
        except zipfile.BadZipFile:
            return False

    def is_root(self) -> bool:
        """
        Boolean function for determining if the ZipPath object is at the root of
        the ZIP archive.
        """
        return self._path == ''

    def iterdir(self) -> Iterator[ZipPath]:
        """
        Iterate over the files and directories in this directory.

        Returns:
            An iterator of ZipPath objects

        Raises:
            NotADirectoryError: If this path is not a directory
        """
        if not self.is_dir():
            raise NotADirectoryError(f"Not a directory: {self}")

        with self._get_zipfile() as zf:
            prefix = self._normalize_path(self._path)
            if prefix and not prefix.endswith('/'):
                prefix += '/'

            # Track directories we've seen to avoid duplicates
            seen_dirs = set()

            for name in zf.namelist():
                if name.startswith(prefix):
                    # Get the relative path from the current directory
                    rel_path = name[len(prefix):]
                    if not rel_path:
                        continue

                    # Get the first component of the relative path
                    parts = rel_path.split('/', 1)
                    first_part = parts[0]

                    if len(parts) > 1:  # This is a subdirectory
                        if first_part not in seen_dirs:
                            seen_dirs.add(first_part)
                            yield ZipPath(self.zip_file, f"{prefix}{first_part}", mode=self._mode)
                    else:  # This is a file
                        yield ZipPath(self.zip_file, f"{prefix}{first_part}", mode=self._mode)

    def glob(self, pattern: str) -> Iterator[ZipPath]:
        """
        Iterate over paths matching a glob pattern.

        Args:
            pattern: Glob pattern to match

        Returns:
            An iterator of ZipPath objects matching the pattern
        """
        with self._get_zipfile() as zf:
            prefix = self._normalize_path(self._path)
            if prefix and not prefix.endswith('/'):
                prefix += '/'

            if pattern.startswith("**/"):
                list_src = zf.namelist()
                pattern = pattern.removeprefix("**/")
            else:
                list_src = [str(p).partition("::")[-1] for p in self.iterdir()]

            for name in list_src:
                if name.startswith(prefix):
                    # Get the relative path from the current directory
                    rel_path = name[len(prefix):]
                    if not rel_path:
                        continue

                    # Check if it matches the pattern
                    if fnmatch.fnmatch(rel_path, pattern):
                        yield ZipPath(self.zip_file, f"{prefix}{rel_path}")

    def riterdir(self) -> Iterator[ZipPath]:
        """
        Recursive iterator listing all files and directories in this directory and
        its subdirectories (depth first).
        """
        to_visit: list[ZipPath] = [self]
        while to_visit:
            current = to_visit.pop()
            yield current
            if current.is_dir():
                for entry in current.iterdir():
                    to_visit.append(entry)

    def rglob(self, pattern: str) -> Iterator[ZipPath]:
        """
        Recursive glob iterator listing all files and directories in this directory and its subdirectories
        that match the given pattern.

        Args:
            pattern: Glob pattern to match

        Returns:
            An iterator of ZipPath objects matching the pattern
        """
        for path in self.riterdir():
            if fnmatch.fnmatch(path.name, pattern):
                yield path

    def __iter__(self):
        return (line for line in self.read_text().splitlines())

    def open(self, mode: str = 'r', encoding: str | None = None) -> BinaryIO | TextIO:
        """
        Open the file pointed to by this path.

        Args:
            mode: Open mode ('r', 'rb', 'w', 'wb', etc.)
            encoding: Text encoding (for text modes)

        Returns:
            A file-like object

        Raises:
            FileNotFoundError: If the file doesn't exist in read mode
            IsADirectoryError: If the path points to a directory
        """
        # Reading modes
        if 'r' in mode and not any(c in mode for c in 'wa'):
            if not self.is_file():
                if self.is_dir():
                    raise IsADirectoryError(f"Is a directory: {self}")
                raise FileNotFoundError(f"File not found in ZIP: {self}")

            with self._get_zipfile() as zf:
                normalized_path = self._normalize_path(self._path)
                file_data = zf.read(normalized_path)

            if 'b' in mode:  # Binary mode
                return io.BytesIO(file_data)
            else:  # Text mode
                encoding = encoding or 'utf-8'
                return io.StringIO(file_data.decode(encoding))

        # Writing modes
        elif any(c in mode for c in 'wa'):
            if self.is_dir():
                raise IsADirectoryError(f"Is a directory: {self}")

            # For writing, we return a custom file-like object that will update the ZIP when closed
            if 'b' in mode:  # Binary mode
                return _ZipWriteFile(self, mode, None)
            else:  # Text mode
                encoding = encoding or 'utf-8'
                return _ZipWriteFile(self, mode, encoding)

        else:
            raise ValueError(f"Unsupported file mode: {mode}")

    def read_text(self, encoding: str = 'utf-8') -> str:
        """
        Read the contents of this file as text.

        Args:
            encoding: Text encoding

        Returns:
            The file contents as a string

        Raises:
            FileNotFoundError: If the file doesn't exist
            IsADirectoryError: If the path points to a directory
        """
        return self.read_bytes().decode(encoding)

    def write_text(self, data: str, encoding: str = 'utf-8') -> int:
        """
        Write text to this file.

        Args:
            data: The text to write
            encoding: Text encoding

        Returns:
            The number of characters written

        Raises:
            IsADirectoryError: If the path points to a directory
        """
        self._clear_cached_info()
        with self.open('wt', encoding=encoding) as f:
            return f.write(data)

    def read_bytes(self) -> bytes:
        """
        Read the contents of this file as bytes.

        Returns:
            The file contents as bytes

        Raises:
            FileNotFoundError: If the file doesn't exist
            IsADirectoryError: If the path points to a directory
        """
        with self.open('rb') as f:
            return f.read()

    def write_bytes(self, data: bytes) -> int:
        """
        Write bytes to this file.

        Args:
            data: The bytes to write

        Returns:
            The number of bytes written

        Raises:
            IsADirectoryError: If the path points to a directory
        """
        self._clear_cached_info()
        with self.open('wb') as f:
            return f.write(data)

    @property
    def parent(self) -> ZipPath:
        """
        Return the parent directory of this path.

        Returns:
            A ZipPath object pointing to the parent directory
        """
        parent_path = str(PurePath(self._path).parent)
        return ZipPath(self.zip_file, parent_path, mode=self._mode)

    @functools.cached_property
    def _info(self) -> zipfile.ZipInfo | None:
        from contextlib import closing

        if not self.is_file() or not self.exists():
            return None

        with closing(zipfile.ZipFile(self.zip_file)) as zf:
            info: zipfile.ZipInfo = zf.getinfo(self._path)

        return info

    def _clear_cached_info(self):
        with contextlib.suppress(AttributeError):
            del self._info

    def stat(self) -> os.stat_result:
        """
        Return a simulated stat.stat_result object for this file/directory.
        """
        if not self.exists():
            raise FileNotFoundError(f"File not found in ZIP: {self}")

        ret_st_mode = (
            (stat.S_IFDIR if self.is_dir() else stat.S_IFREG)
            | stat.S_IREAD
            | (stat.S_IWRITE if "w" in self._mode else 0)
        )

        if self.is_file():
            ret_st_size = self._info.file_size
        else:
            ret_st_size = 0

        ret_atime = ret_mtime = ret_ctime = int(self._zipfile_stat.st_mtime)

        return os.stat_result(
            _ZipStat(
                st_mode=ret_st_mode,
                st_size=ret_st_size,
                st_atime=ret_atime,
                st_mtime=ret_mtime,
                st_ctime=ret_ctime,
            )
        )

    def size(self) -> int:
        return self.stat().st_size

    def total_size(self) -> int:
        return sum(p.size() for p in self.riterdir())

    def rmdir(self) -> None:
        """Not supported."""
        raise NotImplementedError(f"{type(self).__name__} does not support removing directories")

    def unlink(self, *args) -> None:
        """Not supported."""
        raise NotImplementedError(f"{type(self).__name__} does not support removing files")

    def rename(self, *args) -> None:
        """Not supported."""
        raise NotImplementedError(f"{type(self).__name__} does not support renaming files or directories")

    def replace(self, *args) -> None:
        """Not supported."""
        raise NotImplementedError(f"{type(self).__name__} does not support replacing files or directories")

    def chmod(self, *args) -> None:
        """Not supported."""
        raise NotImplementedError(f"{type(self).__name__} does not support changing file permissions")
