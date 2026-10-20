import re
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class Operator(str, Enum):
    EQUALS = "eq"
    NOT_EQUALS = "neq"
    GREATER_THAN = "gt"
    GREATER_THAN_OR_EQUAL = "gte"
    LESS_THAN = "lt"
    LESS_THAN_OR_EQUAL = "lte"
    CONTAINS = "contains"
    REGEX = "regex"
    IN = "in"

class Condition(BaseModel):
    field: str
    operator: Operator
    value: Any

class Rule(BaseModel):
    id: str
    description: str
    conditions: List[Condition]
    match_all: bool = True  # True = AND logic; False = OR logic
    action: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class RuleEvaluationResult(BaseModel):
    rule_id: str
    matched: bool
    action: Optional[str] = None
    reason: str

class JsonRuleEngine:
    """
    Lightweight, declarative JSON rule evaluation engine.
    Parses JSON rule definitions with Pydantic and evaluates nested payload dicts.
    """
    def __init__(self, rules: List[Rule]):
        self.rules = rules

    @staticmethod
    def _get_nested_field(data: Dict[str, Any], path: str) -> Any:
        keys = path.split(".")
        val = data
        for k in keys:
            if isinstance(val, dict) and k in val:
                val = val[k]
            else:
                return None
        return val

    @classmethod
    def evaluate_condition(cls, condition: Condition, data: Dict[str, Any]) -> bool:
        field_val = cls._get_nested_field(data, condition.field)
        target_val = condition.value
        op = condition.operator

        if field_val is None:
            return False

        if op == Operator.EQUALS:
            return field_val == target_val
        elif op == Operator.NOT_EQUALS:
            return field_val != target_val
        elif op == Operator.GREATER_THAN:
            return field_val > target_val
        elif op == Operator.GREATER_THAN_OR_EQUAL:
            return field_val >= target_val
        elif op == Operator.LESS_THAN:
            return field_val < target_val
        elif op == Operator.LESS_THAN_OR_EQUAL:
            return field_val <= target_val
        elif op == Operator.CONTAINS:
            return target_val in field_val
        elif op == Operator.REGEX:
            return bool(re.search(str(target_val), str(field_val)))
        elif op == Operator.IN:
            return field_val in target_val
        return False

    def evaluate(self, payload: Dict[str, Any]) -> List[RuleEvaluationResult]:
        results = []
        for rule in self.rules:
            cond_matches = [self.evaluate_condition(c, payload) for c in rule.conditions]
            matched = all(cond_matches) if rule.match_all else any(cond_matches)
            results.append(RuleEvaluationResult(
                rule_id=rule.id,
                matched=matched,
                action=rule.action if matched else None,
                reason=f"Matched all {len(rule.conditions)} conditions" if matched else "Conditions not met"
            ))
        return results
