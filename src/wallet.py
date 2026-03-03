from src.crypto import keys, signatures
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePrivateKey


class Wallet:
    def __init__(self, private_key: EllipticCurvePrivateKey):
        self.private_key = private_key
        self.public_key = keys.derive_public_key(private_key)
        self.address = keys.derive_address(self.public_key)

    @classmethod
    def generate(cls) -> "Wallet":
        private_key = keys.generate_private_key()
        return cls(private_key)

    def sign(self, data: str) -> bytes:
        return signatures.sign(self.private_key, data)

    @staticmethod
    def verify(public_key, data: str, signature: bytes) -> bool:
        return signatures.verify(public_key, data, signature)