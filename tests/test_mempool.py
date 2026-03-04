from src.core.mempool import Mempool
from src.core.transaction import Transaction
from src.crypto import keys


def make_tx(nonce=0):
    private_key = keys.generate_private_key()
    public_key = keys.derive_public_key(private_key)
    address = keys.derive_address(public_key)
    return Transaction(
        sender=address,
        recipient="ARCbob",
        amount=10.0,
        nonce=nonce,
        sender_public_key=private_key.public_key()
    )


def test_add_transaction():
    mempool = Mempool()
    tx = make_tx()
    assert mempool.add(tx) is True
    assert len(mempool.pending) == 1


def test_add_duplicate_rejected():
    mempool = Mempool()
    tx = make_tx()
    mempool.add(tx)
    assert mempool.add(tx) is False
    assert len(mempool.pending) == 1


def test_get_valid_txs():
    mempool = Mempool()
    tx = make_tx()
    mempool.add(tx)
    result = mempool.get_valid_txs()
    assert len(result) == 1


def test_remove():
    mempool = Mempool()
    tx = make_tx()
    mempool.add(tx)
    mempool.remove([tx.tx_id])
    assert len(mempool.pending) == 0