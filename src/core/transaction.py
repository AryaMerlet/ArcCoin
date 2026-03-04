import uuid
from cryptography.hazmat.primitives import serialization
from src.crypto.hash import sha256
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePublicKey


class Transaction:
    def __init__(
        self,
        sender: str,
        recipient: str,
        amount: float,
        nonce: int,
        sender_public_key: EllipticCurvePublicKey,
        tx_type: str = "payment",
        payload: dict = None,
    ):
        self.tx_id = str(uuid.uuid4())
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.nonce = nonce
        self.tx_type = tx_type
        self.payload = payload or {}
        self.signature = None
        self.sender_public_key = sender_public_key


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
            "signature": self.signature.hex() if self.signature else None,
            "sender_public_key": self.sender_public_key.public_bytes(
                encoding=serialization.Encoding.X962,
                format=serialization.PublicFormat.UncompressedPoint
            ).hex() if not isinstance(self.sender_public_key, str) else self.sender_public_key,
        }

    @staticmethod
    def from_dict(data: dict) -> "Transaction":
        tx = Transaction(
            sender=data["sender"],
            recipient=data["recipient"],
            amount=data["amount"],
            nonce=data["nonce"],
            sender_public_key=data["sender_public_key"],
            tx_type=data["tx_type"],
            payload=data["payload"]
        )
        tx.tx_id = data["tx_id"]
        tx.signature = bytes.fromhex(data["signature"]) if data["signature"] else None
        return tx