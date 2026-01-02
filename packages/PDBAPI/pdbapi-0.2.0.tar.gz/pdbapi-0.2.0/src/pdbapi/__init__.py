"""PDBAPI: Retrieve data from the RCSB Protein Data Bank (PDB) web APIs.

PDBAPI is a Python library providing convenient access to the RCSB Protein Data Bank
(PDB) web APIs and file download services. It allows you to programmatically retrieve
structural data, metadata, sequences, validation reports, and various file formats
from the PDB archive.

The library is organized into two main modules:

- :mod:`pdbapi.data`: Query the RESTful Data API for metadata and annotations
- :mod:`pdbapi.file`: Download structure files and experimental data

Quick Start
-----------
>>> import pdbapi
>>>
>>> # Get entry metadata
>>> entry_data = pdbapi.data.entry("4HHB")
>>> print(entry_data["entry"]["id"])
4HHB
>>>
>>> # Download a structure file
>>> pdbapi.file.entry("4HHB", format="cif", output_path="./structures")

References
----------
- `RCSB PDB <https://www.rcsb.org/>`_
- `RCSB Programmatic Access <https://www.rcsb.org/docs/programmatic-access>`_
- `Data API <https://data.rcsb.org/>`_
- `Data API Documentation <https://data.rcsb.org/redoc/>`_
- `File Download Services <https://www.rcsb.org/docs/programmatic-access/file-download-services>`_
- `Python RCSB API (alternative) <https://github.com/rcsb/py-rcsb-api>`_

Notes
-----
This library requires an active internet connection to access the PDB APIs.
All API endpoints are subject to the RCSB PDB's terms of use and rate limits.

See Also
--------
pdbapi.data : Data API query functions
pdbapi.file : File download functions
pdbapi.exception : Custom exception classes
"""

from . import data, file
from .exception import PDBAPIError, PDBAPIInputError, PDBAPIHTTPError, PDBAPIFileError


__all__ = [
    # Modules
    "data",
    "file",
    # Exceptions
    "PDBAPIError",
    "PDBAPIInputError",
    "PDBAPIHTTPError",
    "PDBAPIFileError",
]
