"""Custom exceptions for the PDBAPI package."""


class PDBAPIError(Exception):
    """Base class for all PDBAPI exceptions.

    All exceptions raised by this library inherit from this class,
    allowing users to catch all PDBAPI-specific errors with a single
    exception handler.
    """
    pass


class PDBAPIInputError(PDBAPIError):
    """Exception raised for invalid input to PDBAPI functions.

    This exception is raised when function parameters fail validation,
    such as invalid PDB IDs, file formats, or other input parameters.
    """
    pass


class PDBAPIHTTPError(PDBAPIError):
    """Exception raised for HTTP request failures.

    This exception is raised when an HTTP request to the PDB API fails,
    including network errors, timeouts, or server errors.
    """
    pass


class PDBAPIFileError(PDBAPIError):
    """Exception raised for file I/O errors.

    This exception is raised when file writing or reading operations fail.
    """
    pass
