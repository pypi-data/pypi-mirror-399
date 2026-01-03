from privsci_client.actions.helpers.handle_serialize import deserialize_merkle_proof
from privsci_client.models import Structure, Action, Packet, Leaf, LeafType

def package_proof(session, org_name, leaf_index):
    args = []
    leaf = session.query(Leaf).filter_by(org_name=org_name, leaf_index=leaf_index).first()
    if leaf.type == LeafType.STRUCTURE: 
        data = session.query(Structure).filter_by(org_name=org_name, leaf_index=leaf_index).first()
        args.append(data.raw_structure)
    else: 
        action_data = session.query(Action).filter_by(org_name=org_name, leaf_index=leaf_index).first()
        structure_data = session.query(Structure).filter_by(org_name=org_name, can_structure=action_data.can_structure).first()
        args.append(structure_data.raw_structure)
        args.append(action_data.action)
    packet = session.query(Packet).filter_by(org_name=org_name, leaf_index=leaf_index).first()
    inclusion_proof = {
        "peaks" : deserialize_merkle_proof(packet.serial_inclusion_peaks),
        "path" : deserialize_merkle_proof(packet.serial_inclusion_path)
    }
    consistency_proof = {
        "old_peaks": deserialize_merkle_proof(packet.serial_consistency_old_peaks),
        "new_peaks": deserialize_merkle_proof(packet.serial_consistency_new_peaks),
        "path": deserialize_merkle_proof(packet.serial_consistency_path)
    }

    new_sth = {
        "tree_size": packet.tree_size,
        "root_hash": packet.root_hash,
        "signature": packet.signature
    }
    return inclusion_proof, consistency_proof, args, new_sth