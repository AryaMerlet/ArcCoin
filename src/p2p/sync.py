import requests
from src.core.validation import Validator


class Sync:
    def __init__(self, chain):
        self.chain = chain

    def fetch_chain(self, url: str) -> dict:
        try:
            response = requests.get(f"{url}/chain")
            if response.status_code == 200:
                return response.json()
            return None
        except requests.exceptions.ConnectionError:
            return None

    def resolve(self, peers: list[str]) -> bool:
        new_chain = Validator.select_chain(self.chain, peers)
        if new_chain != self.chain:
            self.chain = new_chain
            return True
        return False