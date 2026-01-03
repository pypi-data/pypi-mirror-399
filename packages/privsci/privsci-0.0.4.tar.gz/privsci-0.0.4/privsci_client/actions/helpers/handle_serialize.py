import json

def serialize_merkle_proof(proof):
    """
    Serializes a Merkle proof (list of byte hashes) into a JSON string.
    Converts binary hash data to hex strings for safe transport.
    
    Args:
        proof: A list of dicts, e.g., [{'hash': b'\xaf...', 'direction': 'left'}, ...]
        
    Returns:
        A JSON formatted string representation of the proof.
    """
    serializable_list = []
    
    for item in proof:
        # Create a copy to avoid mutating the original data
        s_item = item.copy()
        
        # specific handling for bytes: convert to hex string
        if isinstance(s_item.get('hash'), bytes):
            s_item['hash'] = s_item['hash'].hex()
            
        serializable_list.append(s_item)
        
    return json.dumps(serializable_list).encode('utf-8')

def deserialize_merkle_proof(json_data):
    """
    Deserializes a JSON string back into a Merkle proof object with raw bytes.
    Converts hex strings back to valid python bytes.
    
    Args:
        json_data: A JSON string containing the serialized proof.
        
    Returns:
        A list of dicts with 'hash' fields restored to bytes.
    """
    loaded_list = json.loads(json_data)
    deserialized_proof = []
    
    for item in loaded_list:
        d_item = item.copy()
        deserialized_proof.append(d_item)
        
    return deserialized_proof