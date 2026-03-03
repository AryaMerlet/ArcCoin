from flask import Flask, request, jsonify
from src.core.chain import Chain
from src.core.transaction import Transaction
from src.core.validation import Validator
from src.p2p.peers import Peers
from src.p2p.broadcast import Broadcast
from src.p2p.sync import Sync


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
                sender_public_key=data["sender_public_key"],
            )
            tx.signature = bytes.fromhex(data["signature"])
            if not Validator.validate_transaction(tx, self.chain.state):
                return jsonify({"error": "invalid transaction"}), 400
            self.chain.add_transaction(tx)
            self.broadcast.send_tx(tx, self.peers.all())
            return jsonify({"status": "ok"}), 200

        @self.app.route("/block", methods=["POST"])
        def post_block():
            data = request.get_json()
            # deserialization handled in next branch
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

    def start(self):
        self.sync.resolve(self.peers.all())
        self.app.run(host=self.host, port=self.port)