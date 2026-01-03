from rdkit import Chem
import hashlib
import secrets
from importlib.metadata import version
from privsci_client.actions.helpers.registry import register_handler

@register_handler("molecule", "smiles")
def molecule_smiles_handler(structure) -> dict:
    pkg_name = "rdkit"
    pkg_version = version(pkg_name)

    if isinstance(structure, str):
        mol = Chem.MolFromSmiles(structure)
        if mol is None:
            raise ValueError("Invalid SMILES string")
    else:
        mol = structure

    canonical = Chem.MolToSmiles(
        mol,
        isomericSmiles=True,
        kekuleSmiles=False,
    )

    salt = secrets.token_hex(16)
    combined_input = f"{salt}:{canonical}"
    hash_value = hashlib.sha256(combined_input.encode('utf-8')).hexdigest()

    return {
        "salt": salt,
        "canonical": canonical,
        "hash_value": hash_value,
        "canonical_package": pkg_name,
        "canonical_package_version": pkg_version,
    }