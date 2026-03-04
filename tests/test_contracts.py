import pytest
from src.contracts.engine import ContractEngine
from src.contracts.execution import run_counter, run_escrow, run_transfer
from src.contracts.state import ContractState


def test_counter_increment():
    engine = ContractEngine()
    engine.deploy("ARC001", "counter")
    result = engine.call("ARC001", "increment", {}, "ARCcaller")
    assert result == 1


def test_counter_get_count():
    engine = ContractEngine()
    engine.deploy("ARC001", "counter")
    engine.call("ARC001", "increment", {}, "ARCcaller")
    engine.call("ARC001", "increment", {}, "ARCcaller")
    result = engine.call("ARC001", "get_count", {}, "ARCcaller")
    assert result == 2


def test_escrow_deposit_and_release():
    engine = ContractEngine()
    engine.deploy("ARC002", "escrow")
    engine.call("ARC002", "deposit", {"amount": 100}, "ARCsender")
    result = engine.call("ARC002", "release", {"recipient": "ARCrecipient"}, "ARCsender")
    assert result is True


def test_escrow_refund():
    engine = ContractEngine()
    engine.deploy("ARC002", "escrow")
    engine.call("ARC002", "deposit", {"amount": 100}, "ARCsender")
    result = engine.call("ARC002", "refund", {}, "ARCsender")
    assert result is True


def test_deploy_twice_fails():
    engine = ContractEngine()
    engine.deploy("ARC003", "counter")
    result = engine.deploy("ARC003", "counter")
    assert result is False

def test_counter_unknown_function():
    state = ContractState()
    with pytest.raises(ValueError):
        run_counter("unknown", {}, "ARCcaller", state, "ARC001")


def test_escrow_release_not_locked():
    state = ContractState()
    result = run_escrow("release", {"recipient": "ARCbob"}, "ARCsender", state, "ARC002")
    assert result is False


def test_escrow_release_wrong_caller():
    state = ContractState()
    run_escrow("deposit", {"amount": 100}, "ARCsender", state, "ARC002")
    result = run_escrow("release", {"recipient": "ARCbob"}, "ARCwrong", state, "ARC002")
    assert result is False


def test_escrow_refund_wrong_caller():
    state = ContractState()
    run_escrow("deposit", {"amount": 100}, "ARCsender", state, "ARC002")
    result = run_escrow("refund", {}, "ARCwrong", state, "ARC002")
    assert result is False


def test_escrow_unknown_function():
    state = ContractState()
    with pytest.raises(ValueError):
        run_escrow("unknown", {}, "ARCcaller", state, "ARC002")


def test_transfer_wrong_owner():
    state = ContractState()
    state.set("ARC003", "owner", "ARCowner")
    result = run_transfer("transfer", {"recipient": "ARCbob"}, "ARCwrong", state, "ARC003")
    assert result is False


def test_transfer_success():
    state = ContractState()
    state.set("ARC003", "owner", "ARCowner")
    result = run_transfer("transfer", {"recipient": "ARCbob"}, "ARCowner", state, "ARC003")
    assert result is True


def test_transfer_unknown_function():
    state = ContractState()
    with pytest.raises(ValueError):
        run_transfer("unknown", {}, "ARCcaller", state, "ARC003")

def test_call_nonexistent_contract():
    engine = ContractEngine()
    with pytest.raises(ValueError):
        engine.call("ARC999", "increment", {}, "ARCcaller")


def test_call_unknown_contract_type():
    engine = ContractEngine()
    engine.contracts["ARC999"] = "unknown_type"
    with pytest.raises(ValueError):
        engine.call("ARC999", "increment", {}, "ARCcaller")


def test_call_transfer_contract():
    engine = ContractEngine()
    engine.deploy("ARC004", "transfer")
    engine.state.set("ARC004", "owner", "ARCowner")
    result = engine.call("ARC004", "transfer", {"recipient": "ARCbob"}, "ARCowner")
    assert result is True


def test_get_state():
    engine = ContractEngine()
    engine.deploy("ARC005", "counter")
    engine.call("ARC005", "increment", {}, "ARCcaller")
    state = engine.get_state("ARC005")
    assert state["count"] == 1