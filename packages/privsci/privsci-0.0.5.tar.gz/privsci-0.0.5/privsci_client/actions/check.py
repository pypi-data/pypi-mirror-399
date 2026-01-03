from privsci_client.actions.helpers.registry import get_handler
import requests
import hashlib
from . import load_config
from ..models import Structure
from privsci_client.database import get_db_session

_current_config = load_config()
API_BASE = _current_config['base_url']
API_KEY = _current_config['api_key']
DEFAULT_DB = _current_config["DEFAULT_DB"]
ORG_NAME = _current_config["ORG_NAME"]
DOMAIN = _current_config["DOMAIN"]
REPRESENTATION = _current_config["REPRESENTATION"]

def check(
        *, 
        salt_list=None, 
        structure_list, 
        action_list=None,
        org_name=ORG_NAME, 
        api_key=API_KEY, 
        domain=DOMAIN, 
        representation=REPRESENTATION
    ):
    handler = get_handler(domain, representation)

    if action_list == None: 
        action_list = [None] * len(structure_list)

    if salt_list == None: 
        salt_list = [None] * len(structure_list)

    hash_value_list = []    
    for salt, structure, action in zip(salt_list, structure_list, action_list):
        result = handler(structure)

        canonical = result["canonical"]
        if salt == None: 
            with get_db_session() as session:
                structure = session.query(Structure).filter_by(org_name=org_name, can_structure=canonical).first()
                salt = structure.salt
        combined_input = f"{salt}:{canonical}"
        hash_value = hashlib.sha256(combined_input.encode('utf-8')).hexdigest() 

        if action != None:
            combined_data = f"{hash_value}:{action}"
            action_commitment = hashlib.sha256(combined_data.encode('utf-8')).hexdigest()

        hash_value_list.append(hash_value if action is None else action_commitment)

    payload = {
        "org_name": org_name,
        "hash_value_list": hash_value_list,
        "domain": domain,
        "representation_type": representation,
        "canonical_package": result["canonical_package"],
        "canonical_package_version": result["canonical_package_version"]
    }

    resp = requests.post(
        f"{API_BASE}/action/api/check",
        json=payload,
        headers={"X-API-Key": api_key},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()

    return data