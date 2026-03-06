from src.core.block import Block
from src.core.block_header import BlockHeader
from src.core.transaction import Transaction
from src.crypto.hash import merkle_root


class Miner:
    def __init__(self, difficulty: int = 2):
        self.difficulty = difficulty

    def mine(self, block: Block) -> Block:
        target = "0" * self.difficulty
        while not block.header.hash().startswith(target):
            block.header.nonce += 1
        return block

    def create_block(self, index: int, prev_hash: str, transactions: list[Transaction]) -> Block:
        m_root = merkle_root([tx.hash() for tx in transactions])
        header = BlockHeader(
            index=index,
            prev_hash=prev_hash,
            merkle_root=m_root,
            difficulty=self.difficulty
        )
        return Block(header, transactions)