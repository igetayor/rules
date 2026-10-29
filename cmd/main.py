"""
Entrypoint for the JSON Rule Engine.

Usage:
  python -m cmd.main              # Run CLI demo
  python -m cmd.main --serve      # Launch web server on port 8093
  python -m cmd.main --serve -p 9000
"""

import sys
import argparse
import asyncio

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def run_cli_demo():
    from backend.core.engine import JsonRuleEngine, Rule, Condition, Operator

    print("=" * 65)
    print("[*] Ige JSON Rule Engine -- Declarative Policy Evaluation")
    print("=" * 65)

    rules = [
        Rule(
            id="RULE_001_HIGH_RISK_AML",
            description="Flag high-value international transfers from high-risk users",
            priority=1,
            match_all=True,
            conditions=[
                Condition(field="transaction.amount", operator=Operator.GREATER_THAN, value=5000),
                Condition(field="user.risk_level", operator=Operator.IN, value=["HIGH", "CRITICAL"]),
                Condition(field="recipient.country", operator=Operator.NOT_EQUALS, value="US"),
            ],
            action="HOLD_AND_ALERT_COMPLIANCE"
        ),
        Rule(
            id="RULE_002_AUTO_VIP_UPGRADE",
            description="Upgrade institutional users with 30-day volume >= 500k",
            priority=2,
            match_all=True,
            conditions=[
                Condition(field="account.thirty_day_volume", operator=Operator.GREATER_THAN_OR_EQUAL, value=500000),
                Condition(field="account.kyc_tier", operator=Operator.EQUALS, value="TIER_3"),
            ],
            action="PROMOTE_TO_PRIME_BROKERAGE"
        )
    ]

    engine = JsonRuleEngine(rules=rules)

    payload_a = {
        "transaction": {"amount": 12500, "currency": "EUR"},
        "user": {"risk_level": "HIGH", "name": "Global Traders Ltd"},
        "recipient": {"country": "DE"}
    }

    print("\n[1] Evaluating Payload A (High-Risk Wire):")
    res_a = engine.evaluate(payload_a)
    print(f"   Execution Time: {res_a['evaluation_time_us']} us")
    print(f"   Rules Triggered: {res_a['rules_triggered_count']} / {res_a['rules_evaluated_count']}")
    for r in res_a["results"]:
        status = "[TRIGGERED]" if r["matched"] else "[PASSED OVER]"
        print(f"    - {status} {r['rule_id']} -> Action: {r['action']}")
        print(f"      Explanation: {r['explanation']}")

    payload_b = {
        "account": {"thirty_day_volume": 850000, "kyc_tier": "TIER_3"},
        "transaction": {"amount": 500}
    }

    print("\n[2] Evaluating Payload B (Institutional Volume Upgrade):")
    res_b = engine.evaluate(payload_b)
    print(f"   Execution Time: {res_b['evaluation_time_us']} us")
    print(f"   Rules Triggered: {res_b['rules_triggered_count']} / {res_b['rules_evaluated_count']}")
    for r in res_b["results"]:
        status = "[TRIGGERED]" if r["matched"] else "[PASSED OVER]"
        print(f"    - {status} {r['rule_id']} -> Action: {r['action']}")
        print(f"      Explanation: {r['explanation']}")

    print("\n[+] JSON Rule Engine demonstrated sub-millisecond evaluation with full audit trails.")
    print("    To launch the interactive visualizer, run: python -m cmd.main --serve")


def main():
    parser = argparse.ArgumentParser(description="Ige JSON Rule Engine")
    parser.add_argument("--serve", "-s", action="store_true", help="Launch interactive web server on port 8093")
    parser.add_argument("--port", "-p", type=int, default=8093, help="Port to listen on")
    args = parser.parse_args()

    if args.serve:
        from backend.api.server import start_server
        start_server(args.port)
    else:
        run_cli_demo()


if __name__ == "__main__":
    main()
