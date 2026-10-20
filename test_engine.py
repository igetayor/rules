import pytest
from engine import JsonRuleEngine, Rule, Condition, Operator

def test_single_condition_equality():
    rule = Rule(
        id="R1",
        description="Check status",
        conditions=[Condition(field="status", operator=Operator.EQUALS, value="ACTIVE")],
        action="ALLOW"
    )
    engine = JsonRuleEngine([rule])
    res = engine.evaluate({"status": "ACTIVE"})
    assert res[0].matched is True
    assert res[0].action == "ALLOW"

    res_fail = engine.evaluate({"status": "PENDING"})
    assert res_fail[0].matched is False

def test_nested_field_and_operators():
    rule = Rule(
        id="R2",
        description="Nested threshold and regex",
        conditions=[
            Condition(field="user.age", operator=Operator.GREATER_THAN_OR_EQUAL, value=18),
            Condition(field="user.email", operator=Operator.REGEX, value=r"@acme\.com$")
        ],
        match_all=True,
        action="APPROVE_CORP_ACCOUNT"
    )
    engine = JsonRuleEngine([rule])

    # Passing payload
    match_res = engine.evaluate({"user": {"age": 25, "email": "employee@acme.com"}})
    assert match_res[0].matched is True

    # Underage fail
    fail_res = engine.evaluate({"user": {"age": 16, "email": "intern@acme.com"}})
    assert fail_res[0].matched is False

def test_or_matching_logic():
    rule = Rule(
        id="R3",
        description="OR logic rule",
        conditions=[
            Condition(field="role", operator=Operator.EQUALS, value="ADMIN"),
            Condition(field="override", operator=Operator.EQUALS, value=True)
        ],
        match_all=False,
        action="GRANT_ACCESS"
    )
    engine = JsonRuleEngine([rule])
    assert engine.evaluate({"role": "GUEST", "override": True})[0].matched is True
    assert engine.evaluate({"role": "GUEST", "override": False})[0].matched is False
