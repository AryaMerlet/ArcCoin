from src.contracts.engine import ContractEngine


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