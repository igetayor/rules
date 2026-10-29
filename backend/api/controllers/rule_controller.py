"""
RuleController — HTTP controller for JSON Rule Engine REST endpoints.

Handles request parsing, input validation, delegates to RuleService,
and formats HTTP responses. Follows single-responsibility: no business logic here.
"""

import json
from urllib.parse import urlparse
from http.server import BaseHTTPRequestHandler

from backend.api.services.rule_service import RuleService
from backend.core.engine import Rule


class RuleController:
    """
    Stateless controller that maps HTTP verbs + paths to service calls.
    Injected with a RuleService instance via the handler factory.
    """

    def __init__(self, service: RuleService):
        self._service = service

    # ------------------------------------------------------------------ #
    #  GET  /api/rules                                                     #
    # ------------------------------------------------------------------ #
    def list_rules(self) -> tuple[int, dict]:
        """Return the full catalog of registered rules."""
        rules = self._service.list_rules()
        return 200, [r.model_dump() for r in rules]

    # ------------------------------------------------------------------ #
    #  POST /api/rules                                                     #
    # ------------------------------------------------------------------ #
    def create_rule(self, body: dict) -> tuple[int, dict]:
        """Validate and register a new rule from the request body."""
        try:
            new_rule = Rule(**body)
            self._service.add_rule(new_rule)
            return 201, {"success": True, "rule": new_rule.model_dump()}
        except Exception as exc:
            return 400, {"error": f"Invalid rule schema: {exc}"}

    # ------------------------------------------------------------------ #
    #  POST /api/evaluate                                                  #
    # ------------------------------------------------------------------ #
    def evaluate(self, body: dict) -> tuple[int, dict]:
        """Evaluate an arbitrary JSON payload against all registered rules."""
        data = body.get("data", body)
        result = self._service.evaluate(data)
        return 200, result
