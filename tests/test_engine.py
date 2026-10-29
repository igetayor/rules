"""
Unit tests for the JSON Rule Engine core.
Runs with standard unittest or pytest:
    py -3 -m unittest discover tests
"""

import unittest
from backend.core.engine import JsonRuleEngine, Rule, Condition, Operator


class TestJsonRuleEngine(unittest.TestCase):
    def test_single_condition_equality(self):
        rule = Rule(
            id="R1",
            description="Check status",
            conditions=[Condition(field="status", operator=Operator.EQUALS, value="ACTIVE")],
            action="ALLOW"
        )
        engine = JsonRuleEngine([rule])
        res = engine.evaluate({"status": "ACTIVE"})
        self.assertTrue(res["results"][0]["matched"])
        self.assertEqual(res["results"][0]["action"], "ALLOW")

        res_fail = engine.evaluate({"status": "PENDING"})
        self.assertFalse(res_fail["results"][0]["matched"])

    def test_nested_field_and_operators(self):
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

        match_res = engine.evaluate({"user": {"age": 25, "email": "employee@acme.com"}})
        self.assertTrue(match_res["results"][0]["matched"])

        fail_res = engine.evaluate({"user": {"age": 16, "email": "intern@acme.com"}})
        self.assertFalse(fail_res["results"][0]["matched"])

    def test_or_matching_logic(self):
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

        res_admin = engine.evaluate({"role": "ADMIN", "override": False})
        self.assertTrue(res_admin["results"][0]["matched"])

        res_override = engine.evaluate({"role": "USER", "override": True})
        self.assertTrue(res_override["results"][0]["matched"])

        res_neither = engine.evaluate({"role": "GUEST", "override": False})
        self.assertFalse(res_neither["results"][0]["matched"])


if __name__ == "__main__":
    unittest.main()
