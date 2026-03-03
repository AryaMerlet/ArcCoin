import uuid
from src.crypto.hash import sha256


class Transaction:
    def __init__(
        self,
        sender: str,
        recipient: str,
        amount: float,
        nonce: int,
        tx_type: str = "payment",
        payload: dict = None
    ):
        self.tx_id = str(uuid.uuid4())
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.nonce = nonce
        self.tx_type = tx_type
        self.payload = payload or {}
        self.signature = None

    def hash(self) -> str:
        return sha256({
            "sender": self.sender,
            "recipient": self.recipient,
            "amount": self.amount,
            "nonce": self.nonce,
            "tx_type": self.tx_type,
            "payload": self.payload
        })

    # convert object into dictionary so it can be serialized in JSON
    def to_dict(self) -> dict:
        return {
            "tx_id": self.tx_id,
            "sender": self.sender,
            "recipient": self.recipient,
            "amount": self.amount,
            "nonce": self.nonce,
            "tx_type": self.tx_type,
            "payload": self.payload,
            "signature": self.signature.hex() if self.signature else None
        }