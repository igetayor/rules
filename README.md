# Ige Lightweight JSON Rule Engine

A fast, declarative business rule evaluator implemented in Python with Pydantic. Enables dynamic evaluation of nested JSON payloads against configurable rule predicates (equality, thresholds, regular expressions, set inclusion) with Boolean AND/OR composition logic.

## Supported Operators
- `eq`, `neq`: Exact equality comparison.
- `gt`, `gte`, `lt`, `lte`: Numeric & date threshold boundaries.
- `contains`: Substring or list membership.
- `regex`: Regular expression pattern matching.
- `in`: Membership checks within an enumerated set.

## Quick Start
```bash
# Run demo
python main.py

# Run test suite
pytest test_engine.py -v
```
