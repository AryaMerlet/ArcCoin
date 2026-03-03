from cryptography.hazmat.primitives.asymmetric.ec import (
    ECDSA,
    EllipticCurvePrivateKey,
    EllipticCurvePublicKey
)
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidSignature


def sign(private_key: EllipticCurvePrivateKey, data: str) -> bytes:
    return private_key.sign(
        data.encode("utf-8"),
        ECDSA(hashes.SHA256())
    )


def verify(public_key: EllipticCurvePublicKey, data: str, signature: bytes) -> bool:
    try:
        public_key.verify(
            signature,
            data.encode("utf-8"),
            ECDSA(hashes.SHA256())
        )
        return True
    except InvalidSignature:
        return False