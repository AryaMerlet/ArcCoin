import pytest

from src.core.miner import Miner
from src.core.validator import Validator
from src.core.transaction import Transaction
from src.core.block import Block
from src.core.block_header import BlockHeader
from src.core.chain import Chain
from src.core.state import State
from src.crypto import keys, signatures


def make_tx(sender_private_key, sender_address, recipient, amount, nonce):
    tx = Transaction(
        sender=sender_address,
        recipient=recipient,
        amount=amount,
        nonce=nonce,
        sender_public_key=sender_private_key.public_key()
    )
    tx.signature = signatures.sign(sender_private_key, tx.hash())
    return tx


def test_validate_transaction_valid():
    private_key = keys.generate_private_key()
    address = keys.derive_address(keys.derive_public_key(private_key))
    state = State()
    state.balances[address] = 100.0
    tx = make_tx(private_key, address, "ARCbob", 10.0, 0)
    assert Validator.validate_transaction(tx, state) is True


def test_validate_transaction_no_signature():
    private_key = keys.generate_private_key()
    address = keys.derive_address(keys.derive_public_key(private_key))
    state = State()
    state.balances[address] = 100.0
    tx = Transaction(
        sender=address,
        recipient="ARCbob",
        amount=10.0,
        nonce=0,
        sender_public_key=private_key.public_key()
    )
    assert Validator.validate_transaction(tx, state) is False


def test_validate_transaction_insufficient_balance():
    private_key = keys.generate_private_key()
    address = keys.derive_address(keys.derive_public_key(private_key))
    state = State()
    state.balances[address] = 5.0
    tx = make_tx(private_key, address, "ARCbob", 10.0, 0)
    assert Validator.validate_transaction(tx, state) is False


def test_validate_transaction_wrong_nonce():
    private_key = keys.generate_private_key()
    address = keys.derive_address(keys.derive_public_key(private_key))
    state = State()
    state.balances[address] = 100.0
    tx = make_tx(private_key, address, "ARCbob", 10.0, 5)
    assert Validator.validate_transaction(tx, state) is False


def test_validate_block_no_prev():
    header = BlockHeader(index=0, prev_hash="0" * 64, merkle_root="0" * 64, difficulty=1)
    block = Block(header, [])
    miner = Miner(difficulty=1)
    miner.mine(block)
    assert Validator.validate_block(block, None) is True


def test_validate_block_valid():
    header1 = BlockHeader(index=0, prev_hash="0" * 64, merkle_root="0" * 64, difficulty=1)
    block1 = Block(header1, [])
    miner = Miner(difficulty=1)
    miner.mine(block1)
    header2 = BlockHeader(index=1, prev_hash=block1.header.hash(), merkle_root="0" * 64, difficulty=1)
    block2 = Block(header2, [])
    miner = Miner(difficulty=1)
    miner.mine(block2)
    assert Validator.validate_block(block2, block1) is True


def test_validate_block_wrong_prev_hash():
    header1 = BlockHeader(index=0, prev_hash="0" * 64, merkle_root="0" * 64, difficulty=1)
    block1 = Block(header1, [])
    miner = Miner(difficulty=1)
    miner.mine(block1)
    header2 = BlockHeader(index=1, prev_hash="wronghash", merkle_root="0" * 64, difficulty=1)
    block2 = Block(header2, [])
    miner = Miner(difficulty=1)
    miner.mine(block2)
    assert Validator.validate_block(block2, block1) is False


def test_validate_block_invalid_pow():
    header1 = BlockHeader(index=0, prev_hash="0" * 64, merkle_root="0" * 64, difficulty=1)
    block1 = Block(header1, [])
    miner = Miner(difficulty=1)
    miner.mine(block1)
    header2 = BlockHeader(index=1, prev_hash=block1.header.hash(), merkle_root="0" * 64, difficulty=4)
    block2 = Block(header2, [])
    # intentionally not mining
    assert Validator.validate_block(block2, block1) is False


def test_validate_chain_valid():
    chain = Chain()
    header = BlockHeader(index=0, prev_hash="0" * 64, merkle_root="0" * 64, difficulty=1)
    block = Block(header, [])
    miner = Miner(difficulty=1)
    miner.mine(block)
    chain.add_block(block)
    assert Validator.validate_chain(chain) is True


def test_select_chain_picks_longest():
    chain_a = Chain()
    chain_b = Chain()
    for i in range(3):
        header = BlockHeader(index=i, prev_hash="0" * 64, merkle_root="0" * 64, difficulty=1)
        block = Block(header, [])
        miner = Miner(difficulty=1)
        miner.mine(block)
        chain_a.add_block(block)
    header = BlockHeader(index=0, prev_hash="0" * 64, merkle_root="0" * 64, difficulty=1)
    block = Block(header, [])
    miner = Miner(difficulty=1)
    miner.mine(block)
    chain_b.add_block(block)
    assert Validator.select_chain(chain_a, chain_b) == chain_a


def test_select_chain_picks_remote_if_longer():
    chain_a = Chain()
    chain_b = Chain()

    header = BlockHeader(index=0, prev_hash="0" * 64, merkle_root="0" * 64, difficulty=1)
    block = Block(header, [])
    miner = Miner(difficulty=1)
    miner.mine(block)
    chain_a.add_block(block)

    prev_hash = "0" * 64
    for i in range(3):
        header = BlockHeader(index=i, prev_hash=prev_hash, merkle_root="0" * 64, difficulty=1)
        block = Block(header, [])
        miner = Miner(difficulty=1)
        miner.mine(block)
        prev_hash = block.header.hash()
        chain_b.add_block(block)

    assert Validator.select_chain(chain_a, chain_b) == chain_b

def test_validate_transaction_wrong_signature():
        private_key_a = keys.generate_private_key()
        private_key_b = keys.generate_private_key()
        address = keys.derive_address(keys.derive_public_key(private_key_a))
        state = State()
        state.balances[address] = 100.0
        tx = Transaction(
            sender=address,
            recipient="ARCbob",
            amount=10.0,
            nonce=0,
            sender_public_key=private_key_a.public_key()
        )
        # sign with wrong key
        tx.signature = signatures.sign(private_key_b, tx.hash())
        assert Validator.validate_transaction(tx, state) is False

def test_validate_chain_invalid():
            chain = Chain()
            header1 = BlockHeader(index=0, prev_hash="0" * 64, merkle_root="0" * 64, difficulty=1)
            block1 = Block(header1, [])
            miner = Miner(difficulty=1)
            miner.mine(block1)
            chain.add_block(block1)

            # second block with wrong prev_hash
            header2 = BlockHeader(index=1, prev_hash="wronghash", merkle_root="0" * 64, difficulty=1)
            block2 = Block(header2, [])
            miner = Miner(difficulty=1)
            miner.mine(block1)
            chain.add_block(block2)

            assert Validator.validate_chain(chain) is False