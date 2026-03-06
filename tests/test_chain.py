from src.core.chain import Chain
from src.core.block import Block
from src.core.block_header import BlockHeader
from src.core.miner import Miner
from src.core.transaction import Transaction
from src.core.validator import Validator
from src.crypto import keys, signatures


def test_add_block():
    chain = Chain()
    header = BlockHeader(index=0, prev_hash="0" * 64, merkle_root="0" * 64, difficulty=2)
    block = Block(header, [])
    miner = Miner(difficulty=1)
    miner.mine(block)
    assert chain.add_block(block) is True
    assert chain.length() == 1


def test_chain_validation():
    chain = Chain()
    header = BlockHeader(index=0, prev_hash="0" * 64, merkle_root="0" * 64, difficulty=2)
    block = Block(header, [])
    miner = Miner(difficulty=1)
    miner.mine(block)
    chain.add_block(block)
    assert Validator.validate_chain(chain) is True


def test_select_longest_chain():
    chain_a = Chain()
    chain_b = Chain()

    for i in range(2):
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

    result = Validator.select_chain(chain_a, chain_b)
    assert result == chain_a


def test_state_updates_after_block():
    chain = Chain()
    private_key = keys.generate_private_key()
    public_key = keys.derive_public_key(private_key)
    sender = keys.derive_address(public_key)

    chain.state.balances[sender] = 100.0

    tx = Transaction(
        sender=sender,
        recipient="ARCrecipient",
        amount=10.0,
        nonce=0,
        sender_public_key=private_key.public_key()
    )
    tx.signature = signatures.sign(private_key, tx.hash())

    header = BlockHeader(index=0, prev_hash="0" * 64, merkle_root="0" * 64, difficulty=1)
    block = Block(header, [tx])
    miner = Miner(difficulty=1)
    miner.mine(block)
    chain.add_block(block)

    assert chain.state.get_balance(sender) == 90.0
    assert chain.state.get_balance("ARCrecipient") == 10.0

def make_block(index, prev_hash, difficulty=1):
    header = BlockHeader(index=index, prev_hash=prev_hash, merkle_root="0" * 64, difficulty=difficulty)
    block = Block(header, [])
    miner = Miner(difficulty=1)
    miner.mine(block)
    return block


def test_add_transaction():
    chain = Chain()
    private_key = keys.generate_private_key()
    address = keys.derive_address(keys.derive_public_key(private_key))
    tx = Transaction(
        sender=address,
        recipient="ARCbob",
        amount=10.0,
        nonce=0,
        sender_public_key=private_key.public_key()
    )
    assert chain.add_transaction(tx) is True


def test_latest_block():
    chain = Chain()
    block = make_block(0, "0" * 64)
    chain.add_block(block)
    assert chain.latest() == block


def test_latest_empty_chain():
    chain = Chain()
    assert chain.latest() is None


def test_select_longer_chain():
    chain_a = Chain()
    chain_b = Chain()
    chain_a.add_block(make_block(0, "0" * 64))
    chain_a.add_block(make_block(1, "0" * 64))
    chain_b.add_block(make_block(0, "0" * 64))
    assert chain_a.select(chain_b) == chain_a


def test_to_dict():
    chain = Chain()
    chain.add_block(make_block(0, "0" * 64))
    d = chain.to_dict()
    assert d["length"] == 1
    assert len(d["blocks"]) == 1


def test_from_dict():
    chain = Chain()
    prev_hash = "0" * 64
    for i in range(2):
        block = make_block(i, prev_hash)
        prev_hash = block.header.hash()
        chain.add_block(block)
    restored = Chain.from_dict(chain.to_dict())
    assert restored.length() == 2