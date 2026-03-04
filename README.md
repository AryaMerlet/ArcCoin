# ArcCoin

A minimal functional blockchain implementation in Python, built for educational purposes.
Ticker: ARC

## Project Structure
```
src/
├── crypto/         # hash, keys, signatures
├── core/           # transaction, block, chain, state, mempool, validator
├── contracts/      # engine, state, execution
└── p2p/            # node, peers, broadcast, sync
tests/              # all unit tests
```

## Project Structure

![Blockchain Key Management-2026-03-04-082800.png](../../Documents/COURS/BLOCKCHAIN%26SMART_CONTRACT/Blockchain%20Key%20Management-2026-03-04-082800.png)

## Setup
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run a node
```bash
python -m src.p2p.node
```

## Run tests
```bash
pytest -v
```

## Dependencies

- flask
- cryptography
- pytest
- requests