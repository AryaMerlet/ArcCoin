from src.contracts.state import ContractState


def run_counter(fn: str, args: dict, caller: str, state: ContractState, address: str) -> any:
    if fn == "increment":
        current = state.get(address).get("count", 0)
        state.set(address, "count", current + 1)
        return current + 1
    if fn == "get_count":
        return state.get(address).get("count", 0)
    raise ValueError(f"Unknown function: {fn}")


def run_escrow(fn: str, args: dict, caller: str, state: ContractState, address: str) -> any:
    if fn == "deposit":
        state.set(address, "amount", args["amount"])
        state.set(address, "sender", caller)
        state.set(address, "status", "locked")
        return True
    if fn == "release":
        if state.get(address).get("status") != "locked":
            return False
        if state.get(address).get("sender") != caller:
            return False
        state.set(address, "recipient", args["recipient"])
        state.set(address, "status", "released")
        return True
    if fn == "refund":
        if state.get(address).get("sender") != caller:
            return False
        state.set(address, "status", "refunded")
        return True
    raise ValueError(f"Unknown function: {fn}")


def run_transfer(fn: str, args: dict, caller: str, state: ContractState, address: str) -> any:
    if fn == "transfer":
        if state.get(address).get("owner") != caller:
            return False
        state.set(address, "owner", args["recipient"])
        return True
    raise ValueError(f"Unknown function: {fn}")