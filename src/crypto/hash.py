import hashlib
import json


def sha256(data) -> str:
    if isinstance(data, str):
        data = data.encode("utf-8")
    elif isinstance(data, dict):
        data = json.dumps(data, sort_keys=True).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def merkle_root(tx_hashes: list) -> str:
    if not tx_hashes:
        return sha256("")
    if len(tx_hashes) == 1:
        return tx_hashes[0]

    # pair up hashes and combine them until one remains
    while len(tx_hashes) > 1:
        if len(tx_hashes) % 2 != 0:
            tx_hashes.append(tx_hashes[-1])  # duplicate last if odd number
        tx_hashes = [
            sha256(tx_hashes[i] + tx_hashes[i + 1])
            for i in range(0, len(tx_hashes), 2)
        ]

    return tx_hashes[0]