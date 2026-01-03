import hashlib

def _hash_leaf(data: bytes) -> bytes:
    return hashlib.sha256(b"\x00" + data).digest()

def _hash_node(left: bytes, right: bytes) -> bytes:
    return hashlib.sha256(b"\x01" + left + right).digest()

class Verifier: 
    @staticmethod
    def verify_inclusion(leaf_hash_hex, proof, expected_root):
        raw_leaf_bytes = bytes.fromhex(leaf_hash_hex)
        target_hash = _hash_leaf(raw_leaf_bytes)
        expected_root_bytes = bytes.fromhex(expected_root) if isinstance(expected_root, str) else expected_root
        
        current_hash = target_hash
        local_height = 0
        
        for sibling in proof['path']:
            sibling_hash = bytes.fromhex(sibling['hash'])
            direction = sibling['direction']

            if direction == 'L':
                current_hash = _hash_node(sibling_hash, current_hash)
            elif direction == 'R':
                current_hash = _hash_node(current_hash, sibling_hash)
            else:
                raise ValueError(f"Invalid direction: {direction}")
            local_height += 1
            
        local_peak = current_hash
        all_peaks = proof['peaks'] + [{'hash': local_peak.hex(), 'level': local_height}]
        all_peaks.sort(key=lambda x: x['level'], reverse=True)
        
        computed_root = bytes.fromhex(all_peaks[0]['hash'])
        for i in range(1, len(all_peaks)):
            next_peak = bytes.fromhex(all_peaks[i]['hash'])
            computed_root = _hash_node(computed_root, next_peak)
            
        return computed_root == expected_root_bytes

    @staticmethod
    def verify_consistency(old_sth, new_sth, proof):
        old_root_hex = old_sth['root_hash']
        new_root_hex = new_sth['root_hash']
        old_size = old_sth['tree_size']
        
        old_peaks = [bytes.fromhex(p['hash']) for p in proof['old_peaks']]
        path = proof['path']
        bagging_order = old_peaks[::-1]
        
        if not bagging_order:
            calculated_old_root = hashlib.sha256(b'').digest()
        else:
            calculated_old_root = bagging_order[0]
            for p in bagging_order[1:]:
                calculated_old_root = _hash_node(calculated_old_root, p)
        
        if calculated_old_root.hex() != old_root_hex:
            print(f"Mismatch! Calculated: {calculated_old_root.hex()} vs Expected: {old_root_hex}")
            return False

        if old_size == 0:
            current_hash = None
            current_level = 0
        else:
            current_level = (old_size & -old_size).bit_length() - 1
            current_hash = old_peaks[0]

        for sibling_info in path:
            sibling_hash = bytes.fromhex(sibling_info['hash'])
            direction = sibling_info['direction']
            
            if direction == 'L':
                current_hash = _hash_node(sibling_hash, current_hash)
            else:
                current_hash = _hash_node(current_hash, sibling_hash)
            
            current_level += 1
        
        all_peaks = []
        for p in proof['new_peaks']:
            all_peaks.append({
                'hash': bytes.fromhex(p['hash']),
                'level': p['level']
            })
            
        if current_hash is not None:
            all_peaks.append({
                'hash': current_hash,
                'level': current_level
            })
            
        all_peaks.sort(key=lambda x: x['level'], reverse=True)
        
        if not all_peaks:
            calculated_new_root = hashlib.sha256(b'').digest()
        else:
            calculated_new_root = all_peaks[0]['hash']
            for p in all_peaks[1:]:
                calculated_new_root = _hash_node(calculated_new_root, p['hash'])

        return calculated_new_root.hex() == new_root_hex