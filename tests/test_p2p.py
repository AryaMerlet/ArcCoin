import requests
import pytest
from unittest.mock import patch, MagicMock
from src.p2p.peers import Peers
from src.p2p.broadcast import Broadcast
from src.p2p.sync import Sync
from src.core.chain import Chain
from src.core.block import Block
from src.core.block_header import BlockHeader
from src.p2p.node import Node
from src.crypto import keys, signatures
from cryptography.hazmat.primitives import serialization


# ── PEERS ────────────────────────────────────────────

def test_peers_add():
    peers = Peers()
    peers.add("http://127.0.0.1:5001")
    assert "http://127.0.0.1:5001" in peers.all()


def test_peers_remove():
    peers = Peers()
    peers.add("http://127.0.0.1:5001")
    peers.remove("http://127.0.0.1:5001")
    assert "http://127.0.0.1:5001" not in peers.all()


def test_peers_all():
    peers = Peers()
    peers.add("http://127.0.0.1:5001")
    peers.add("http://127.0.0.1:5002")
    assert len(peers.all()) == 2


def test_peers_discover():
    peers = Peers()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"peers": ["http://127.0.0.1:5002"]}
    with patch("requests.get", return_value=mock_response):
        peers.discover("http://127.0.0.1:5001")
    assert "http://127.0.0.1:5002" in peers.all()


def test_peers_discover_connection_error():
    peers = Peers()
    with patch("requests.get", side_effect=requests.exceptions.ConnectionError):
        peers.discover("http://127.0.0.1:5001")
    assert len(peers.all()) == 0


# ── BROADCAST ────────────────────────────────────────

def make_block():
    header = BlockHeader(index=0, prev_hash="0" * 64, merkle_root="0" * 64, difficulty=1)
    block = Block(header, [])
    block.mine()
    return block


def test_broadcast_is_seen():
    broadcast = Broadcast()
    broadcast.seen_ids.add("tx123")
    assert broadcast.is_seen("tx123") is True
    assert broadcast.is_seen("tx999") is False


def test_broadcast_send_tx():
    from src.core.transaction import Transaction
    from src.crypto import keys
    broadcast = Broadcast()
    private_key = keys.generate_private_key()
    address = keys.derive_address(keys.derive_public_key(private_key))
    tx = Transaction(
        sender=address,
        recipient="ARCbob",
        amount=10.0,
        nonce=0,
        sender_public_key=private_key.public_key()
    )
    with patch("requests.post") as mock_post:
        broadcast.send_tx(tx, ["http://127.0.0.1:5001"])
        assert mock_post.called


def test_broadcast_send_tx_already_seen():
    from src.core.transaction import Transaction
    from src.crypto import keys
    broadcast = Broadcast()
    private_key = keys.generate_private_key()
    address = keys.derive_address(keys.derive_public_key(private_key))
    tx = Transaction(
        sender=address,
        recipient="ARCbob",
        amount=10.0,
        nonce=0,
        sender_public_key=private_key.public_key()
    )
    broadcast.seen_ids.add(tx.tx_id)
    with patch("requests.post") as mock_post:
        broadcast.send_tx(tx, ["http://127.0.0.1:5001"])
        assert not mock_post.called


def test_broadcast_send_block():
    broadcast = Broadcast()
    block = make_block()
    with patch("requests.post") as mock_post:
        broadcast.send_block(block, ["http://127.0.0.1:5001"])
        assert mock_post.called


def test_broadcast_send_block_already_seen():
    broadcast = Broadcast()
    block = make_block()
    broadcast.seen_ids.add(block.header.hash())
    with patch("requests.post") as mock_post:
        broadcast.send_block(block, ["http://127.0.0.1:5001"])
        assert not mock_post.called


def test_broadcast_connection_error():
    broadcast = Broadcast()
    block = make_block()
    with patch("requests.post", side_effect=requests.exceptions.ConnectionError):
        broadcast.send_block(block, ["http://127.0.0.1:5001"])


# ── SYNC ─────────────────────────────────────────────

def test_sync_fetch_chain_success():
    chain = Chain()
    sync = Sync(chain)
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"length": 0, "blocks": []}
    with patch("requests.get", return_value=mock_response):
        result = sync.fetch_chain("http://127.0.0.1:5001")
    assert result == {"length": 0, "blocks": []}


def test_sync_fetch_chain_failure():
    chain = Chain()
    sync = Sync(chain)
    with patch("requests.get", side_effect=requests.exceptions.ConnectionError):
        result = sync.fetch_chain("http://127.0.0.1:5001")
    assert result is None


def test_sync_resolve_no_peers():
    chain = Chain()
    sync = Sync(chain)
    result = sync.resolve([])
    assert result is False


def test_sync_resolve_longer_chain():
    local_chain = Chain()
    sync = Sync(local_chain)

    remote_chain = Chain()
    prev_hash = "0" * 64
    for i in range(2):
        header = BlockHeader(index=i, prev_hash=prev_hash, merkle_root="0" * 64, difficulty=1)
        block = Block(header, [])
        block.mine()
        prev_hash = block.header.hash()
        remote_chain.add_block(block)

    with patch.object(sync, "fetch_chain", return_value=remote_chain.to_dict()):
        result = sync.resolve(["http://127.0.0.1:5001"])
    assert result is True

def test_broadcast_send_tx_connection_error():
    from src.core.transaction import Transaction
    from src.crypto import keys
    broadcast = Broadcast()
    private_key = keys.generate_private_key()
    address = keys.derive_address(keys.derive_public_key(private_key))
    tx = Transaction(
        sender=address,
        recipient="ARCbob",
        amount=10.0,
        nonce=0,
        sender_public_key=private_key.public_key()
    )
    with patch("requests.post", side_effect=requests.exceptions.ConnectionError):
        broadcast.send_tx(tx, ["http://127.0.0.1:5001"])


def test_sync_fetch_chain_non_200():
    chain = Chain()
    sync = Sync(chain)
    mock_response = MagicMock()
    mock_response.status_code = 404
    with patch("requests.get", return_value=mock_response):
        result = sync.fetch_chain("http://127.0.0.1:5001")
    assert result is None


def test_sync_resolve_fetch_returns_none():
    chain = Chain()
    sync = Sync(chain)
    with patch.object(sync, "fetch_chain", return_value=None):
        result = sync.resolve(["http://127.0.0.1:5001"])
    assert result is False


@pytest.fixture
def client():
    node = Node("127.0.0.1", 5001)
    node.app.config["TESTING"] = True
    return node.app.test_client(), node


def test_get_chain(client):
    app_client, node = client
    response = app_client.get("/chain")
    assert response.status_code == 200
    data = response.get_json()
    assert "blocks" in data


def test_post_peers(client):
    app_client, node = client
    response = app_client.post("/peers", json={"url": "http://127.0.0.1:5002"})
    assert response.status_code == 200


def test_get_peers(client):
    app_client, node = client
    app_client.post("/peers", json={"url": "http://127.0.0.1:5002"})
    response = app_client.get("/peers")
    assert response.status_code == 200
    assert "http://127.0.0.1:5002" in response.get_json()["peers"]


def test_post_valid_transaction(client):
    app_client, node = client
    private_key = keys.generate_private_key()
    public_key = keys.derive_public_key(private_key)
    address = keys.derive_address(public_key)
    node.chain.state.balances[address] = 100.0
    from src.core.transaction import Transaction
    tx = Transaction(
        sender=address,
        recipient="ARCbob",
        amount=10.0,
        nonce=0,
        sender_public_key=private_key.public_key()
    )
    tx.signature = signatures.sign(private_key, tx.hash())
    data = tx.to_dict()
    data["sender_public_key"] = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.X962,
        format=serialization.PublicFormat.UncompressedPoint
    ).hex()
    with patch("src.p2p.node.Broadcast.send_tx"):
        response = app_client.post("/transaction", json=data)
    assert response.status_code == 200


def test_post_invalid_transaction(client):
    app_client, node = client
    private_key = keys.generate_private_key()
    public_key = keys.derive_public_key(private_key)
    address = keys.derive_address(public_key)
    from src.core.transaction import Transaction
    tx = Transaction(
        sender=address,
        recipient="ARCbob",
        amount=10.0,
        nonce=0,
        sender_public_key=private_key.public_key()
    )
    data = tx.to_dict()
    data["sender_public_key"] = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.X962,
        format=serialization.PublicFormat.UncompressedPoint
    ).hex()
    response = app_client.post("/transaction", json=data)
    assert response.status_code == 400


def test_post_valid_block(client):
    app_client, node = client
    header = BlockHeader(index=0, prev_hash="0" * 64, merkle_root="0" * 64, difficulty=1)
    block = Block(header, [])
    block.mine()
    with patch("src.p2p.node.Broadcast.send_block"):
        response = app_client.post("/block", json=block.to_dict())
    assert response.status_code == 200


def test_post_invalid_block(client):
    app_client, node = client
    # add a first valid block
    header1 = BlockHeader(index=0, prev_hash="0" * 64, merkle_root="0" * 64, difficulty=1)
    block1 = Block(header1, [])
    block1.mine()
    node.chain.add_block(block1)
    # second block with wrong prev_hash
    header2 = BlockHeader(index=1, prev_hash="wronghash", merkle_root="0" * 64, difficulty=1)
    block2 = Block(header2, [])
    block2.mine()
    response = app_client.post("/block", json=block2.to_dict())
    assert response.status_code == 400