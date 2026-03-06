from src.core.block import Block
from src.core.chain import Chain
from src.core.state import State
from src.core.transaction import Transaction
from src.crypto.signatures import verify
from src.core.miner import Miner


class Validator:

    @staticmethod
    def validate_transaction(tx: Transaction, state: State) -> bool:
        if tx.signature is None:
            print("DEBUG: no signature")
            return False
        if not verify(tx.sender_public_key, tx.hash(), tx.signature):
            print("DEBUG: invalid signature")

            return False
        if state.get_balance(tx.sender) < tx.amount:
            print(f"DEBUG: insufficient balance: {state.get_balance(tx.sender)}")

            return False
        if state.get_nonce(tx.sender) != tx.nonce:
            print(f"DEBUG: wrong nonce: expected {state.get_nonce(tx.sender)}, got {tx.nonce}")

            return False
        return True

    @staticmethod
    def validate_block(block: Block, prev_block: Block) -> bool:
        if prev_block is None:
            return True
        if block.header.prev_hash != prev_block.header.hash():
            return False
        target = "0" * block.header.difficulty
        if not block.header.hash().startswith(target):
            return False
        return True

    @staticmethod
    def validate_chain(chain: Chain) -> bool:
        for i in range(1, chain.length()):
            current = chain.blocks[i]
            previous = chain.blocks[i - 1]
            if not Validator.validate_block(current, previous):
                return False
        return True

    #fork validation rule
    @staticmethod
    def select_chain(local: Chain, remote: Chain) -> Chain:
        if Validator.validate_chain(remote) and remote.length() > local.length():
            return remote
        return local