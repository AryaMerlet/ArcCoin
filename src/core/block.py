from src.crypto.hash import merkle_root
from src.core.block_header import BlockHeader
from src.core.transaction import Transaction


class Block:
    def __init__(self, header: BlockHeader, transactions: list[Transaction]):
        self.header = header
        self.transactions = transactions

    def mine(self) -> None:
        target = "0" * self.header.difficulty
        while not self.header.hash().startswith(target):
            self.header.nonce += 1

    def to_dict(self) -> dict:
        return {
            "header": self.header.to_dict(),
            "transactions": [tx.to_dict() for tx in self.transactions]
        }