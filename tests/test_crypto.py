import pytest
from src.crypto import keys, signatures


def test_sign_and_verify():
    private_key = keys.generate_private_key()
    public_key = keys.derive_public_key(private_key)
    data = "hello arccoin"
    sig = signatures.sign(private_key, data)
    assert signatures.verify(private_key.public_key(), data, sig) is True


def test_verify_fails_on_tampered_data():
    private_key = keys.generate_private_key()
    data = "hello arccoin"
    sig = signatures.sign(private_key, data)
    assert signatures.verify(private_key.public_key(), "tampered data", sig) is False


def test_address_starts_with_arc():
    private_key = keys.generate_private_key()
    public_key = keys.derive_public_key(private_key)
    address = keys.derive_address(public_key)
    assert address.startswith("ARC")