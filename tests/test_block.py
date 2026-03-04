from src.crypto import keys, signatures
from src.core.transaction import Transaction
from src.core.block_header import BlockHeader
from src.core.block import Block
from src.crypto.hash import merkle_root


def test_block_mining():
    header = BlockHeader(
        index=1,
        prev_hash="0" * 64,
        merkle_root="0" * 64,
        difficulty=2
    )
    block = Block(header, [])
    block.mine()
    assert block.header.hash().startswith("00")


def test_block_to_dict():
    header = BlockHeader(
        index=1,
        prev_hash="0" * 64,
        merkle_root="0" * 64,
        difficulty=2
    )
    block = Block(header, [])
    d = block.to_dict()
    assert d["header"]["index"] == 1
    assert d["transactions"] == []


def test_block_from_dict():
    header = BlockHeader(
        index=1,
        prev_hash="0" * 64,
        merkle_root="0" * 64,
        difficulty=2
    )
    block = Block(header, [])
    block.mine()
    d = block.to_dict()
    restored = Block.from_dict(d)
    assert restored.header.index == 1
    assert restored.header.hash() == block.header.hash()