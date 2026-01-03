from privsci_client.actions.helpers.registry import get_handler
import requests
import hashlib
from . import load_config
from ..models import Structure, Action, Leaf, LeafType
from privsci_client.database import get_db_session

_current_config = load_config()
API_BASE = _current_config['base_url']
API_KEY = _current_config['api_key']
DEFAULT_DB = _current_config["DEFAULT_DB"]
ORG_NAME = _current_config["ORG_NAME"]
DOMAIN = _current_config["DOMAIN"]
REPRESENTATION = _current_config["REPRESENTATION"]

def sign(
        *, 
        salt_list=None,
        structure_list, 
        action_list, 
        org_name=ORG_NAME, 
        api_key=API_KEY, 
        domain=DOMAIN, 
        representation=REPRESENTATION
    ):
    handler = get_handler(domain, representation)

    if salt_list == None: 
        salt_list = [None] * len(structure_list)

    input_list = []
    hashed_structure_list = []
    hashed_action_list = []
    canonical_package = None
    canonical_package_version = None
    for salt, structure, action in zip(salt_list, structure_list, action_list):
        result = handler(structure)
        if canonical_package == None: 
            canonical_package = result["canonical_package"]
            canonical_package_version = result["canonical_package_version"]
        canonical = result["canonical"]
        if salt == None: 
            with get_db_session() as session:
                structure = session.query(Structure).filter_by(org_name=org_name, can_structure=canonical).first()
                salt = structure.salt
        combined_input = f"{salt}:{canonical}"
        hash_value = hashlib.sha256(combined_input.encode('utf-8')).hexdigest()

        combined_data = f"{hash_value}:{action}"
        action_commitment = hashlib.sha256(combined_data.encode('utf-8')).hexdigest()

        input_list.append({
            "salt": salt,
            "can_structure": canonical,
            "action": action,
            "action_hash": action_commitment
        })
        hashed_structure_list.append(hash_value)
        hashed_action_list.append(action_commitment)

    payload = {
        "org_name": org_name,
        "hashed_structure_list": hashed_structure_list,
        "domain": domain,
        "representation_type": representation,
        "canonical_package": canonical_package,
        "canonical_package_version": canonical_package_version,
        "hashed_action_list": hashed_action_list
    }

    resp = requests.post(
        f"{API_BASE}/action/api/sign",
        json=payload,
        headers={"X-API-Key": api_key},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    receipt = data['receipt']

    if DEFAULT_DB:
        new_db_records = []
        start_index = receipt["meta"]["start_index"]
        final_tree_size = receipt["sth"]["tree_size"]
        final_root_hash = receipt["sth"]["root_hash"]
        final_signature = receipt["sth"]["signature"]
        for i, item_data in enumerate(input_list):
            current_leaf_index = start_index + i

            leaf = Leaf(
                leaf_index=current_leaf_index,
                org_name = org_name,
                type = LeafType.ACTION
            )

            new_db_records.append(leaf)

            record = Action(
                org_name=org_name,
                can_structure=item_data["can_structure"],
                action=item_data["action"],
                action_hash=item_data["action_hash"],
                leaf_index=current_leaf_index,
                tree_size=final_tree_size,
                root_hash=final_root_hash,
                signature=final_signature
            )

            new_db_records.append(record)
        
        with get_db_session() as session:
            session.bulk_save_objects(new_db_records)

    return data