import json
from engine import JsonRuleEngine, Rule

sample_rules_json = [
    {
        "id": "RULE_FRAUD_HIGH_VALUE_FOREIGN",
        "description": "Flag transaction over $5,000 originating outside US/UK",
        "match_all": True,
        "conditions": [
            {"field": "transaction.amount", "operator": "gte", "value": 5000},
            {"field": "transaction.country", "operator": "in", "value": ["NG", "RO", "RU", "KY"]}
        ],
        "action": "TRIGGER_MANUAL_KYC_REVIEW"
    },
    {
        "id": "RULE_VIP_TIER_FEE_WAIVER",
        "description": "Waive platform fees for enterprise customers",
        "match_all": False,
        "conditions": [
            {"field": "customer.tier", "operator": "eq", "value": "ENTERPRISE"},
            {"field": "customer.monthly_spend", "operator": "gt", "value": 50000}
        ],
        "action": "APPLY_ZERO_FEE_OVERRIDE"
    }
]

def main():
    print("=" * 60)
    print("📋 Ige Lightweight JSON Rule Evaluation Engine")
    print("=" * 60)

    rules = [Rule(**r) for r in sample_rules_json]
    engine = JsonRuleEngine(rules)

    sample_transaction = {
        "transaction": {
            "id": "tx_99182",
            "amount": 7500.0,
            "country": "NG",
            "currency": "USD"
        },
        "customer": {
            "id": "cust_123",
            "tier": "STANDARD",
            "monthly_spend": 1200
        }
    }

    print("\n[1] Evaluating Incoming Payload against Declarative Rules:")
    print(json.dumps(sample_transaction, indent=2))

    evaluations = engine.evaluate(sample_transaction)

    print("\n[2] Evaluation Results:")
    for ev in evaluations:
        status = "MATCHED (ACTION TRIGGERED)" if ev.matched else "NOT MATCHED"
        print(f" Rule:   {ev.rule_id}")
        print(f" Status: {status}")
        if ev.matched:
            print(f" Action: {ev.action}")
        print(f" Reason: {ev.reason}\n")

if __name__ == "__main__":
    main()
