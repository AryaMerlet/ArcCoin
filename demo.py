import requests
from src.wallet import Wallet
from src.core.transaction import Transaction
from cryptography.hazmat.primitives import serialization

# register peers
peers = [5001, 5002, 5003]
for port in peers:
    for other_port in peers:
        if port != other_port:
            requests.post(f"http://127.0.0.1:{port}/peers", json={"url": f"http://127.0.0.1:{other_port}"})
print("Peers registered")

# create wallets
alice = Wallet.generate()
bob = Wallet.generate()
print(f"Alice: {alice.address}")
print(f"Bob:   {bob.address}")

# seed alice on all nodes
for port in peers:
    requests.post(f"http://127.0.0.1:{port}/seed", json={"address": alice.address, "amount": 100.0})
print("Alice seeded on all nodes")

# create and send transaction
from src.core.transaction import Transaction
tx = Transaction(
    sender=alice.address,
    recipient=bob.address,
    amount=10.0,
    nonce=0,
    sender_public_key=alice.private_key.public_key()
)
tx.signature = alice.sign(tx.hash())
data = tx.to_dict()

response = requests.post("http://127.0.0.1:5001/transaction", json=data)
print(f"Transaction: {response.status_code} - {response.json()}")