import time
from src.crypto.hash import sha256


class BlockHeader:
    def __init__(
        self,
        index: int,
        prev_hash: str,
        merkle_root: str,
        difficulty: int,
        timestamp: float = None,
        nonce: int = 0
    ):
        self.index = index
        self.prev_hash = prev_hash
        self.merkle_root = merkle_root
        self.difficulty = difficulty
        self.timestamp = timestamp or time.time()
        self.nonce = nonce

    def hash(self) -> str:
        return sha256({
            "index": self.index,
            "prev_hash": self.prev_hash,
            "merkle_root": self.merkle_root,
            "difficulty": self.difficulty,
            "timestamp": self.timestamp,
            "nonce": self.nonce
        })

    def to_dict(self) -> dict:
        return {
            "index": self.index,
            "prev_hash": self.prev_hash,
            "merkle_root": self.merkle_root,
            "difficulty": self.difficulty,
            "timestamp": self.timestamp,
            "nonce": self.nonce
        }