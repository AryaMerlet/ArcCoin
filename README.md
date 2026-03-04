# ArcCoin

A minimal functional blockchain implementation in Python, built for educational purposes.
Ticker: **ARC**

## UML Class Diagram

![UML Class Diagram](docs/blockchain_uml.png)

## Project Structure
```
src/
├── crypto/         # hash.py, keys.py, signatures.py
├── core/           # transaction.py, block_header.py, block.py
│                   # chain.py, mempool.py, state.py, validator.py
├── contracts/      # engine.py, state.py, execution.py
└── p2p/            # node.py, peers.py, broadcast.py, sync.py
tests/              # unit tests and network scenarios
wallet.py           # client-side key and signing management
```

## Setup
```bash
python -m venv .venv
.venv\Scripts\activate       # Windows
source .venv/bin/activate    # Mac/Linux
pip install -r requirements.txt
```

## Launch nodes

Open 3 separate terminals and run:
```bash
python -m src.p2p.node --host 127.0.0.1 --port 5001
python -m src.p2p.node --host 127.0.0.1 --port 5002
python -m src.p2p.node --host 127.0.0.1 --port 5003
```

## API Routes

| Method | Route | Description |
|--------|-------|-------------|
| POST | `/transaction` | Submit a signed transaction |
| POST | `/block` | Receive a broadcast block |
| POST | `/peers` | Register a peer node |
| GET | `/peers` | List known peers |
| GET | `/chain` | Get the full chain |
| GET | `/mempool` | Get pending transactions |
| POST | `/mine` | Mine a block from mempool |
| POST | `/seed` | Seed an address with balance (demo only) |

## Run tests
```bash
pytest -v
```

## Dependencies

- `flask` — HTTP API for each node
- `cryptography` — ECDSA keys and signatures
- `requests` — P2P communication between nodes
- `pytest` — automated tests

---

## Data Model

### Transaction
Represents a signed action on the network — a payment or a contract call.
Fields: `tx_id`, `sender`, `recipient`, `amount`, `nonce`, `type`, `payload`, `signature`, `sender_public_key`.

### BlockHeader
The metadata of a block. Contains `index`, `prev_hash`, `merkle_root`, `timestamp`, `difficulty`, `nonce`.
Only the header is hashed for PoW — not the full transaction list.

### Block
A container grouping a `BlockHeader` and a list of `Transaction` objects.
The `mine()` method increments the nonce until the header hash starts with enough leading zeros.

### Chain
The ordered list of validated blocks. Owns the `State` and the `Mempool`.
New transactions wait in the mempool until a block is mined and added to the chain.

### State
The current snapshot of the world — all balances and nonces derived from replaying every transaction.
Updated every time a new block is added to the chain.

---

## Hashing and Integrity

- **Transaction hash** — SHA256 of the transaction fields (excluding signature). Used for signing and as a unique identifier.
- **Merkle root** — all transaction hashes in a block are combined pairwise until a single root hash remains. Any change to any transaction changes the merkle root.
- **Previous block link** — each `BlockHeader` contains the hash of the previous block. Tampering with any block breaks all subsequent links.

---

## Validation Rules

Handled by `Validator` in `src/core/validator.py`:

- **Transaction validation** — checks signature, sufficient balance, correct nonce (replay prevention)
- **Block validation** — checks `prev_hash` matches previous block, PoW target met
- **Chain validation** — validates every block link from genesis to latest
- **Chain selection** — when two nodes have different chains, the longest valid chain wins (simplified Nakamoto consensus)

---

## Wallets and Identities

Handled by `src/wallet.py` and `src/crypto/keys.py`:

- **Private key** — random 256-bit number generated using SECP256K1 curve (same as Bitcoin)
- **Public key** — mathematically derived from the private key, cannot be reversed
- **Address** — SHA256 then RIPEMD160 of the public key, prefixed with `ARC` (e.g. `ARC3f2a9bc...`)

---

## Transaction Signatures

- **Client side** — the wallet hashes the transaction fields then signs the hash with the private key using ECDSA
- **Node side** — on receiving a transaction, the node verifies the signature using the sender's public key
- **Replay prevention** — each transaction includes a `nonce` (counter of transactions sent by that address). The node rejects any transaction whose nonce doesn't match the expected value in `State`

---

## P2P Network

Handled by `src/p2p/`:

- **Peer discovery** — `Peers.discover(url)` asks a known node for its peer list and adds them
- **Transaction broadcast** — when a node receives a valid transaction it forwards it to all its peers
- **Block broadcast** — when a node mines or receives a valid block it forwards it to all its peers
- **Anti-loop** — `Broadcast` keeps a `seen_ids` set. Any message already seen is ignored and not re-propagated

---

## Consensus

Simplified **Proof of Work (PoW)**:

- The miner increments the `nonce` in the `BlockHeader` until the SHA256 hash starts with `difficulty` leading zeros
- Difficulty is a fixed integer (e.g. `2` → hash must start with `"00"`)
- Verification is instant — any node can hash once and confirm
- Fork resolution uses the longest valid chain rule (`Validator.select_chain`)

---

## Smart Contracts

Handled by `src/contracts/`:

- **ContractState** — key-value store per contract address
- **ContractEngine** — deploys contracts and routes calls to the right execution function
- **Execution** — deterministic functions with no side effects outside of `ContractState`:
  - `counter` — increment and read a counter
  - `escrow` — deposit, release to recipient, or refund to sender
  - `transfer` — transfer ownership of an asset between addresses

---

## Demonstration

## Demonstration

Run `demo.py` at the root of the project. It automates the full flow:
```bash
python demo.py
```

This script:
1. Registers all 3 nodes as peers of each other
2. Creates two wallets — Alice and Bob
3. Seeds Alice with 100 ARC on all nodes
4. Creates a signed transaction from Alice to Bob for 10 ARC
5. Submits it to node 1

Then mine the transaction into a block on node 1:
```bash
# PowerShell
Invoke-RestMethod -Method POST -Uri "http://127.0.0.1:5001/mine"

# bash/curl
curl -X POST http://127.0.0.1:5001/mine
```

Then verify all 3 nodes are in sync:
```bash
# PowerShell
Invoke-RestMethod -Method GET -Uri "http://127.0.0.1:5001/chain"
Invoke-RestMethod -Method GET -Uri "http://127.0.0.1:5002/chain"
Invoke-RestMethod -Method GET -Uri "http://127.0.0.1:5003/chain"
```

All 3 nodes should show `length: 1` with the same block.