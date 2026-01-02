"""Download various data files from the RCSB PDB.

This module provides comprehensive access to all RCSB PDB file download services,
including structure files, experimental data, validation reports, sequences,
chemical components, and derived data.

References
----------
- [RCSB File Download Services](https://www.rcsb.org/docs/programmatic-access/file-download-services)
- [wwPDB Archive Downloads](https://www.wwpdb.org/ftp/pdb-ftp-sites)
"""

from __future__ import annotations

import gzip
from pathlib import Path
from typing import TYPE_CHECKING, overload


from .util import write_to_file, http_request
from .exception import PDBAPIError, PDBAPIInputError

if TYPE_CHECKING:
    from typing import Literal
    from pdbapi.typing import PathLike

__all__ = [
    "entry",
    "entry_header",
    "assembly",
    "molecule",
    "molecule_instance",
    "molecule_bird",
    "dictionary",
    "ccd",
    "ccd_molstar",
    "validation_report",
    "structure_factors",
    "nmr_restraints",
    "nmr_restraints_v2",
    "nmr_chemical_shifts",
    "nmr_data_combined",
    "electron_density_map",
    "fasta_entry",
    "fasta_entity",
    "fasta_chain",
    "fasta_all_entries",
    "sequence_clusters",
]


@overload
def entry(
    pdb_id: str,
    assembly_id: int | str | None = None,
    *,
    format: Literal["cif", "pdb", "xml", "bcif"] = "cif",
    compressed: bool = True,
    output_path: None = None,
) -> bytes: ...

@overload
def entry(
    pdb_id: str,
    assembly_id: int | str | None = None,
    *,
    format: Literal["cif", "pdb", "xml", "bcif"] = "cif",
    compressed: bool = True,
    output_path: PathLike,
) -> Path: ...

def entry(
    pdb_id: str,
    assembly_id: int | str | None = None,
    *,
    format: Literal["cif", "pdb", "xml", "bcif"] = "cif",
    compressed: bool = True,
    output_path: PathLike | None = None,
) -> bytes | Path:
    """Download a PDB entry file in one of available formats.

    Parameters
    ----------
    pdb_id
        PDB ID of the entry.
    assembly_id
        Biological assembly ID of an assembly within the entry.
        If not provided (i.e. when set `None`; default), the asymmetric unit will be downloaded,
        otherwise the file containing the coordinates of the given assembly.
        Notice that many records are only available in the PDB file of the asymmetric unit.
    format
        Format of the entry file to download; one of:
        - `'cif'`: PDBx/mmCIF format
        - `'pdb'`: Legacy PDB format (see Notes below)
        - `'xml'`: PDBML/XML format
        - `'bcif'`: BinaryCIF format
    compressed
        Whether to download the gzip-compressed version (default: True).
        BinaryCIF files are always downloaded from a different server (models.rcsb.org).
    output_path
        Path to a local directory for storing the downloaded file.
        If the directory does not exist, it and all its necessary parent directories will be created.
        The filename will be the PDB ID, and the extension will be the same as the `format` argument.
        If not provided (i.e. when set `None`; default),
        the byte contents of the downloaded file will be returned.

    Returns
    -------
    bytes or pathlib.Path
        Either the content of the downloaded file in bytes (when `output_path` is `None`),
        or the full filepath of the stored file (when `output_path` is specified).

    Notes
    -----
    * Following entries don't have a corresponding PDB-format file:
      * Entries with multiple-character chain IDs.
      * Entries with more than 62 chains.
      * Entries with 100,000 or more atoms.
      * Entries with a complex beta sheet topology.

    References
    ----------
    * [RCSB File Download Services](https://www.rcsb.org/docs/programmatic-access/file-download-services)
    * [Structures Without Legacy PDB Format Files](https://www.rcsb.org/docs/general-help/structures-without-legacy-pdb-format-files)
    """

    # Validate inputs
    if not isinstance(pdb_id, str):
        raise PDBAPIInputError("`pdb_id` must be of type string.")
    if len(pdb_id) != 4:
        raise PDBAPIInputError("`pdb_id` must have 4 characters.")
    if not pdb_id[0].isnumeric() or pdb_id[0] == "0":
        raise PDBAPIInputError("First character of `pdb_id` must be a non-zero digit.")
    if format not in ("cif", "pdb", "xml", "bcif"):
        raise PDBAPIInputError(f"File format {format} not recognized.")

    # Build request URL
    if format == "bcif":
        # BinaryCIF is hosted on models.rcsb.org
        comp_suffix = ".gz" if compressed else ""
        url = f"https://models.rcsb.org/{pdb_id}.bcif{comp_suffix}"
        if assembly_id is not None:
            raise PDBAPIInputError("Biological assemblies are not available in BinaryCIF format.")
    else:
        # Standard files on files.rcsb.org
        comp_suffix = ".gz" if compressed else ""
        if assembly_id is None:
            filename = f"{pdb_id}.{format}{comp_suffix}"
        elif format == "cif":
            filename = f"{pdb_id}-assembly{assembly_id}.cif{comp_suffix}"
        elif format == "pdb":
            filename = f"{pdb_id}.pdb{assembly_id}{comp_suffix}"
        else:
            raise PDBAPIInputError("Biological assemblies can only be downloaded in CIF and PDB formats.")
        url = f"https://files.rcsb.org/download/{filename}"

    # Download file
    byte_content = http_request(url=url, response_type="bytes")

    # Decompress if needed
    if compressed:
        byte_content = gzip.decompress(byte_content)

    if output_path is None:
        return byte_content
    return write_to_file(
        content=byte_content, filename=pdb_id, extension=format, path=output_path
    )


@overload
def entry_header(
    pdb_id: str,
    *,
    format: Literal["cif", "pdb", "xml"] = "cif",
    output_path: None = None,
) -> bytes: ...

@overload
def entry_header(
    pdb_id: str,
    *,
    format: Literal["cif", "pdb", "xml"] = "cif",
    output_path: PathLike,
) -> Path: ...

def entry_header(
    pdb_id: str,
    *,
    format: Literal["cif", "pdb", "xml"] = "cif",
    output_path: PathLike | None = None,
) -> bytes | Path:
    """Download a PDB entry header file (summary data, no coordinates).

    Parameters
    ----------
    pdb_id
        PDB ID of the entry.
    format
        Format of the header file; one of 'cif', 'pdb', or 'xml'.
    output_path
        Path to a local directory for storing the downloaded file.
        If not provided, the byte contents will be returned.

    Returns
    -------
    bytes or pathlib.Path
        Either the content of the downloaded file in bytes (when `output_path` is `None`),
        or the full filepath of the stored file (when `output_path` is specified).

    References
    ----------
    * [RCSB File Download Services](https://www.rcsb.org/docs/programmatic-access/file-download-services)
    """
    if format not in ("cif", "pdb", "xml"):
        raise PDBAPIInputError(f"File format {format} not recognized.")

    pdb_id_lower = pdb_id.lower()
    if format == "xml":
        url = f"https://files.rcsb.org/download/{pdb_id_lower}-noatom.xml"
    else:
        url = f"https://files.rcsb.org/header/{pdb_id_lower}.{format}"

    byte_content = http_request(url=url, response_type="bytes")

    if output_path is None:
        return byte_content

    suffix = "-noatom" if format == "xml" else "-header"
    return write_to_file(
        content=byte_content, filename=f"{pdb_id}{suffix}", extension=format, path=output_path
    )


@overload
def assembly(
    pdb_id: str,
    assembly_id: int | str = 1,
    *,
    format: Literal["cif", "pdb"] = "cif",
    compressed: bool = True,
    output_path: None = None,
) -> bytes: ...

@overload
def assembly(
    pdb_id: str,
    assembly_id: int | str = 1,
    *,
    format: Literal["cif", "pdb"] = "cif",
    compressed: bool = True,
    output_path: PathLike,
) -> Path: ...

def assembly(
    pdb_id: str,
    assembly_id: int | str = 1,
    *,
    format: Literal["cif", "pdb"] = "cif",
    compressed: bool = True,
    output_path: PathLike | None = None,
) -> bytes | Path:
    """Download a biological assembly file.

    Alias for entry() with assembly_id specified. Provided for convenience and clarity.

    Parameters
    ----------
    pdb_id
        PDB ID of the entry.
    assembly_id
        Biological assembly ID (default: 1).
    format
        Format of the file; one of 'cif' or 'pdb'.
    compressed
        Whether to download the gzip-compressed version (default: True).
    output_path
        Path to a local directory for storing the downloaded file.
        If not provided, the byte contents will be returned.

    Returns
    -------
    bytes or pathlib.Path
        Either the content of the downloaded file in bytes (when `output_path` is `None`),
        or the full filepath of the stored file (when `output_path` is specified).

    References
    ----------
    * [RCSB File Download Services](https://www.rcsb.org/docs/programmatic-access/file-download-services)
    """
    return entry(
        pdb_id=pdb_id,
        assembly_id=assembly_id,
        format=format,
        compressed=compressed,
        output_path=output_path,
    )


@overload
def molecule(
    ccd_id: str,
    file_type: Literal["ideal_coords", "def"] = "ideal_coords",
    *,
    format: Literal["sdf", "cif"] = "sdf",
    output_path: None = None,
) -> bytes: ...

@overload
def molecule(
    ccd_id: str,
    file_type: Literal["ideal_coords", "def"] = "ideal_coords",
    *,
    format: Literal["sdf", "cif"] = "sdf",
    output_path: PathLike,
) -> Path: ...

def molecule(
    ccd_id: str,
    file_type: Literal["ideal_coords", "def"] = "ideal_coords",
    *,
    format: Literal["sdf", "cif"] = "sdf",
    output_path: PathLike | None = None,
) -> bytes | Path:
    """Download a small molecule (ligand/chemical component) file.

    Downloads chemical component files from the Chemical Component Dictionary (CCD).
    Only ideal coordinates and definition files are available through this endpoint.
    For coordinates from actual structures, use `molecule_instance()` instead.

    Parameters
    ----------
    ccd_id
        Chemical component ID (CCD ID) of the ligand (e.g., 'HEM', 'ATP', 'GTP').
    file_type
        Type of the file; one of:
        - `'ideal_coords'`: Ideal coordinates (SDF format only)
        - `'def'`: Definition file (CIF format only)
    format
        Output format; one of 'sdf' or 'cif'.
        Note: Ideal coordinates are only available in SDF format.
        Definition files are only available in CIF format.
    output_path
        Path to a local directory for storing the downloaded file.
        If the directory does not exist, it and all its necessary parent directories will be created.
        The filename will be the ligand ID, and the extension will be the format.
        If not provided (i.e. when set `None`; default),
        the byte contents of the downloaded file will be returned.

    Returns
    -------
    bytes or pathlib.Path
        Either the content of the downloaded file in bytes (when `output_path` is `None`),
        or the full filepath of the stored file (when `output_path` is specified).

    References
    ----------
    * [RCSB File Download Services](https://www.rcsb.org/docs/programmatic-access/file-download-services)
    * [Chemical Component Dictionary](https://www.wwpdb.org/data/ccd)

    See Also
    --------
    molecule_instance : Download chemical component coordinates from actual PDB structures
    """
    if format not in ("cif", "sdf"):
        raise PDBAPIInputError(f"File format {format} not recognized. Use 'sdf' or 'cif'.")
    if file_type not in ("ideal_coords", "def"):
        raise PDBAPIInputError(f"File type {file_type} not recognized. Use 'ideal_coords' or 'def'.")

    ligand_id_lower = ccd_id.lower()
    _URL_PREFIX_MOL = "https://files.rcsb.org/ligands/download/"

    if file_type == "def":
        if format != "cif":
            raise PDBAPIInputError("Definition files are only available in CIF format.")
        url = f"{_URL_PREFIX_MOL}{ligand_id_lower}.cif"
    else:  # ideal_coords
        if format != "sdf":
            raise PDBAPIInputError("Ideal coordinates are only available in SDF format.")
        url = f"{_URL_PREFIX_MOL}{ligand_id_lower}_ideal.sdf"

    byte_content = http_request(url=url, response_type="bytes")
    if output_path is None:
        return byte_content
    return write_to_file(
        content=byte_content, filename=ccd_id, extension=format, path=output_path
    )


@overload
def molecule_instance(
    pdb_id: str,
    *,
    label_comp_id: str | None = None,
    label_entity_id: int | str | None = None,
    label_asym_id: str | None = None,
    auth_comp_id: str | None = None,
    auth_asym_id: str | None = None,
    auth_seq_id: int | str | None = None,
    format: Literal["cif", "mol", "mol2", "sdf"] = "cif",
    output_path: None = None,
) -> bytes: ...

@overload
def molecule_instance(
    pdb_id: str,
    *,
    label_comp_id: str | None = None,
    label_entity_id: int | str | None = None,
    label_asym_id: str | None = None,
    auth_comp_id: str | None = None,
    auth_asym_id: str | None = None,
    auth_seq_id: int | str | None = None,
    format: Literal["cif", "mol", "mol2", "sdf"] = "cif",
    output_path: PathLike,
) -> Path: ...

def molecule_instance(
    pdb_id: str,
    *,
    label_comp_id: str | None = None,
    label_entity_id: int | str | None = None,
    label_asym_id: str | None = None,
    auth_comp_id: str | None = None,
    auth_asym_id: str | None = None,
    auth_seq_id: int | str | None = None,
    format: Literal["cif", "mol", "mol2", "sdf"] = "cif",
    output_path: PathLike | None = None,
) -> bytes | Path:
    """Download a small molecule (ligand/chemical component) instance from a specific structure.

    Parameters
    ----------
    pdb_id
        PDB ID of the entry.
    label_comp_id
        Chemical component ID if the ligand (optional).
    label_entity_id
        Entity ID of the ligand (optional).
    label_asym_id
        Asymmetric ID of the ligand (optional).
    auth_comp_id
        Author-provided chemical component ID of the ligand (optional).
    auth_asym_id
        Author-provided chain ID of the ligand (optional).
    auth_seq_id
        Author-provided sequence ID of the ligand (optional).
    format
        Output format; one of 'cif', 'mol', 'mol2', or 'sdf'.
    output_path
        Path to a local directory for storing the downloaded file.
        If not provided, the byte contents will be returned.

    Returns
    -------
    bytes or pathlib.Path
        Either the content of the file in bytes (when `output_path` is `None`),
        or the full filepath of the stored file (when `output_path` is specified).

    Notes
    -----
    * At least one of the optional mmCIF instance identifiers must be provided.
    * Any combination of identifiers can be used to specify the molecule instance.
      If the combination is ambiguous (i.e., matches multiple instances),
      the first matching instance will be returned.

    References
    ----------
    * [RCSB File Download Services](https://www.rcsb.org/docs/programmatic-access/file-download-services)
    """
    if format not in ("cif", "mol", "mol2", "sdf"):
        raise PDBAPIInputError(f"Format {format} not recognized. Use 'cif', 'mol', 'mol2', or 'sdf'.")

    # Build query parameters dynamically
    params = {}
    if label_comp_id is not None:
        params["label_comp_id"] = label_comp_id
    if label_entity_id is not None:
        params["label_entity_id"] = label_entity_id
    if label_asym_id is not None:
        params["label_asym_id"] = label_asym_id
    if auth_comp_id is not None:
        params["auth_comp_id"] = auth_comp_id
    if auth_asym_id is not None:
        params["auth_asym_id"] = auth_asym_id
    if auth_seq_id is not None:
        params["auth_seq_id"] = auth_seq_id

    if not params:
        raise PDBAPIInputError("At least one of the optional mmCIF instance identifiers must be provided.")

    # Build query string
    query_parts = [f"{key}={value}" for key, value in params.items()]
    query_string = "&".join(query_parts)

    url = f"https://models.rcsb.org/v1/{pdb_id}/ligand?{query_string}&encoding={format}"
    byte_content = http_request(url=url, response_type="bytes")

    if output_path is None:
        return byte_content

    # Build filename from provided identifiers
    filename_parts = [pdb_id] + [str(v) for v in params.values()]
    filename = "_".join(filename_parts)

    return write_to_file(
        content=byte_content,
        filename=filename,
        extension=format,
        path=output_path,
    )


@overload
def molecule_bird(
    bird_id: str,
    file_type: Literal["atom", "def"] = "def",
    *,
    output_path: None = None,
) -> bytes: ...

@overload
def molecule_bird(
    bird_id: str,
    file_type: Literal["atom", "def"] = "def",
    *,
    output_path: PathLike,
) -> Path: ...

def molecule_bird(
    bird_id: str,
    file_type: Literal["atom", "def"] = "def",
    *,
    output_path: PathLike | None = None,
) -> bytes | Path:
    """Download a BIRD (Biologically Interesting Molecule Reference Dictionary) file.

    Parameters
    ----------
    bird_id
        BIRD ID of the entry (e.g., 'PRD_000001' or '000001').
    file_type
        Type of the file; one of:
        - `'atom'`: Atom-site representation file
        - `'def'`: Definition file
    output_path
        Path to a local directory for storing the downloaded file.
        If not provided, the byte contents will be returned.

    Returns
    -------
    bytes or pathlib.Path
        Either the content of the downloaded file in bytes (when `output_path` is `None`),
        or the full filepath of the stored file (when `output_path` is specified).

    References
    ----------
    * [RCSB File Download Services](https://www.rcsb.org/docs/programmatic-access/file-download-services)
    """
    if file_type not in ("atom", "def"):
        raise PDBAPIInputError(f"File type {file_type} not recognized. Use 'atom' or 'def'.")

    id_upper = bird_id.upper()
    if id_upper.startswith("PRD_") or id_upper.startswith("PRDCC_"):
        bird_id = id_upper.split("_", 1)[1]
    id_prefix = "PRD" if file_type == "def" else "PRDCC"

    filename = f"{id_prefix}_{bird_id}"

    url = f"https://files.rcsb.org/birds/download/{filename}.cif"
    byte_content = http_request(url=url, response_type="bytes")

    if output_path is None:
        return byte_content
    return write_to_file(
        content=byte_content, filename=filename, extension="cif", path=output_path
    )


@overload
def ccd(
    variant: Literal["main", "protonation", "model"] = "main",
    *,
    output_path: None = None,
) -> bytes: ...

@overload
def ccd(
    variant: Literal["main", "protonation", "model"] = "main",
    *,
    output_path: PathLike,
) -> Path: ...

def ccd(
    variant: Literal["main", "protonation", "model"] = "main",
    *,
    output_path: PathLike | None = None,
) -> bytes | Path:
    """Download one of the Chemical Component Dictionary (CCD) variants.

    The CCD contains detailed chemical descriptions of all residues and small molecules
    in the PDB archive, including standard amino acids, nucleotides, and ligands.

    Parameters
    ----------
    variant
        Variant of the dictionary to download; one of:
        - `'main'`: Chemical Component Dictionary - complete CCD in mmCIF format
        - `'protonation'`: Protonation Variants Companion Dictionary - amino acid variants
        - `'model'`: Chemical Component Model Data - 3D model coordinates for components
    output_path
        Path to a local directory for storing the downloaded file.
        If the directory does not exist,
        it and all its necessary parent directories will be created.
        The filename will be the variant name, and the extension will be '.cif'.
        If not provided (i.e. when set `None`; default),
        the byte contents of the downloaded file will be returned.

    Returns
    -------
    bytes or pathlib.Path
        Either the content of the downloaded file in bytes (when `output_path` is `None`),
        or the full filepath of the stored file (when `output_path` is specified).

    Notes
    -----
    * The main CCD file is quite large (>500 MB uncompressed).
    * All files are downloaded compressed and automatically decompressed.

    References
    ----------
    * [Chemical Component Dictionary](https://www.wwpdb.org/data/ccd)
    * [RCSB File Download Services](https://www.rcsb.org/docs/programmatic-access/file-download-services)
    """
    if variant == "main":
        url = "https://files.wwpdb.org/pub/pdb/data/monomers/components.cif.gz"
        name = "components"
    elif variant == "protonation":
        url = "https://files.wwpdb.org/pub/pdb/data/monomers/aa-variants-v1.cif.gz"
        name = "aa-variants-v1"
    elif variant == "model":
        url = "https://files.wwpdb.org/pub/pdb/data/component-models/complete/chem_comp_model.cif.gz"
        name = "chem_comp_model"
    else:
        raise PDBAPIInputError(
            "Parameter `variant` of `chemical_component_dictionary` "
            "expects one of the following argument: ('main', 'protonation', 'model'). "
            f"The input argument was: {variant}."
        )

    byte_content = gzip.decompress(http_request(url=url, response_type="bytes"))
    if output_path is None:
        return byte_content
    return write_to_file(
        content=byte_content, filename=name, extension="cif", path=output_path
    )


@overload
def ccd_molstar(
    file_type: Literal["atom", "bond"] = "atom",
    *,
    output_path: None = None,
) -> bytes: ...

@overload
def ccd_molstar(
    file_type: Literal["atom", "bond"] = "atom",
    *,
    output_path: PathLike,
) -> Path: ...

def ccd_molstar(
    file_type: Literal["atom", "bond"] = "atom",
    *,
    output_path: PathLike | None = None,
) -> bytes | Path:
    """Download Chemical Component Dictionary (CCD) data in BinaryCIF format.

    Provides a subset of properties for all CCD components,
    used in Mol* ModelServer for efficient ligand rendering.

    Parameters
    ----------
    file_type
        Type of the file; one of:
        - `'atom'`: Atom properties, containing columns
           `atom_id`, `comp_id`, `charge`, and `pdbx_stereo_config`.
        - `'bond'`: Bond properties, containing columns
           `atom_id_1`, `atom_id_2`, `comp_id`,
           `molstar_protonation_variant`, `pdbx_aromatic_flag`,
           `pdbx_stereo_config`, and `value_order`.
    output_path
        Path to a local directory for storing the downloaded file.
        If not provided, the byte contents will be returned.

    Returns
    -------
    bytes or pathlib.Path
        Either the content of the file in bytes (when `output_path` is `None`),
        or the full filepath of the stored file (when `output_path` is specified).

    References
    ----------
    * [RCSB File Download Services](https://www.rcsb.org/docs/programmatic-access/file-download-services)
    * [Mol* ModelServer](https://molstar.org/docs/data-access-tools/model-server/)
    """
    filename = "cca" if file_type == "atom" else "ccb"
    url = f"https://models.rcsb.org/{filename}.bcif"
    byte_content = http_request(url=url, response_type="bytes")

    if output_path is None:
        return byte_content
    return write_to_file(
        content=byte_content, filename=filename, extension="bcif", path=output_path
    )


@overload
def dictionary(
    name: Literal[
        "pdbx_v50",
        "pdbx_v5_next",
        "pdbx_v40",
        "pdbx_vrpt",
        "ddl",
        "ihm",
        "em",
        "nmr-star",
        "img",
        "sas",
        "std",
        "biosync",
        "sim",
        "nef",
        "ndb_ntc",
    ] = "pdbx_v50",
    *,
    output_path: None = None,
) -> bytes: ...

@overload
def dictionary(
    name: Literal[
        "pdbx_v50",
        "pdbx_v5_next",
        "pdbx_v40",
        "pdbx_vrpt",
        "ddl",
        "ihm",
        "em",
        "nmr-star",
        "img",
        "sas",
        "std",
        "biosync",
        "sim",
        "nef",
        "ndb_ntc",
    ] = "pdbx_v50",
    *,
    output_path: PathLike,
) -> Path: ...

def dictionary(
    name: Literal[
        "pdbx_v50",
        "pdbx_v5_next",
        "pdbx_v40",
        "pdbx_vrpt",
        "ddl",
        "ihm",
        "em",
        "nmr-star",
        "img",
        "sas",
        "std",
        "biosync",
        "sim",
        "nef",
        "ndb_ntc",
    ] = "pdbx_v50",
    *,
    output_path: PathLike | None = None,
) -> bytes | Path:
    """Download one of the mmCIF dictionary files.

    mmCIF dictionaries define the data items and their relationships in mmCIF format files.

    Parameters
    ----------
    name
        Name of the dictionary to download; one of:
        - `'pdbx_v50'`: PDB Exchange Dictionary Version 5.0, supporting the data files
          in the current PDB archive.
        - `'pdbx_v5_next'`: The development version of the PDB Exchange Dictionary Version 5.0.
        - `'pdbx_v40'`: The prior version to the PDB Exchange Dictionary Version 5.0.
        - `'pdbx_vrpt'`: PDB Validation Report Dictionary, which is an extension of the
          PDBx/mmCIF dictionary to support the public validation reports.
        - `'ddl'`: Dictionary Description Language Version 2 (DDL2), supporting mmCIF
          and PDB Exchange Dictionary.
        - `'ihm'`: Integrative/Hybrid (I/H) methods extension dictionary, as an extension
          of the PDB Exchange Dictionary.
        - `'em'`: Community extension data dictionary describing 3D EM structures and
          experimental data deposited in the EMDB and PDB archives.
        - `'nmr-star'`: PDBx/mmCIF translation of the NMRSTAR data dictionary developed
          by the BioMagResBank.
        - `'img'`: Extension to the mmCIF dictionary describing image data collections
          and compact binary representations of diffraction image data.
        - `'sas'`: Draft data definitions for small-angle scattering applications.
        - `'std'`: Original IUCr mmCIF Dictionary.
        - `'biosync'`: Extension to the mmCIF dictionary describing the features of
          synchrotron facilities and beamlines.
        - `'sim'`: Dictionary describing crystallographic symmetry operations.
        - `'nef'`: Draft data definitions for NMR exchange format definitions.
        - `'ndb_ntc'`: The NDB NTC dictionary, which is an extension of the PDBx/mmCIF
          dictionary for DNATCO conformer analysis of nucleic acids.
    output_path
        Path to a local directory for storing the downloaded file.
        If the directory does not exist, it and all its necessary parent directories will be created.
        The filename will be the `name` argument, and the extension will be '.dic'.
        If not provided (i.e. when set `None`; default),
        the byte contents of the downloaded file will be returned.

    Returns
    -------
    bytes or pathlib.Path
        Either the content of the downloaded file in bytes (when `output_path` is `None`),
        or the full filepath of the stored file (when `output_path` is specified).

    References
    ----------
    * [mmCIF Dictionary Downloads](https://mmcif.wwpdb.org/dictionaries/downloads.html)
    * [RCSB File Download Services](https://www.rcsb.org/docs/programmatic-access/file-download-services)
    """
    byte_content = gzip.decompress(
        http_request(
            url=f"https://mmcif.wwpdb.org/dictionaries/ascii/mmcif_{name}.dic.gz",
            response_type="bytes",
        )
    )
    if output_path is None:
        return byte_content
    return write_to_file(
        content=byte_content, filename=name, extension="dic", path=output_path
    )


@overload
def validation_report(
    pdb_id: str,
    *,
    format: Literal["pdf", "xml", "cif"] = "xml",
    output_path: None = None,
) -> bytes: ...

@overload
def validation_report(
    pdb_id: str,
    *,
    format: Literal["pdf", "xml", "cif"] = "xml",
    output_path: PathLike,
) -> Path: ...

def validation_report(
    pdb_id: str,
    *,
    format: Literal["pdf", "xml", "cif"] = "xml",
    output_path: PathLike | None = None,
) -> bytes | Path:
    """Download a validation report file.

    Parameters
    ----------
    pdb_id
        PDB ID of the entry.
    format
        Format of the validation report; one of 'pdf', 'xml', or 'cif'.
        Default is 'xml'.
    output_path
        Path to a local directory for storing the downloaded file.
        If not provided, the byte contents will be returned.

    Returns
    -------
    bytes or pathlib.Path
        Either the content of the downloaded file in bytes (when `output_path` is `None`),
        or the full filepath of the stored file (when `output_path` is specified).

    Notes
    -----
    * All validation report files are stored compressed (.gz) and automatically decompressed.
    * Files are downloaded from the wwPDB validation reports archive.

    References
    ----------
    * [RCSB File Download Services](https://www.rcsb.org/docs/programmatic-access/file-download-services)
    * [wwPDB Validation Reports](https://www.wwpdb.org/validation/validation-reports)
    """
    if format not in ("pdf", "xml", "cif"):
        raise PDBAPIInputError(f"File format {format} not recognized.")

    # Validation reports use middle two characters for directory structure
    # and require lowercase PDB IDs. All files are stored compressed (.gz)
    pdb_id_lower = pdb_id.lower()
    mid_chars = pdb_id_lower[1:3]

    # All validation report files are gzip compressed
    url = f"https://files.rcsb.org/pub/pdb/validation_reports/{mid_chars}/{pdb_id_lower}/{pdb_id_lower}_validation.{format}.gz"

    byte_content = http_request(url=url, response_type="bytes")

    # Decompress the gzipped content
    byte_content = gzip.decompress(byte_content)

    if output_path is None:
        return byte_content
    return write_to_file(
        content=byte_content, filename=f"{pdb_id}_validation", extension=format, path=output_path
    )


@overload
def structure_factors(
    pdb_id: str,
    *,
    compressed: bool = True,
    output_path: None = None,
) -> bytes: ...

@overload
def structure_factors(
    pdb_id: str,
    *,
    compressed: bool = True,
    output_path: PathLike,
) -> Path: ...

def structure_factors(
    pdb_id: str,
    *,
    compressed: bool = True,
    output_path: PathLike | None = None,
) -> bytes | Path:
    """Download structure factors file (X-ray experimental data).

    Parameters
    ----------
    pdb_id
        PDB ID of the entry.
    compressed
        Whether to download the gzip-compressed version (default: True).
    output_path
        Path to a local directory for storing the downloaded file.
        If not provided, the byte contents will be returned.

    Returns
    -------
    bytes or pathlib.Path
        Either the content of the downloaded file in bytes (when `output_path` is `None`),
        or the full filepath of the stored file (when `output_path` is specified).

    References
    ----------
    * [RCSB File Download Services](https://www.rcsb.org/docs/programmatic-access/file-download-services)
    """
    pdb_id_lower = pdb_id.lower()
    comp_suffix = ".gz" if compressed else ""
    url = f"https://files.rcsb.org/download/{pdb_id_lower}-sf.cif{comp_suffix}"

    byte_content = http_request(url=url, response_type="bytes")

    if compressed:
        byte_content = gzip.decompress(byte_content)

    if output_path is None:
        return byte_content
    return write_to_file(
        content=byte_content, filename=f"{pdb_id}-sf", extension="cif", path=output_path
    )


@overload
def nmr_restraints(
    pdb_id: str,
    *,
    compressed: bool = True,
    output_path: None = None,
) -> bytes: ...

@overload
def nmr_restraints(
    pdb_id: str,
    *,
    compressed: bool = True,
    output_path: PathLike,
) -> Path: ...

def nmr_restraints(
    pdb_id: str,
    *,
    compressed: bool = True,
    output_path: PathLike | None = None,
) -> bytes | Path:
    """Download NMR restraints file (legacy format).

    Parameters
    ----------
    pdb_id
        PDB ID of the entry.
    compressed
        Whether to download the gzip-compressed version (default: True).
    output_path
        Path to a local directory for storing the downloaded file.
        If not provided, the byte contents will be returned.

    Returns
    -------
    bytes or pathlib.Path
        Either the content of the downloaded file in bytes (when `output_path` is `None`),
        or the full filepath of the stored file (when `output_path` is specified).

    References
    ----------
    * [RCSB File Download Services](https://www.rcsb.org/docs/programmatic-access/file-download-services)
    """
    pdb_id_lower = pdb_id.lower()
    comp_suffix = ".gz" if compressed else ""
    url = f"https://files.rcsb.org/download/{pdb_id_lower}.mr{comp_suffix}"

    byte_content = http_request(url=url, response_type="bytes")

    if compressed:
        byte_content = gzip.decompress(byte_content)

    if output_path is None:
        return byte_content
    return write_to_file(
        content=byte_content, filename=pdb_id_lower, extension="mr", path=output_path
    )


@overload
def nmr_restraints_v2(
    pdb_id: str,
    *,
    compressed: bool = True,
    output_path: None = None,
) -> bytes: ...

@overload
def nmr_restraints_v2(
    pdb_id: str,
    *,
    compressed: bool = True,
    output_path: PathLike,
) -> Path: ...

def nmr_restraints_v2(
    pdb_id: str,
    *,
    compressed: bool = True,
    output_path: PathLike | None = None,
) -> bytes | Path:
    """Download NMR restraints file (NMR-STAR v2 format).

    Parameters
    ----------
    pdb_id
        PDB ID of the entry.
    compressed
        Whether to download the gzip-compressed version (default: True).
    output_path
        Path to a local directory for storing the downloaded file.
        If not provided, the byte contents will be returned.

    Returns
    -------
    bytes or pathlib.Path
        Either the content of the downloaded file in bytes (when `output_path` is `None`),
        or the full filepath of the stored file (when `output_path` is specified).

    References
    ----------
    * [RCSB File Download Services](https://www.rcsb.org/docs/programmatic-access/file-download-services)
    """
    pdb_id_lower = pdb_id.lower()
    comp_suffix = ".gz" if compressed else ""
    url = f"https://files.rcsb.org/download/{pdb_id_lower}_mr.str{comp_suffix}"

    byte_content = http_request(url=url, response_type="bytes")

    if compressed:
        byte_content = gzip.decompress(byte_content)

    if output_path is None:
        return byte_content
    return write_to_file(
        content=byte_content, filename=f"{pdb_id_lower}_mr", extension="str", path=output_path
    )


@overload
def nmr_chemical_shifts(
    pdb_id: str,
    *,
    compressed: bool = True,
    output_path: None = None,
) -> bytes: ...

@overload
def nmr_chemical_shifts(
    pdb_id: str,
    *,
    compressed: bool = True,
    output_path: PathLike,
) -> Path: ...

def nmr_chemical_shifts(
    pdb_id: str,
    *,
    compressed: bool = True,
    output_path: PathLike | None = None,
) -> bytes | Path:
    """Download NMR chemical shifts file.

    Parameters
    ----------
    pdb_id
        PDB ID of the entry.
    compressed
        Whether to download the gzip-compressed version (default: True).
    output_path
        Path to a local directory for storing the downloaded file.
        If not provided, the byte contents will be returned.

    Returns
    -------
    bytes or pathlib.Path
        Either the content of the downloaded file in bytes (when `output_path` is `None`),
        or the full filepath of the stored file (when `output_path` is specified).

    References
    ----------
    * [RCSB File Download Services](https://www.rcsb.org/docs/programmatic-access/file-download-services)
    """
    pdb_id_lower = pdb_id.lower()
    comp_suffix = ".gz" if compressed else ""
    url = f"https://files.rcsb.org/download/{pdb_id_lower}_cs.str{comp_suffix}"

    byte_content = http_request(url=url, response_type="bytes")

    if compressed:
        byte_content = gzip.decompress(byte_content)

    if output_path is None:
        return byte_content
    return write_to_file(
        content=byte_content, filename=f"{pdb_id_lower}_cs", extension="str", path=output_path
    )


@overload
def nmr_data_combined(
    pdb_id: str,
    *,
    format: Literal["nef", "nmr-star"] = "nef",
    output_path: None = None,
) -> bytes: ...

@overload
def nmr_data_combined(
    pdb_id: str,
    *,
    format: Literal["nef", "nmr-star"] = "nef",
    output_path: PathLike,
) -> Path: ...

def nmr_data_combined(
    pdb_id: str,
    *,
    format: Literal["nef", "nmr-star"] = "nef",
    output_path: PathLike | None = None,
) -> bytes | Path:
    """Download combined NMR data file (NEF or NMR-STAR format).

    Parameters
    ----------
    pdb_id
        PDB ID of the entry.
    format
        Format of the combined NMR data; one of 'nef' or 'nmr-star'.
    output_path
        Path to a local directory for storing the downloaded file.
        If not provided, the byte contents will be returned.

    Returns
    -------
    bytes or pathlib.Path
        Either the content of the downloaded file in bytes (when `output_path` is `None`),
        or the full filepath of the stored file (when `output_path` is specified).

    References
    ----------
    * [RCSB File Download Services](https://www.rcsb.org/docs/programmatic-access/file-download-services)
    """
    if format not in ("nef", "nmr-star"):
        raise PDBAPIInputError(f"Format {format} not recognized. Use 'nef' or 'nmr-star'.")

    pdb_id_lower = pdb_id.lower()
    mid_chars = pdb_id[1:3].lower()

    if format == "nef":
        url = f"https://files.rcsb.org/pub/pdb/data/structures/divided/nmr_data/{mid_chars}/{pdb_id_lower}_nmr-data.nef.gz"
        ext = "nef"
    else:
        url = f"https://files.rcsb.org/pub/pdb/data/structures/divided/nmr_data/{mid_chars}/{pdb_id_lower}_nmr-data.str.gz"
        ext = "str"

    byte_content = gzip.decompress(http_request(url=url, response_type="bytes"))

    if output_path is None:
        return byte_content
    return write_to_file(
        content=byte_content, filename=f"{pdb_id}_nmr-data", extension=ext, path=output_path
    )


@overload
def electron_density_map(
    pdb_id: str,
    *,
    output_path: None = None,
) -> bytes: ...

@overload
def electron_density_map(
    pdb_id: str,
    *,
    output_path: PathLike,
) -> Path: ...

def electron_density_map(
    pdb_id: str,
    *,
    output_path: PathLike | None = None,
) -> bytes | Path:
    """Download electron density map (2Fo-Fc & Fo-Fc) in BinaryCIF format.

    Note: This downloads the potentially downsampled map for web viewing.

    Parameters
    ----------
    pdb_id
        PDB ID of the entry.
    output_path
        Path to a local directory for storing the downloaded file.
        If not provided, the byte contents will be returned.

    Returns
    -------
    bytes or pathlib.Path
        Either the content of the downloaded file in bytes (when `output_path` is `None`),
        or the full filepath of the stored file (when `output_path` is specified).

    References
    ----------
    * [RCSB File Download Services](https://www.rcsb.org/docs/programmatic-access/file-download-services)
    """
    url = f"https://maps.rcsb.org/x-ray/{pdb_id}/cell/"
    byte_content = http_request(url=url, response_type="bytes")

    if output_path is None:
        return byte_content
    return write_to_file(
        content=byte_content, filename=f"{pdb_id}_map", extension="bcif", path=output_path
    )


@overload
def fasta_entry(
    pdb_id: str,
    *,
    output_path: None = None,
) -> str: ...

@overload
def fasta_entry(
    pdb_id: str,
    *,
    output_path: PathLike,
) -> Path: ...

def fasta_entry(
    pdb_id: str,
    *,
    output_path: PathLike | None = None,
) -> str | Path:
    """Download FASTA sequences for all polymer entities in a PDB entry.

    Parameters
    ----------
    pdb_id
        PDB ID of the entry.
    output_path
        Path to a local directory for storing the downloaded file.
        If not provided, the string contents will be returned.

    Returns
    -------
    str or pathlib.Path
        Either the content of the FASTA file as a string (when `output_path` is `None`),
        or the full filepath of the stored file (when `output_path` is specified).

    Notes
    -----
    * Output is per entity (with chain identifiers provided in header).
    * This endpoint replaces the discontinued `/pdb/download/downloadFastaFiles.do` service.

    References
    ----------
    * [RCSB File Download Services](https://www.rcsb.org/docs/programmatic-access/file-download-services)
    """
    url = f"https://www.rcsb.org/fasta/entry/{pdb_id.upper()}/download"
    content = http_request(url=url, response_type="str")

    if output_path is None:
        return content
    return write_to_file(
        content=content, filename=pdb_id, extension="fasta", path=output_path
    )


@overload
def fasta_entity(
    pdb_id: str,
    entity_id: int | str,
    *,
    output_path: None = None,
) -> str: ...

@overload
def fasta_entity(
    pdb_id: str,
    entity_id: int | str,
    *,
    output_path: PathLike,
) -> Path: ...

def fasta_entity(
    pdb_id: str,
    entity_id: int | str,
    *,
    output_path: PathLike | None = None,
) -> str | Path:
    """Download FASTA sequence for a specific polymer entity.

    Parameters
    ----------
    pdb_id
        PDB ID of the entry.
    entity_id
        Entity ID within the entry.
    output_path
        Path to a local directory for storing the downloaded file.
        If not provided, the string contents will be returned.

    Returns
    -------
    str or pathlib.Path
        Either the content of the FASTA file as a string (when `output_path` is `None`),
        or the full filepath of the stored file (when `output_path` is specified).

    References
    ----------
    * [RCSB File Download Services](https://www.rcsb.org/docs/programmatic-access/file-download-services)
    """
    url = f"https://www.rcsb.org/fasta/entity/{pdb_id.upper()}_{entity_id}/download"
    content = http_request(url=url, response_type="str")

    if output_path is None:
        return content
    return write_to_file(
        content=content, filename=f"{pdb_id}_{entity_id}", extension="fasta", path=output_path
    )


@overload
def fasta_chain(
    pdb_id: str,
    asym_id: str,
    *,
    output_path: None = None,
) -> str: ...

@overload
def fasta_chain(
    pdb_id: str,
    asym_id: str,
    *,
    output_path: PathLike,
) -> Path: ...

def fasta_chain(
    pdb_id: str,
    asym_id: str,
    *,
    output_path: PathLike | None = None,
) -> str | Path:
    """Download FASTA sequence for a specific polymer entity instance (chain).

    Parameters
    ----------
    pdb_id
        PDB ID of the entry.
    asym_id
        Label asym ID (not author chain ID) of the chain.
    output_path
        Path to a local directory for storing the downloaded file.
        If not provided, the string contents will be returned.

    Returns
    -------
    str or pathlib.Path
        Either the content of the FASTA file as a string (when `output_path` is `None`),
        or the full filepath of the stored file (when `output_path` is specified).

    Notes
    -----
    * This uses label_asym_id, not author chain ID (auth_asym_id).

    References
    ----------
    * [RCSB File Download Services](https://www.rcsb.org/docs/programmatic-access/file-download-services)
    """
    url = f"https://www.rcsb.org/fasta/chain/{pdb_id.upper()}.{asym_id}/download"
    content = http_request(url=url, response_type="str")

    if output_path is None:
        return content
    return write_to_file(
        content=content, filename=f"{pdb_id}_{asym_id}", extension="fasta", path=output_path
    )


@overload
def fasta_all_entries(
    *,
    output_path: None = None,
) -> bytes: ...

@overload
def fasta_all_entries(
    *,
    output_path: PathLike,
) -> Path: ...

def fasta_all_entries(
    *,
    output_path: PathLike | None = None,
) -> bytes | Path:
    """Download FASTA sequences for all entries in the PDB archive.

    Parameters
    ----------
    output_path
        Path to a local directory for storing the downloaded file.
        If not provided, the byte contents will be returned.

    Returns
    -------
    bytes or pathlib.Path
        Either the content of the FASTA file in bytes (when `output_path` is `None`),
        or the full filepath of the stored file (when `output_path` is specified).

    References
    ----------
    * [RCSB File Download Services](https://www.rcsb.org/docs/programmatic-access/file-download-services)
    * [wwPDB Archive Downloads](https://www.wwpdb.org/ftp/pdb-ftp-sites)
    """
    url = "https://files.rcsb.org/pub/pdb/derived_data/pdb_seqres.txt.gz"
    byte_content = gzip.decompress(http_request(url=url, response_type="bytes"))

    if output_path is None:
        return byte_content
    return write_to_file(
        content=byte_content, filename="pdb_seqres", extension="txt", path=output_path
    )


@overload
def sequence_clusters(
    identity: Literal[30, 40, 50, 70, 90, 95, 100] = 90,
    *,
    output_path: None = None,
) -> str: ...

@overload
def sequence_clusters(
    identity: Literal[30, 40, 50, 70, 90, 95, 100] = 90,
    *,
    output_path: PathLike,
) -> Path: ...

def sequence_clusters(
    identity: Literal[30, 40, 50, 70, 90, 95, 100] = 90,
    *,
    output_path: PathLike | None = None,
) -> str | Path:
    """Download sequence cluster data at specified identity level.

    Results from weekly clustering of protein sequences in the PDB using DIAMOND.
    Files use polymer entity identifiers (not chain identifiers) to avoid redundancy.

    Parameters
    ----------
    identity
        Sequence identity clustering threshold; one of 30, 40, 50, 70, 90, 95, or 100.
    output_path
        Path to a local directory for storing the downloaded file.
        If not provided, the string contents will be returned.

    Returns
    -------
    str or pathlib.Path
        Either the content of the file as a string (when `output_path` is `None`),
        or the full filepath of the stored file (when `output_path` is specified).

    Notes
    -----
    * One cluster per line, sorted from largest to smallest.
    * Uses polymer entity identifiers (format: <pdb_id>_<entity_id>).

    References
    ----------
    * [RCSB File Download Services](https://www.rcsb.org/docs/programmatic-access/file-download-services)
    * [DIAMOND Aligner](https://github.com/bbuchfink/diamond)
    """
    if identity not in (30, 40, 50, 70, 90, 95, 100):
        raise PDBAPIInputError(f"Identity {identity} not valid. Use one of: 30, 40, 50, 70, 90, 95, 100.")

    url = f"https://cdn.rcsb.org/resources/sequence/clusters/clusters-by-entity-{identity}.txt"
    content = http_request(url=url, response_type="str")

    if output_path is None:
        return content
    return write_to_file(
        content=content, filename=f"clusters-by-entity-{identity}", extension="txt", path=output_path
    )
