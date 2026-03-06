from src.core.chain import Chain
from src.core.transaction import Transaction
from src.core.validator import Validator
from src.p2p.peers import Peers
from src.p2p.broadcast import Broadcast
from src.p2p.sync import Sync
from src.crypto.keys import public_key_from_bytes
from src.core.block import Block
from flask_cors import CORS
import os
from src.core.miner import Miner
from flask import Flask, request, jsonify, Response


class Node:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.chain = Chain()
        self.peers = Peers()
        self.broadcast = Broadcast()
        self.sync = Sync(self.chain)
        self.app = Flask(__name__)
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        dashboard_path = os.path.join(BASE_DIR, 'dashboard')
        self.app = Flask(__name__, static_folder=dashboard_path, static_url_path='')
        CORS(self.app, resources={r"/*": {"origins": "*"}})
        self._register_routes()
        self.miner = Miner(difficulty=2)

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

        @self.app.route("/wallet/generate", methods=["POST"])
        def generate_wallet():
            from src.wallet import Wallet
            from cryptography.hazmat.primitives import serialization
            w = Wallet.generate()
            private_key_hex = w.private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ).decode("utf-8")
            return jsonify({
                "address": w.address,
                "private_key_hex": private_key_hex
            }), 200

        @self.app.route("/wallet/send", methods=["POST"])
        def wallet_send():
            from src.wallet import Wallet
            from cryptography.hazmat.primitives.serialization import load_pem_private_key
            from src.core.transaction import Transaction
            data = request.get_json()
            private_key = load_pem_private_key(
                data["private_key_hex"].encode("utf-8"),
                password=None
            )
            w = Wallet(private_key)
            nonce = self.chain.state.get_nonce(w.address)
            tx = Transaction(
                sender=w.address,
                recipient=data["recipient"],
                amount=float(data["amount"]),
                nonce=nonce,
                sender_public_key=private_key.public_key()
            )
            tx.signature = w.sign(tx.hash())
            if not Validator.validate_transaction(tx, self.chain.state):
                return jsonify({"error": "invalid transaction"}), 400
            self.chain.add_transaction(tx)
            self.broadcast.send_tx(tx, self.peers.all())
            return jsonify({"status": "ok"}), 200

        @self.app.route("/mine", methods=["POST"])
        def mine():
            txs = self.chain.mempool.get_valid_txs()
            if not txs:
                return jsonify({"error": "no transactions to mine"}), 400
            prev = self.chain.latest()
            prev_hash = prev.header.hash() if prev else "0" * 64
            block = self.miner.create_block(self.chain.length(), prev_hash, txs)
            self.miner.mine(block)
            self.chain.add_block(block)
            self.broadcast.send_block(block, self.peers.all())
            return jsonify({"status": "mined", "block": block.to_dict()}), 200

        @self.app.route("/")
        def dashboard():
            return self.app.send_static_file("index.html")

        @self.app.after_request
        def add_cors_headers(response):
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
            return response

        @self.app.route('/', defaults={'path': ''}, methods=['OPTIONS'])
        @self.app.route('/<path:path>', methods=['OPTIONS'])
        def handle_options(path):
            return Response(status=200, headers={
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            })

        @self.app.route("/balance/<address>", methods=["GET"])
        def get_balance(address):
            return jsonify({
                "address": address,
                "balance": self.chain.state.get_balance(address)
            }), 200

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