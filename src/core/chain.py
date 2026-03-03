from src.core.block import Block
from src.core.mempool import Mempool
from src.core.state import State
from src.core.transaction import Transaction


class Chain:
    def __init__(self):
        self.blocks = []
        self.mempool = Mempool()
        self.state = State()

    def add_block(self, block: Block) -> bool:
        self.blocks.append(block)
        self.state.apply_block(block.transactions)
        self.mempool.remove([tx.tx_id for tx in block.transactions])
        return True

    def add_transaction(self, tx: Transaction) -> bool:
        return self.mempool.add(tx)

    def latest(self) -> Block:
        return self.blocks[-1] if self.blocks else None

    def length(self) -> int:
        return len(self.blocks)

    def select(self, other: "Chain") -> "Chain":
        return self if self.length() >= other.length() else other

    def to_dict(self) -> dict:
        return {
            "length": self.length(),
            "blocks": [block.to_dict() for block in self.blocks]
        }