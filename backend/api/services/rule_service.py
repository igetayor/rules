"""
RuleService — application service layer for the JSON Rule Engine.

Encapsulates all business logic: rule lifecycle management and payload evaluation.
Controllers and CLI runners depend on this layer; the engine core is hidden behind it.
"""

from typing import List, Dict, Any

from backend.core.engine import JsonRuleEngine, Rule


class RuleService:
    """
    Manages the engine's rule catalog and exposes evaluation capabilities.
    This is the single entry point for business operations — keeps
    controllers and CLI runners decoupled from engine internals.
    """

    def __init__(self, initial_rules: List[Rule] | None = None):
        self._engine = JsonRuleEngine(rules=initial_rules or [])

    # ------------------------------------------------------------------ #
    #  Rule Catalog                                                        #
    # ------------------------------------------------------------------ #
    def list_rules(self) -> List[Rule]:
        return list(self._engine.rules)

    def add_rule(self, rule: Rule) -> None:
        self._engine.add_rule(rule)

    def remove_rule(self, rule_id: str) -> bool:
        before = len(self._engine.rules)
        self._engine.rules = [r for r in self._engine.rules if r.id != rule_id]
        return len(self._engine.rules) < before

    # ------------------------------------------------------------------ #
    #  Evaluation                                                          #
    # ------------------------------------------------------------------ #
    def evaluate(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Delegate evaluation to the engine core and return a fully
        structured audit result (matches, timings, condition traces).
        """
        return self._engine.evaluate(payload)
