"""Utility functions for HTTP requests and file operations.

This module provides helper functions for making HTTP requests to the PDB API
and writing downloaded content to files.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, overload
from pathlib import Path

import pylinks

if TYPE_CHECKING:
    from pdbapi.typing import FileContentLike, PathLike

from .exception import PDBAPIFileError, PDBAPIHTTPError


def write_to_file(
    content: FileContentLike,
    filename: str,
    extension: str | None = None,
    path: PathLike | None = None
) -> Path:
    """Write content to a file with proper error handling.

    Creates the directory structure if it doesn't exist and writes the content
    to a file with the specified name and extension.

    Parameters
    ----------
    content
        Content to write to the file (string, bytes, or file-like object).
    filename
        Name of the file (without extension).
    extension
        File extension (with or without leading dot). If None, no extension is added.
    path
        Directory path where the file should be saved. If None, uses current working directory.
        The directory and all parent directories will be created if they don't exist.

    Returns
    -------
    pathlib.Path
        Absolute path to the written file.

    Raises
    ------
    PDBAPIFileError
        If file writing fails due to permissions, disk space, or other I/O errors.

    Examples
    --------
    >>> content = b"Hello, World!"
    >>> path = write_to_file(content, "hello", "txt", "/tmp/output")
    >>> print(path)
    /tmp/output/hello.txt
    """
    try:
        # Determine the target directory
        if path is None:
            dir_path = Path.cwd()
        else:
            dir_path = Path(path)
            # Create directory structure if it doesn't exist
            dir_path.mkdir(parents=True, exist_ok=True)

        # Build the full file path
        fullpath = (dir_path / filename).resolve()

        # Add extension if provided
        if extension is not None:
            ext = f".{extension.removeprefix('.')}" if extension else ""
            fullpath = fullpath.with_suffix(ext)

        # Determine write mode based on content type
        mode = "wb" if isinstance(content, bytes) else "w"

        # Write content to file
        with open(fullpath, mode) as f:
            f.write(content)

        return fullpath

    except (OSError, IOError) as e:
        raise PDBAPIFileError(
            f"Failed to write file '{filename}': {str(e)}"
        ) from e


@overload
def http_request(url: str, response_type: Literal["json"] = "json") -> dict: ...

@overload
def http_request(url: str, response_type: Literal["bytes"]) -> bytes: ...

@overload
def http_request(url: str, response_type: Literal["str"]) -> str: ...

def http_request(
    url: str,
    response_type: Literal["json", "bytes", "str"] = "json"
) -> dict | bytes | str:
    """Send HTTP request and get response in specified format.

    Makes an HTTP GET request to the specified URL and returns the response
    in the requested format (JSON dictionary, bytes, or string).

    Parameters
    ----------
    url
        Full URL of the API endpoint to query.
    response_type
        Format of the response to return:
        - 'json': Parse response as JSON and return dict (default)
        - 'bytes': Return raw response bytes
        - 'str': Return response as decoded string

    Returns
    -------
    dict, bytes, or str
        Response in the requested format.

    Raises
    ------
    PDBAPIHTTPError
        If the HTTP request fails (network error, 404, 500, etc.).

    Examples
    --------
    >>> # Get JSON data
    >>> data = http_request("https://data.rcsb.org/rest/v1/core/entry/4HHB")
    >>> print(data["entry"]["id"])
    4HHB

    >>> # Download binary file
    >>> content = http_request(
    ...     "https://files.rcsb.org/download/4HHB.cif.gz",
    ...     response_type="bytes"
    ... )
    """
    try:
        return pylinks.http.request(url=url, response_type=response_type)
    except Exception as e:
        raise PDBAPIHTTPError(
            f"HTTP request failed for URL '{url}': {str(e)}"
        ) from e
