from src.wallet import Wallet
from src.core.transaction import Transaction


def test_wallet_generation():
    wallet = Wallet.generate()
    assert wallet.address.startswith("ARC")
    assert wallet.public_key is not None
    assert wallet.private_key is not None


def test_wallet_sign_and_verify():
    wallet = Wallet.generate()
    tx = Transaction(
        sender=wallet.address,
        recipient="ARCrecipient",
        amount=10.0,
        nonce=0,
        sender_public_key=wallet.private_key.public_key()
    )
    tx.signature = wallet.sign(tx.hash())
    assert Wallet.verify(wallet.private_key.public_key(), tx.hash(), tx.signature) is True


def test_two_wallets_different_addresses():
    wallet_a = Wallet.generate()
    wallet_b = Wallet.generate()
    assert wallet_a.address != wallet_b.address