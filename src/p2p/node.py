from flask import Flask, request, jsonify
from src.core.chain import Chain
from src.core.transaction import Transaction
from src.core.validator import Validator
from src.p2p.peers import Peers
from src.p2p.broadcast import Broadcast
from src.p2p.sync import Sync
from src.core.block import Block
from src.crypto.keys import public_key_from_bytes

class Node:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.chain = Chain()
        self.peers = Peers()
        self.broadcast = Broadcast()
        self.sync = Sync(self.chain)
        self.app = Flask(__name__)
        self._register_routes()

    def _register_routes(self):
        @self.app.route("/transaction", methods=["POST"])
        def post_transaction():
            data = request.get_json()
            tx = Transaction(
                sender=data["sender"],
                recipient=data["recipient"],
                amount=data["amount"],
                nonce=data["nonce"],
                sender_public_key=public_key_from_bytes(bytes.fromhex(data["sender_public_key"])),
            )
            tx.tx_id = data["tx_id"]
            tx.signature = bytes.fromhex(data["signature"]) if data["signature"] else None
            if not Validator.validate_transaction(tx, self.chain.state):
                return jsonify({"error": "invalid transaction"}), 400
            self.chain.add_transaction(tx)
            self.broadcast.send_tx(tx, self.peers.all())
            return jsonify({"status": "ok"}), 200

        @self.app.route("/block", methods=["POST"])
        def post_block():
            data = request.get_json()
            block = Block.from_dict(data)
            if not Validator.validate_block(block, self.chain.latest()):
                return jsonify({"error": "invalid block"}), 400
            self.chain.add_block(block)
            self.broadcast.send_block(block, self.peers.all())
            return jsonify({"status": "ok"}), 200

        @self.app.route("/chain", methods=["GET"])
        def get_chain():
            return jsonify(self.chain.to_dict()), 200

        @self.app.route("/peers", methods=["POST"])
        def post_peers():
            url = request.get_json().get("url")
            self.peers.add(url)
            return jsonify({"status": "ok"}), 200

        @self.app.route("/peers", methods=["GET"])
        def get_peers():
            return jsonify({"peers": self.peers.all()}), 200

        @self.app.route("/seed", methods=["POST"])
        def seed_balance():
            data = request.get_json()
            self.chain.state.balances[data["address"]] = data["amount"]
            return jsonify({"status": "ok"}), 200

        @self.app.route("/mempool", methods=["GET"])
        def get_mempool():
            return jsonify({"pending": [tx.to_dict() for tx in self.chain.mempool.pending]}), 200

        @self.app.route("/mine", methods=["POST"])
        def mine():
            txs = self.chain.mempool.get_valid_txs()
            if not txs:
                return jsonify({"error": "no transactions to mine"}), 400
            from src.crypto.hash import merkle_root
            from src.core.block_header import BlockHeader
            from src.core.block import Block
            prev = self.chain.latest()
            prev_hash = prev.header.hash() if prev else "0" * 64
            index = self.chain.length()
            m_root = merkle_root([tx.hash() for tx in txs])
            header = BlockHeader(
                index=index,
                prev_hash=prev_hash,
                merkle_root=m_root,
                difficulty=2
            )
            block = Block(header, txs)
            block.mine()
            self.chain.add_block(block)
            self.broadcast.send_block(block, self.peers.all())
            return jsonify({"status": "mined", "block": block.to_dict()}), 200

    def start(self):
        self.sync.resolve(self.peers.all())
        self.app.run(host=self.host, port=self.port)

if __name__ == "__main__": # pragma: no cover
    import argparse
    parser = argparse.ArgumentParser(description="ArcCoin Node")
    parser.add_argument("--host", type=str, default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5001)
    args = parser.parse_args()
    node = Node(args.host, args.port)
    node.start()