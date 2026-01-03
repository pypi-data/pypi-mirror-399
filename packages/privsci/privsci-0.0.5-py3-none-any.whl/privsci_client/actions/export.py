import requests
from . import load_config
from .helpers.handle_serialize import serialize_merkle_proof, deserialize_merkle_proof
from ..models import Packet
from privsci_client.database import get_db_session

_current_config = load_config()
API_BASE = _current_config['base_url']
API_KEY = _current_config['api_key']
ORG_NAME = _current_config["ORG_NAME"]
DEFAULT_DB = _current_config["DEFAULT_DB"]

def export(
        *, 
        leaf_index_list, 
        old_sth, 
        org_name=ORG_NAME, 
        api_key=API_KEY
    ):
    old_size = old_sth["tree_size"]

    payload = {
        "org_name" : org_name,
        "leaf_index_list": leaf_index_list,
        "old_size": old_size
    }

    resp = requests.post(
        f"{API_BASE}/action/api/export",
        json=payload,
        headers={"X-API-Key": api_key},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()

    if DEFAULT_DB:
        proof_packet = data["proof_packet"]
        inclusion_proof_list = proof_packet['proofs']['inclusion']
        serial_consistency_proof_path = serialize_merkle_proof(proof_packet['proofs']['consistency']['path'])
        serial_consistency_proof_old_peaks = serialize_merkle_proof(proof_packet['proofs']['consistency']['old_peaks'])
        serial_consistency_proof_new_peaks = serialize_merkle_proof(proof_packet['proofs']['consistency']['new_peaks'])

        new_db_records = []
        final_tree_size = proof_packet["sth"]["tree_size"]
        final_root_hash = proof_packet["sth"]["root_hash"]
        final_signature = proof_packet["sth"]["signature"]
        for leaf_index, inclusion_proof in zip(leaf_index_list, inclusion_proof_list):
            serial_inclusion_proof = serialize_merkle_proof(inclusion_proof['proof']['path'])
            serial_peaks = serialize_merkle_proof(inclusion_proof['proof']['peaks'])
            record = Packet(
                org_name=org_name,
                serial_inclusion_peaks=serial_peaks,
                serial_inclusion_path=serial_inclusion_proof,
                serial_consistency_path=serial_consistency_proof_path,
                serial_consistency_old_peaks=serial_consistency_proof_old_peaks,
                serial_consistency_new_peaks=serial_consistency_proof_new_peaks,
                leaf_index=leaf_index,
                tree_size=final_tree_size,
                root_hash=final_root_hash,
                signature=final_signature
            )

            new_db_records.append(record)
        
        with get_db_session() as session:
            session.bulk_save_objects(new_db_records)

    return data