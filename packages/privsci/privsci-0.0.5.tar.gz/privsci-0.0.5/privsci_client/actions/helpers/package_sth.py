from privsci_client.models import Structure, Action, Leaf, LeafType

def package_sth(session, org_name, leaf_index_list):
    leaf_index_list = sorted(leaf_index_list)
    for i, leaf_index in enumerate(leaf_index_list):
        leaf = session.query(Leaf).filter_by(org_name=org_name, leaf_index=leaf_index).first()
        if leaf == None: 
            raise ValueError(f"No leaf found in {org_name}")
        if leaf.type == LeafType.STRUCTURE: 
            structure = session.query(Structure).filter_by(org_name=org_name, leaf_index=leaf_index).first()
            if i == 0: 
                old_sth = {
                    "tree_size": structure.tree_size, 
                    "root_hash": structure.root_hash,
                    "signature": structure.signature
                }
        else: 
            action = session.query(Action).filter_by(org_name=org_name, leaf_index=leaf_index).first()
            if i == 0: 
                old_sth = {
                    "tree_size": action.tree_size, 
                    "root_hash": action.root_hash,
                    "signature": action.signature
                }
    return old_sth