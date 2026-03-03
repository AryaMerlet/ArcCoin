from src.core.transaction import Transaction


class State:
    def __init__(self):
        self.balances = {}
        self.nonces = {}
        self.contracts = {}

    def get_balance(self, address: str) -> float:
        return self.balances.get(address, 0.0)

    def get_nonce(self, address: str) -> int:
        return self.nonces.get(address, 0)

    def apply(self, tx: Transaction) -> None:
        self.balances[tx.sender] = self.get_balance(tx.sender) - tx.amount
        self.balances[tx.recipient] = self.get_balance(tx.recipient) + tx.amount
        self.nonces[tx.sender] = tx.nonce + 1

    def apply_block(self, transactions: list[Transaction]) -> None:
        for tx in transactions:
            self.apply(tx)