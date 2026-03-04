import hashlib
from cryptography.hazmat.primitives.asymmetric.ec import (
    generate_private_key as _generate_ec_key,
    SECP256K1,
    EllipticCurvePrivateKey
)
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePublicKey
def public_key_from_bytes(key_bytes: bytes) -> EllipticCurvePublicKey:
    from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
    from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePublicKey
    from cryptography.hazmat.primitives.asymmetric.ec import SECP256K1
    from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePublicNumbers
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature
    from cryptography.hazmat.primitives.asymmetric.ec import ECDH
    return EllipticCurvePublicKey.from_encoded_point(SECP256K1(), key_bytes)

from cryptography.hazmat.primitives import serialization


def generate_private_key() -> EllipticCurvePrivateKey:
    return _generate_ec_key(SECP256K1())


def derive_public_key(private_key: EllipticCurvePrivateKey) -> bytes:
    return private_key.public_key().public_bytes(
        encoding=serialization.Encoding.X962,
        format=serialization.PublicFormat.UncompressedPoint
    )


def derive_address(public_key: bytes) -> str:
    sha = hashlib.sha256(public_key).digest()
    ripemd = hashlib.new("ripemd160", sha).digest()
    return "ARC" + ripemd.hex()

from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePublicKey


