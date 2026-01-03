from privsci_client.actions.helpers.registry import get_handler
from ..models import Structure
from .helpers.verifier import Verifier
import hashlib
from . import load_config
from privsci_client.database import get_db_session

_current_config = load_config()
API_BASE = _current_config['base_url']
API_KEY = _current_config['api_key']
DEFAULT_DB = _current_config["DEFAULT_DB"]
ORG_NAME = _current_config["ORG_NAME"]
DOMAIN = _current_config["DOMAIN"]
REPRESENTATION = _current_config["REPRESENTATION"]

def verify_inclusion(
        *, 
        salt=None,
        structure, 
        action=None,
        proof,
        root,
        org_name=ORG_NAME,
        domain=DOMAIN, 
        representation=REPRESENTATION
    ):
    handler = get_handler(domain, representation)
    result = handler(structure)
    canonical = result["canonical"]
    if salt == None: 
        with get_db_session() as session:
            db_structure = session.query(Structure).filter_by(org_name=org_name, can_structure=canonical).first()
            salt = db_structure.salt
    combined_input = f"{salt}:{canonical}"
    hash_value = hashlib.sha256(combined_input.encode('utf-8')).hexdigest()

    if action != None:
        combined_data = f"{hash_value}:{action}"
        action_commitment = hashlib.sha256(combined_data.encode('utf-8')).hexdigest()
    else: 
        action_commitment = hash_value
    
    verifier = Verifier()
    is_included = verifier.verify_inclusion(action_commitment, proof, root)

    return is_included

def verify_consistency(
        old_sth, 
        new_sth, 
        proof
    ):
    verifier = Verifier()
    is_consistent = verifier.verify_consistency(old_sth, new_sth, proof)
    
    return is_consistent