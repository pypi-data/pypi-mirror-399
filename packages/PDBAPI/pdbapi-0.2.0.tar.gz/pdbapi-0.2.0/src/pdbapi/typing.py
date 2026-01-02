"""Type aliases for the PDBAPI package.

This module defines common type aliases used throughout the package
to improve type hints and code readability.
"""

from pathlib import Path
from typing import IO, TypeAlias


# Path-like type for file system paths
PathLike: TypeAlias = str | Path
"""Type alias for file system paths.

Accepts either string paths or pathlib.Path objects.
"""

# File content type for reading/writing
FileContentLike: TypeAlias = str | bytes | IO
"""Type alias for file content.

Accepts strings, bytes, or file-like IO objects.
"""
