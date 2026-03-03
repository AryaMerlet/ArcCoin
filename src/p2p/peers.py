import requests


class Peers:
    def __init__(self):
        self.urls = set()

    def add(self, url: str) -> None:
        self.urls.add(url)

    def remove(self, url: str) -> None:
        self.urls.discard(url)

    def all(self) -> list[str]:
        return list(self.urls)

    def discover(self, url: str) -> None:
        try:
            response = requests.get(f"{url}/peers")
            if response.status_code == 200:
                for peer in response.json().get("peers", []):
                    self.add(peer)
        except requests.exceptions.ConnectionError:
            pass