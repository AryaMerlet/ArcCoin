import pytest
from src.crypto import keys, signatures
from src.core.transaction import Transaction


def test_transaction_hash_is_consistent():
    private_key = keys.generate_private_key()
    public_key = keys.derive_public_key(private_key)
    address = keys.derive_address(public_key)
    tx = Transaction(
        sender=address,
        recipient="ARCrecipient",
        amount=10.0,
        nonce=0,
        sender_public_key=private_key.public_key()
    )
    assert tx.hash() == tx.hash()


def test_transaction_signature():
    private_key = keys.generate_private_key()
    public_key = keys.derive_public_key(private_key)
    address = keys.derive_address(public_key)
    tx = Transaction(
        sender=address,
        recipient="ARCrecipient",
        amount=10.0,
        nonce=0,
        sender_public_key=private_key.public_key()
    )
    tx.signature = signatures.sign(private_key, tx.hash())
    assert signatures.verify(private_key.public_key(), tx.hash(), tx.signature) is True


def test_transaction_to_dict():
    private_key = keys.generate_private_key()
    public_key = keys.derive_public_key(private_key)
    address = keys.derive_address(public_key)
    tx = Transaction(
        sender=address,
        recipient="ARCrecipient",
        amount=10.0,
        nonce=0,
        sender_public_key=private_key.public_key()
    )
    d = tx.to_dict()
    assert d["sender"] == address
    assert d["amount"] == 10.0

def test_from_dict():
    private_key = keys.generate_private_key()
    public_key = keys.derive_public_key(private_key)
    address = keys.derive_address(public_key)
    tx = Transaction(
        sender=address,
        recipient="ARCrecipient",
        amount=10.0,
        nonce=0,
        sender_public_key=private_key.public_key()
    )
    tx.signature = signatures.sign(private_key, tx.hash())
    d = tx.to_dict()
    d["sender_public_key"] = private_key.public_key()
    restored = Transaction.from_dict(d)
    assert restored.sender == tx.sender
    assert restored.amount == tx.amount
    assert restored.nonce == tx.nonce