import requests
from src.core.transaction import Transaction
from src.core.block import Block


class Broadcast:
    def __init__(self):
        self.seen_ids = set()

    def is_seen(self, msg_id: str) -> bool:
        return msg_id in self.seen_ids

    def send_tx(self, tx: Transaction, peers: list[str]) -> None:
        if self.is_seen(tx.tx_id):
            return
        self.seen_ids.add(tx.tx_id)
        for peer in peers:
            try:
                requests.post(f"{peer}/transaction", json=tx.to_dict())
            except requests.exceptions.ConnectionError:
                pass

    def send_block(self, block: Block, peers: list[str]) -> None:
        block_hash = block.header.hash()
        if self.is_seen(block_hash):
            return
        self.seen_ids.add(block_hash)
        for peer in peers:
            try:
                requests.post(f"{peer}/block", json=block.to_dict())
            except requests.exceptions.ConnectionError:
                pass