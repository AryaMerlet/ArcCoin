from src.crypto.hash import sha256, merkle_root


def test_sha256_string():
    result = sha256("hello")
    assert isinstance(result, str)
    assert len(result) == 64


def test_sha256_dict():
    result = sha256({"key": "value"})
    assert isinstance(result, str)
    assert len(result) == 64


def test_sha256_bytes():
    result = sha256(b"hello")
    assert isinstance(result, str)
    assert len(result) == 64


def test_sha256_avalanche():
    h1 = sha256("hello")
    h2 = sha256("hello!")
    assert h1 != h2


def test_merkle_root_empty():
    result = merkle_root([])
    assert isinstance(result, str)


def test_merkle_root_single():
    h = sha256("tx1")
    result = merkle_root([h])
    assert result == h


def test_merkle_root_even():
    hashes = [sha256(f"tx{i}") for i in range(4)]
    result = merkle_root(hashes)
    assert isinstance(result, str)
    assert len(result) == 64


def test_merkle_root_odd():
    hashes = [sha256(f"tx{i}") for i in range(3)]
    result = merkle_root(hashes)
    assert isinstance(result, str)
    assert len(result) == 64


def test_merkle_root_changes_with_different_txs():
    hashes_a = [sha256("tx1"), sha256("tx2")]
    hashes_b = [sha256("tx1"), sha256("tx3")]
    assert merkle_root(hashes_a) != merkle_root(hashes_b)