import re
import hashlib

import requests

def update_hash(source, source_hash):
    if source.strip().lower().startswith('http'):
        data = requests.get(source)
        hasher = hashlib.sha256(data)
        new_hash = 'sha256={0}'.format(hasher.hexdigest())
    if source_hash == new_hash:
        return None
    return new_hash

def update_source_hashes(state):
    new_state = _update_source_hashes(state)
    return new_state, new_state != state
