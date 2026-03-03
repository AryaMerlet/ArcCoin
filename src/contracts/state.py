class ContractState:
    def __init__(self):
        self.data = {}

    def get(self, address: str) -> dict:
        return self.data.get(address, {})

    def set(self, address: str, key: str, value) -> None:
        if address not in self.data:
            self.data[address] = {}
        self.data[address][key] = value