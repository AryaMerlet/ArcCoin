from src.core.transaction import Transaction


class Mempool:
    def __init__(self):
        self.pending = []

    def add(self, tx: Transaction) -> bool:
        if tx.tx_id in [t.tx_id for t in self.pending]:
            return False
        self.pending.append(tx)
        return True

    def get_valid_txs(self) -> list[Transaction]:
        return list(self.pending)

    def remove(self, tx_ids: list[str]) -> None:
        self.pending = [tx for tx in self.pending if tx.tx_id not in tx_ids]