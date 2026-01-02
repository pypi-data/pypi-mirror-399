"""Query the RESTful Data API of the RCSB PDB.

References
----------
- [RCSB RESTful API Documentation](https://data.rcsb.org/redoc/)
"""

from collections.abc import Iterable
from typing import Literal

from .util import http_request


# General API endpoints
_ROOT_DATA: str = "https://data.rcsb.org/rest/v1"
_ROOT_FILE: str = "https://files.rcsb.org"
_ROOT_SEARCH: str = "https://search.rcsb.org/rcsbsearch/v2/query"
_END_DATA: str = f"{_ROOT_DATA}/core"
_END_SCHEMA: str = f"{_ROOT_DATA}/schema"
_END_HOLDINGS = f"{_ROOT_DATA}/holdings"


def schema(
    schema_type: Literal[
        "entry",
        "polymer_entity",
        "branched_entity",
        "nonpolymer_entity",
        "polymer_entity_instance",
        "branched_entity_instance",
        "nonpolymer_entity_instance",
        "assembly",
        "chem_comp",
        "drugbank",
        "pubmed",
        "uniprot",
    ],
) -> dict:
    """Get the data schema for a data type.

    Parameters
    ----------
    schema_type
        Data schema to fetch; one of entry, polymer_entity, branched_entity,
        nonpolymer_entity, polymer_entity_instance, branched_entity_instance,
        nonpolymer_entity_instance, assembly, chem_comp, drugbank, pubmed, uniprot.

    Returns
    -------
    dict
        JSON Schema definition for the requested type.

    Sample Response
    ---------------
    "string"

    References
    ----------
    * https://data.rcsb.org/index.html#data-schema
    """
    return http_request(url=f"{_END_SCHEMA}/{schema_type}")


def entry(pdb_id: str) -> dict:
    """Description of a PDB entry at the top level of PDB structural hierarchical data organization.

    Parameters
    ----------
    pdb_id
        PDB ID of the entry.

    Returns
    -------
    dict
        Entry metadata including cell, symmetry, experimental, entity, assembly, citation and accession details.

    Sample Response
    ---------------
    {
      "entry": {"id": "4HHB"},
      "rcsb_entry_container_identifiers": {"entry_id": "4HHB", "assembly_ids": ["1"], "polymer_entity_ids": ["1","2"]},
      "rcsb_entry_info": {"molecular_weight": 64458.2, "assembly_count": 1}
    }

    References
    ----------
    * https://data.rcsb.org/redoc/#operation/getEntryById
    """
    return http_request(url=f"{_END_DATA}/entry/{pdb_id}")


def entry_pubmed(pdb_id: str) -> dict:
    """Description of a PDB entry's primary citation, annotated by PubMed.

    Parameters
    ----------
    pdb_id
        PDB ID of the entry.

    Returns
    -------
    dict
        PubMed metadata for the primary citation.

    Sample Response
    ---------------
    {
      "rcsb_pubmed_container_identifiers": {"pubmed_id": 12345678},
      "rcsb_pubmed_doi": "10.1016/j.jmb.2020.01.001",
      "rcsb_pubmed_mesh_descriptors": ["Proteins", "X-Ray Crystallography"]
    }

    References
    ----------
    * https://data.rcsb.org/redoc/#operation/getPubmedByEntryId
    """
    return http_request(url=f"{_END_DATA}/pubmed/{pdb_id}")


def assembly(pdb_id: str, assembly_id: int | str) -> dict:
    """Description of a structural assembly (quaternary structure) in a PDB entry.

    Parameters
    ----------
    pdb_id
        PDB ID of the entry.
    assembly_id
        Assembly ID of the biological assembly candidate in the PDB entry.

    Returns
    -------
    dict
        Assembly level details including symmetry, stoichiometry, interface identifiers and counts.

    Sample Response
    ---------------
    {
      "rcsb_assembly_container_identifiers": {"entry_id": "1KIP", "assembly_id": "1", "interface_ids": ["1"]},
      "rcsb_assembly_info": {"polymer_entity_instance_count": 2, "polymer_composition": "heteromeric protein"}
    }

    References
    ----------
    * https://data.rcsb.org/redoc/#operation/getAssemblyById
    """
    return http_request(url=f"{_END_DATA}/assembly/{pdb_id}/{assembly_id}")


def entity_branched(pdb_id: str, entity_id: int | str) -> dict:
    """Description of a branched entity (molecule) in a PDB entry.

    Parameters
    ----------
    pdb_id
        PDB ID of the entry.
    entity_id
        Entity ID of the branched entity in the PDB entry.

    Returns
    -------
    dict
        Branched entity data including sequence, taxonomy, annotations and identifiers.

    Sample Response
    ---------------
    {
      "rcsb_polymer_entity_container_identifiers": {"entry_id": "4CYG", "entity_id": "2"},
      "rcsb_polymer_entity": {"pdbx_description": "glycan", "formula_weight": 1200.5}
    }

    References
    ----------
    * https://data.rcsb.org/redoc/#operation/getBranchedEntityById
    """
    return http_request(url=f"{_END_DATA}/branched_entity/{pdb_id}/{entity_id}")


def entity_nonpolymer(pdb_id: str, entity_id: int | str) -> dict:
    """Description of a non-polymer entity (molecule) in a PDB entry.

    Parameters
    ----------
    pdb_id
        PDB ID of the entry.
    entity_id
        Entity ID of the non-polymer entity in the PDB entry.

    Returns
    -------
    dict
        Non-polymer entity description with identifiers, annotations and features.

    Sample Response
    ---------------
    {
      "pdbx_entity_nonpoly": {"comp_id": "GTP", "name": "Guanosine-5'-triphosphate"},
      "rcsb_nonpolymer_entity_container_identifiers": {"entry_id": "4G22", "entity_id": "2", "nonpolymer_comp_id": "GTP"}
    }

    References
    ----------
    * https://data.rcsb.org/redoc/#operation/getNonPolymerEntityById
    """
    return http_request(url=f"{_END_DATA}/nonpolymer_entity/{pdb_id}/{entity_id}")


def entity_polymer(pdb_id: str, entity_id: int | str) -> dict:
    """Description of a polymer entity (molecule) in a PDB entry.

    Parameters
    ----------
    pdb_id
        PDB ID of the entry.
    entity_id
        Entity ID of the polymer entity in the PDB entry.

    Returns
    -------
    dict
        Polymer entity sequence, taxonomy, annotations and identifiers.

    Sample Response
    ---------------
    {
      "entity_poly": {"pdbx_seq_one_letter_code": "MSHHWGYGK..."},
      "rcsb_polymer_entity_container_identifiers": {"entry_id": "4G22", "entity_id": "1", "uniprot_ids": ["P69905"]}
    }

    References
    ----------
    * https://data.rcsb.org/redoc/#operation/getPolymerEntityById
    """
    return http_request(url=f"{_END_DATA}/polymer_entity/{pdb_id}/{entity_id}")


def entity_polymer_uniprot(pdb_id: str, entity_id: int | str) -> dict:
    """UniProt annotations for a macromolecular polymer entity (molecule) in a PDB entry.

    Parameters
    ----------
    pdb_id
        PDB ID of the entry.
    entity_id
        Entity ID of the polymer entity in the PDB entry.

    Returns
    -------
    dict
        UniProt mappings, features and alignments for the entity.

    Sample Response
    ---------------
    [
      {
        "rcsb_uniprot_container_identifiers": {"entry_id": "4G22", "entity_id": "1"},
        "rcsb_uniprot_accession": ["P69905"],
        "rcsb_uniprot_keyword": ["Hemoglobin"],
        "rcsb_uniprot_feature": [ {"type": "CHAIN", "begin": 1, "end": 141} ]
      }
    ]

    References
    ----------
    * https://data.rcsb.org/redoc/#operation/getUniprotByEntityId
    """
    return http_request(url=f"{_END_DATA}/uniprot/{pdb_id}/{entity_id}")


def instance_branched(pdb_id: str, asym_id: int | str) -> dict:
    """Description of an instance (chain) of a branched entity in a PDB entry.

    Parameters
    ----------
    pdb_id
        PDB ID of the entry.
    asym_id
        Instance (chain) ID of the branched entity instance in the PDB entry.

    Returns
    -------
    dict
        Branched chain level information including identifiers, mapping and features.

    Sample Response
    ---------------
    {
      "rcsb_polymer_entity_instance_container_identifiers": {"entry_id": "1US2", "asym_id": "C"},
      "rcsb_polymer_instance_feature_summary": [{"type": "PFAM_DOMAIN", "count": 1}]
    }

    References
    ----------
    * https://data.rcsb.org/redoc/#operation/getBranchedEntityInstanceById
    """
    return http_request(url=f"{_END_DATA}/branched_entity_instance/{pdb_id}/{asym_id}")


def instance_nonpolymer(pdb_id: str, asym_id: int | str) -> dict:
    """Description of an instance (chain) of a non-polymer entity in a PDB entry.

    Parameters
    ----------
    pdb_id
        PDB ID of the entry.
    asym_id
        Instance (chain) ID of the non-polymer entity instance in the PDB entry.

    Returns
    -------
    dict
        Non-polymer instance mapping, identifiers, annotations and validation summaries.

    Sample Response
    ---------------
    {
      "rcsb_nonpolymer_entity_instance_container_identifiers": {"entry_id": "2FBW", "asym_id": "J", "comp_id": "STI"},
      "rcsb_nonpolymer_instance_feature_summary": [{"type": "LIGAND_NEIGHBOR", "count": 5}]
    }

    References
    ----------
    * https://data.rcsb.org/redoc/#operation/getNonPolymerEntityInstanceById
    """
    return http_request(url=f"{_END_DATA}/nonpolymer_entity_instance/{pdb_id}/{asym_id}")


def instance_polymer(pdb_id: str, asym_id: int | str) -> dict:
    """Description of an instance (chain) of a polymer entity in a PDB entry.

    Parameters
    ----------
    pdb_id
        PDB ID of the entry.
    asym_id
        Instance (chain) ID of the polymer entity instance in the PDB entry.

    Returns
    -------
    dict
        Chain-level polymer information including mapping, features and neighbors.

    Sample Response
    ---------------
    {
      "rcsb_polymer_entity_instance_container_identifiers": {"entry_id": "2FBW", "asym_id": "E", "auth_asym_id": "A"},
      "rcsb_polymer_instance_feature_summary": [{"type": "SECONDARY_STRUCTURE", "count": 3}]
    }

    References
    ----------
    * https://data.rcsb.org/redoc/#operation/getPolymerEntityInstanceById
    """
    return http_request(url=f"{_END_DATA}/polymer_entity_instance/{pdb_id}/{asym_id}")


def chemical_component(ccd_id: str) -> dict:
    """Description of a chemical component (i.e. ligand, small molecule, monomer) in a PDB entry.

    Parameters
    ----------
    ccd_id
        CHEM COMP ID of the chemical component. For protein polymer entities, this is the
        three-letter code for the amino acid. For nucleic acid polymer entities, this is the
        one-letter code for the base.

    Returns
    -------
    dict
        Chemical component record including identifiers, descriptors and annotations.

    Sample Response
    ---------------
    {
      "chem_comp": {"id": "ATP", "name": "ADENOSINE-5'-TRIPHOSPHATE", "formula": "C10 H16 N5 O13 P3"},
      "rcsb_chem_comp_descriptor": {"InChIKey": "ZKHQWZAMYRWXGA-KQYNXXCUSA-N"}
    }

    References
    ----------
    * https://data.rcsb.org/redoc/#operation/getChemCompById
    """
    return http_request(url=f"{_END_DATA}/chemcomp/{ccd_id}")


def chemical_drugbank(ccd_id: str) -> dict:
    """Description of a chemical component (i.e. ligand, small molecule, monomer) in a PDB entry, annotated by DrugBank.

    Parameters
    ----------
    ccd_id
        CHEM COMP ID of the chemical component. For protein polymer entities, this is the
        three-letter code for the amino acid. For nucleic acid polymer entities, this is the
        one-letter code for the base.

    Returns
    -------
    dict
        DrugBank-integrated annotations for the chemical component.

    Sample Response
    ---------------
    {
      "drugbank_container_identifiers": {"drugbank_id": "DB00781"},
      "drugbank_info": {"name": "Adenosine triphosphate", "drug_groups": "approved", "mechanism_of_action": "ATP stores and transfers chemical energy"}
    }

    References
    ----------
    * https://data.rcsb.org/redoc/#operation/getDrugBankByChemCompId
    """
    return http_request(url=f"{_END_DATA}/drugbank/{ccd_id}")


def group_entry(group_id: str) -> dict:
    """PDB cluster data for entries, based upon a given aggregation method.

    Parameters
    ----------
    group_id
        Group ID, e.g. 'G_1002011'.

    Returns
    -------
    dict
        Entry group object with identifiers, info and related groups.

    Sample Response
    ---------------
    {
      "rcsb_group_container_identifiers": {"group_id": "G_1002011", "group_provenance_id": "provenance_sequence_identity"},
      "rcsb_group_info": {"group_name": "Group 1002011", "group_members_count": 5}
    }

    References
    ----------
    * https://data.rcsb.org/redoc/#operation/getEntryGroupById
    """
    return http_request(url=f"{_END_DATA}/entry_groups/{group_id}")


def group_provenance(provenance_id: str) -> dict:
    """Aggregation method used to create groups.

    Parameters
    ----------
    provenance_id
        Group provenance ID, e.g. provenance_sequence_identity.

    Returns
    -------
    dict
        Aggregation method description.

    Sample Response
    ---------------
    {
      "rcsb_group_provenance_container_identifiers": {"group_provenance_id": "provenance_sequence_identity"},
      "rcsb_group_aggregation_method": {"type": "sequence_identity", "method": {"identity": 0.9}}
    }

    References
    ----------
    * https://data.rcsb.org/redoc/#operation/getGroupProvenanceById
    """
    return http_request(url=f"{_END_DATA}/group_provenance/{provenance_id}")


def group_entity(group_id: str) -> dict:
    """PDB cluster data for polymer entities, based upon a given aggregation method.

    Parameters
    ----------
    group_id
        Group ID, e.g. Q3Y9I6.

    Returns
    -------
    dict
        Polymer entity group object with identifiers, statistics and alignments.

    Sample Response
    ---------------
    {
      "rcsb_group_container_identifiers": {"group_id": "Q3Y9I6", "group_provenance_id": "provenance_sequence_identity"},
      "rcsb_group_info": {"group_members_count": 10, "group_members_granularity": "entity"}
    }

    References
    ----------
    * https://data.rcsb.org/redoc/#operation/getPolymerEntityGroupById
    """
    return http_request(url=f"{_END_DATA}/polymer_entity_groups/{group_id}")


def group_nonpolymer(group_id: str) -> dict:
    """PDB cluster data for non-polymer entities for a given aggregation method.

    Parameters
    ----------
    group_id
        Group ID, e.g. HEM.

    Returns
    -------
    dict
        Non-polymer entity group object with identifiers and statistics.

    Sample Response
    ---------------
    {
      "rcsb_group_container_identifiers": {"group_id": "HEM", "group_provenance_id": "provenance_sequence_identity"},
      "rcsb_group_info": {"group_members_count": 25, "group_members_granularity": "entity"}
    }

    References
    ----------
    * https://data.rcsb.org/redoc/#operation/getNonPolymerEntityGroupById
    """
    return http_request(url=f"{_END_DATA}/nonpolymer_entity_groups/{group_id}")


def interface(
    pdb_id: str,
    assembly_id: int | str = 1,
    interface_id: int | str = 1,
) -> dict:
    """Description of a pairwise polymeric interface in an assembly of a PDB entry.

    Parameters
    ----------
    pdb_id
        PDB ID of the entry.
    assembly_id
        Assembly ID of the biological assembly candidate in the PDB entry.
    interface_id
        Interface ID of the pairwise polymeric interface.

    Returns
    -------
    dict
        Pairwise interface description including partners, operators and interface area.

    Sample Response
    ---------------
    {
      "rcsb_interface_container_identifiers": {"entry_id": "1RH7", "assembly_id": "1", "interface_id": "1"},
      "rcsb_interface_info": {"interface_area": 850.2, "interface_character": "hetero"}
    }

    References
    ----------
    * https://data.rcsb.org/redoc/#operation/getInterfaceById
    """
    return http_request(url=f"{_END_DATA}/interface/{pdb_id}/{assembly_id}/{interface_id}")


def holdings(status: Literal["current", "unreleased", "removed"] = "current") -> list[str]:
    """Get all PDB ID holdings data for a specific entry status.

    Parameters
    ----------
    status
        Status of PDB entries to retrieve; one of:
        - `"current"`: all current PDB IDs
        - `"unreleased"`: all unreleased PDB IDs
        - `"removed"`: all removed PDB IDs

    Returns
    -------
    pdb_ids
        List of PDB IDs.

    Sample Response
    ---------------
    ["1ABC", "4HHB"]

    References
    ----------
    * https://data.rcsb.org/redoc/#operation/getCurrentEntryIds
    * https://data.rcsb.org/redoc/#operation/getUnreleasedEntryIds
    * https://data.rcsb.org/redoc/#operation/getRemovedEntryIds
    """
    if status not in ("current", "unreleased", "removed"):
        raise ValueError(f"{status} is not a valid argument for `data`.")
    return list(http_request(url=f"{_END_HOLDINGS}/{status}/entry_ids"))


def holdings_current_ccd_ids() -> list[str]:
    """List all current chemical component dictionary (CCD) IDs.

    Returns
    -------
    ccd_ids
        List of current CCD identifiers.

    Sample Response
    ---------------
    ["ATP", "STI"]

    References
    ----------
    * https://data.rcsb.org/redoc/#operation/getCurrentCcdIds
    """
    return list(http_request(url=f"{_END_HOLDINGS}/current/ccd_ids"))


def holdings_current_prd_ids() -> list[str]:
    """List all current PRD IDs for BIRD entries.

    Returns
    -------
    prd_ids
        List of current PRD identifiers.

    Sample Response
    ---------------
    ["PRD_000010", "PRD_000001"]

    References
    ----------
    * https://data.rcsb.org/redoc/#operation/getCurrentPrdIds
    """
    return list(http_request(url=f"{_END_HOLDINGS}/current/prd_ids"))


def holdings_removed_entry_ids() -> list[str]:
    """List all removed PDB entry IDs.

    Returns
    -------
    pdb_ids
        List of removed PDB IDs.

    Sample Response
    ---------------
    ["1HHB", "2XYZ"]

    References
    ----------
    * https://data.rcsb.org/redoc/#operation/getRemovedEntryIds
    """
    return list(http_request(url=f"{_END_HOLDINGS}/removed/entry_ids"))


def holdings_unreleased_entry_ids() -> list[str]:
    """List all unreleased PDB entry IDs currently on hold or in processing.

    Returns
    -------
    pdb_ids
        List of unreleased PDB IDs.

    Sample Response
    ---------------
    ["9ZZZ", "9YYY"]

    References
    ----------
    * https://data.rcsb.org/redoc/#operation/getUnreleasedEntryIds
    """
    return list(http_request(url=f"{_END_HOLDINGS}/unreleased/entry_ids"))


def holdings_without_pdb_file() -> list[str]:
    """Get PDB IDs of all entries without a corresponding legacy PDB-format file.

    Returns
    -------
    pdb_ids
        List of PDB IDs.

    Sample Response
    ---------------
    ["6XY7", "7ABC"]

    Notes
    -----
    * Following entries don't have a corresponding PDB-format file:
      * Entries with multiple-character chain IDs.
      * Entries with more than 62 chains.
      * Entries with 100,000 or more atoms.
      * Entries with a complex beta sheet topology.
    * Number of these entries will continue to grow as new large structures are deposited and released.
    * These entries can also be found using Advanced Search (Deposition > Compatible with PDB Format > equals > N)

    References
    ----------
    * `RCSB Documentation: Structures Without Legacy PDB Format Files <https://www.rcsb.org/docs/general-help/structures-without-legacy-pdb-format-files>`_
    """
    pdb_ids = http_request(
        url="https://files.wwpdb.org/pub/pdb/compatible/pdb_bundle/pdb_bundle_index.txt",
        response_type="str",
    )
    return pdb_ids.upper().splitlines()


def holdings_status(pdb_id: str) -> dict:
    """Status and status code of a PDB entry.

    Parameters
    ----------
    pdb_id
        PDB ID of the entry.

    Returns
    -------
    dict
        Status record for the entry.

    Sample Response
    ---------------
    {
      "rcsb_repository_holdings_combined": {"status": "CURRENT", "status_code": "REL"},
      "rcsb_repository_holdings_combined_entry_container_identifiers": {"entry_id": "1KIP"}
    }

    References
    ----------
    * https://data.rcsb.org/redoc/#operation/getEntryStatus
    """
    return http_request(url=f"{_END_HOLDINGS}/status/{pdb_id}")


def holdings_status_many(pdb_ids: Iterable[str]) -> list[dict]:
    """Get status and status code for multiple entries in one request.

    Parameters
    ----------
    pdb_ids
        Iterable of PDB entry IDs.

    Returns
    -------
    list of dict
        One status record per supplied PDB ID.

    Sample Response
    ---------------
    [
      {"rcsb_repository_holdings_combined_entry_container_identifiers": {"entry_id": "1KIP"}},
      {"rcsb_repository_holdings_combined_entry_container_identifiers": {"entry_id": "4HHB"}}
    ]

    References
    ----------
    * https://data.rcsb.org/redoc/#operation/getEntryStatuses
    """
    ids_csv = ",".join(pdb_ids)
    return list(http_request(url=f"{_END_HOLDINGS}/status?ids={ids_csv}"))


def holdings_removed(pdb_id: str) -> dict:
    """Description of an entry that was removed from the PDB repository.

    Parameters
    ----------
    pdb_id
        PDB ID of the entry.

    Returns
    -------
    dict
        Description of the removed entry.

    Sample Response
    ---------------
    {
      "rcsb_repository_holdings_removed": {"title": "Obsoleted structure", "status_code": "OBS"},
      "rcsb_repository_holdings_removed_entry_container_identifiers": {"entry_id": "1HHB"}
    }

    References
    ----------
    * https://data.rcsb.org/redoc/#operation/getRemovedEntryById
    """
    return http_request(url=f"{_END_HOLDINGS}/removed/{pdb_id}")


def holdings_unreleased(pdb_id: str) -> dict:
    """Description of an entry that is being processed or on hold waiting for release.

    Parameters
    ----------
    pdb_id
        PDB ID of the entry.

    Returns
    -------
    dict
        Description of the unreleased entry.

    Sample Response
    ---------------
    {
      "rcsb_repository_holdings_unreleased": {"status_code": "HPUB", "title": "Pending release"},
      "rcsb_repository_holdings_unreleased_entry_container_identifiers": {"entry_id": "9ZZZ"}
    }

    References
    ----------
    * https://data.rcsb.org/redoc/#operation/getUnreleasedEntryById
    """
    return http_request(url=f"{_END_HOLDINGS}/unreleased/{pdb_id}")


def holdings_unreleased_many(pdb_ids: Iterable[str]) -> list[dict]:
    """Describe unreleased entries in bulk.

    Parameters
    ----------
    pdb_ids
        Iterable of unreleased PDB IDs.

    Returns
    -------
    list of dict
        One unreleased-entry description per supplied ID.

    Sample Response
    ---------------
    [
      {"rcsb_repository_holdings_unreleased_entry_container_identifiers": {"entry_id": "9ZZZ"}},
      {"rcsb_repository_holdings_unreleased_entry_container_identifiers": {"entry_id": "9YYY"}}
    ]

    References
    ----------
    * https://data.rcsb.org/redoc/#operation/getUnreleasedEntries
    """
    ids_csv = ",".join(pdb_ids)
    return list(http_request(url=f"{_END_HOLDINGS}/unreleased?ids={ids_csv}"))
