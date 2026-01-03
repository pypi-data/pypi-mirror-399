from privsci_client.actions.helpers.registry import get_handler
import requests
from . import load_config
from ..models import Structure, Leaf, LeafType
from privsci_client.database import get_db_session

_current_config = load_config()
API_BASE = _current_config['base_url']
API_KEY = _current_config['api_key']
DEFAULT_DB = _current_config["DEFAULT_DB"]
ORG_NAME = _current_config["ORG_NAME"]
DOMAIN = _current_config["DOMAIN"]
REPRESENTATION = _current_config["REPRESENTATION"]

def create(
        *,
        structure_list, 
        org_name=ORG_NAME, 
        api_key=API_KEY, 
        domain=DOMAIN,
        representation=REPRESENTATION
    ):
    handler = get_handler(domain, representation)

    input_list = []
    canonical_package = None
    canonical_package_version = None
    for structure in structure_list:
        result = handler(structure)
        if canonical_package == None: 
            canonical_package = result["canonical_package"]
            canonical_package_version = result["canonical_package_version"]
        input_list.append({
            "salt": result["salt"],
            "raw_structure": structure,
            "can_structure": result["canonical"],
            "hash_value": result["hash_value"]
        })

    payload = {
        "org_name" : org_name,
        "hash_value_list": [i["hash_value"] for i in input_list],
        "domain": domain,
        "representation_type": representation,
        "canonical_package": canonical_package,
        "canonical_package_version": canonical_package_version
    }

    resp = requests.post(
        f"{API_BASE}/action/api/create",
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
                type = LeafType.STRUCTURE
            )

            new_db_records.append(leaf)

            record = Structure(
                org_name=org_name,
                salt=item_data["salt"],
                raw_structure=item_data["raw_structure"],
                can_structure=item_data["can_structure"],
                structure_hash=item_data["hash_value"],
                leaf_index=current_leaf_index,
                tree_size=final_tree_size,
                root_hash=final_root_hash,
                signature=final_signature
            )

            new_db_records.append(record)
        
        with get_db_session() as session:
            session.bulk_save_objects(new_db_records)

    return {
        "input_list": input_list,
        "receipt": data["receipt"]
    }