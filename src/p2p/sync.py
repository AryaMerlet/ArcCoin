import requests
from src.core.validator import Validator
from src.core.chain import Chain


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
        for url in peers:
            data = self.fetch_chain(url)
            if data is None:
                continue
        remote_chain = Chain.from_dict(data)
        new_chain = Validator.select_chain(self.chain, remote_chain)
        if new_chain != self.chain:
            self.chain = new_chain
            return True
        return False