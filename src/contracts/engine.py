from src.contracts.state import ContractState
from src.contracts import execution


class ContractEngine:
    def __init__(self):
        self.state = ContractState()
        self.contracts = {}

    def deploy(self, address: str, contract_type: str) -> bool:
        if address in self.contracts:
            return False
        self.contracts[address] = contract_type
        return True

    def call(self, address: str, fn: str, args: dict, caller: str) -> any:
        if address not in self.contracts:
            raise ValueError(f"No contract at address: {address}")
        contract_type = self.contracts[address]
        if contract_type == "counter":
            return execution.run_counter(fn, args, caller, self.state, address)
        if contract_type == "escrow":
            return execution.run_escrow(fn, args, caller, self.state, address)
        if contract_type == "transfer":
            return execution.run_transfer(fn, args, caller, self.state, address)
        raise ValueError(f"Unknown contract type: {contract_type}")

    def get_state(self, address: str) -> dict:
        return self.state.get(address)