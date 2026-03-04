from src.core.chain import Chain
from src.core.block import Block
from src.core.block_header import BlockHeader
from src.core.transaction import Transaction
from src.core.validator import Validator
from src.crypto import keys, signatures


def test_add_block():
    chain = Chain()
    header = BlockHeader(index=0, prev_hash="0" * 64, merkle_root="0" * 64, difficulty=2)
    block = Block(header, [])
    block.mine()
    assert chain.add_block(block) is True
    assert chain.length() == 1


def test_chain_validation():
    chain = Chain()
    header = BlockHeader(index=0, prev_hash="0" * 64, merkle_root="0" * 64, difficulty=2)
    block = Block(header, [])
    block.mine()
    chain.add_block(block)
    assert Validator.validate_chain(chain) is True


def test_select_longest_chain():
    chain_a = Chain()
    chain_b = Chain()

    for i in range(2):
        header = BlockHeader(index=i, prev_hash="0" * 64, merkle_root="0" * 64, difficulty=1)
        block = Block(header, [])
        block.mine()
        chain_a.add_block(block)

    header = BlockHeader(index=0, prev_hash="0" * 64, merkle_root="0" * 64, difficulty=1)
    block = Block(header, [])
    block.mine()
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
    block.mine()
    chain.add_block(block)

    assert chain.state.get_balance(sender) == 90.0
    assert chain.state.get_balance("ARCrecipient") == 10.0